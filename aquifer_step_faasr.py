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

def aquifer_step_faasr():    
    # Read state from previous step
    try:
        with open("faasr_data.json", "r") as f:
            faasr_data = json.load(f)
    except FileNotFoundError:
        print("No faasr_data.json found - need to run init_components first")
        sys.exit(1)
    
    install_dependencies()
    
    # Import after installation
    from mesa import Model
    from mesa.time import RandomActivation
    from py_champ.components.aquifer import Aquifer

    
    # Get state
    state = faasr_data.get("state", {})
    if not state:
        print("No state found in faasr_data")
        sys.exit(1)
    
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
    
    with open("faasr_output.json", "w") as f:
        json.dump(faasr_data, f, indent=2)
    
    print("State saved to faasr_output.json")

if __name__ == "__main__":
    aquifer_step_faasr()
