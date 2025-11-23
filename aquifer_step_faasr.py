"""
FaaSr Step: Aquifer Simulation
Simulates aquifer dynamics (groundwater depletion from pumping)
"""

import sys
import json
import subprocess

def install_dependencies():
    """Install required packages in FaaSr container"""
    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "numpy", "pandas", "mesa==2.1.1"
    ])
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "git+https://github.com/philip928lin/PyCHAMP.git"
    ])
    print("Dependencies installed")

def aquifer_step_faasr(output1="payload"):    
    # Read state from previous step    
    try:
        faasr_get_file(
            server_name="S3",
            remote_folder="pychamp-workflow",
            remote_file="payload",
            local_folder="",
            local_file="payload"
        )
        print("Downloaded payload from S3")
        
        with open("payload", "r") as f:
            faasr_data = json.load(f)
    except Exception as e:
        print(f" Could not download payload: {e}")
        faasr_data = {}

    
    install_dependencies()
    
    # Import after installation
    from mesa import Model
    from mesa.time import RandomActivation
    from py_champ.components.aquifer import Aquifer

    
    # Get state
    state = faasr_data.get("state", {})
    if not state or "settings" not in state:
            print("No valid state found - workflow needs to run init_components first")
            print("Available keys in faasr_data:", list(faasr_data.keys()))
            #  sys.exit(1)
            return
    
    print(f"Previous step: {state.get('workflow_step')}")
    
    # Recreate model and aquifer from state
    model = Model()
    model.schedule = RandomActivation(model)
    model.current_step = state.get("model_step", 0)
    
    # Get aquifer settings and recreate component
    aquifer_settings = state["settings"]["aquifer"]
    aquifer_settings["init"]["st"] = state["components"]["aquifer"]["st"]
    aquifer_settings["init"]["dwl"] = state["components"]["aquifer"]["dwl"]
    aquifer = Aquifer("aq1", model, aquifer_settings)
    model.schedule.add(aquifer)
    
    print(f"\nAquifer state before step:")
    print(f"  Saturated thickness: {aquifer.st} m")
    print(f"  Depth to water: {aquifer.dwl} m")
    
    # Simulate pumping withdrawal
    withdrawal = 5.0  # m-ha
    inflow = 2.0      # m-ha
    
    print(f"\nSimulation inputs:")
    print(f"  Withdrawal: {withdrawal} m-ha")
    print(f"  Inflow: {inflow} m-ha")
    
    # Run aquifer step
    dwl_change = aquifer.step(withdrawal=withdrawal, inflow=inflow)
    
    print(f"\nAquifer state after step:")
    print(f"  Saturated thickness: {aquifer.st} m")
    print(f"  Change in water level: {dwl_change} m")
    
    # Update state
    model.current_step += 1
    state["workflow_step"] = "aquifer_simulation"
    state["model_step"] = model.current_step
    state["components"]["aquifer"].update({
        "st": aquifer.st,
        "dwl": aquifer.dwl,
        "withdrawal": withdrawal,
        "inflow": inflow,
        "dwl_change": dwl_change
    })
    print("AQUIFER STEP COMPLETED")
    
    # Save updated state
    faasr_data["state"] = state

    # At the end, upload updated state
    with open("payload", "w") as f:
        json.dump(faasr_data, f, indent=2)
    
    faasr_put_file(
        server_name="S3",
        local_folder="",
        local_file="payload",
        remote_folder="pychamp-workflow",
        remote_file="payload"
    )
    
    print("Updated payload uploaded to S3")
    
    # with open(output1, "w") as f:
    #     json.dump(faasr_data, f, indent=2)
    
    # print(f"State saved to {output1}")

if __name__ == "__main__":
    aquifer_step_faasr(output1="payload")
