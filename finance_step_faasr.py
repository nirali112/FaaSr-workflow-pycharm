"""
FaaSr Step: Finance Calculation
Calculates costs, revenue, and profit
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

def finance_step_faasr(output1="payload"):
    """Calculate finance and profit"""
    
    # Download from S3
    try:
        faasr_get_file(
            server_name="S3",
            remote_folder="pychamp-workflow",
            remote_file=output1,
            local_folder="",
            local_file=output1
        )
        print("Downloaded payload from S3")
    except NameError:
        print("Running locally")
    except Exception as e:
        print(f"Download error: {e}")
    
    # Read file
    try:
        with open(output1, "r") as f:
            faasr_data = json.load(f)
    except FileNotFoundError:
        print("No payload file")
        return
    
    install_dependencies()
    
    # Import after installation
    import numpy as np
    from mesa import Model
    from mesa.time import RandomActivation
    from py_champ.components.aquifer import Aquifer
    from py_champ.components.well import Well
    from py_champ.components.field import Field
    from py_champ.components.finance import Finance
    
    print("\n" + "=" * 60)
    print("Calculating Finance")
    print("=" * 60)
    
    # Get state
    state = faasr_data.get("state", {})
    if not state or "settings" not in state:
        print(" No valid state")
        return
    
    print(f"Previous step: {state.get('workflow_step')}")
    
    # Recreate model
    model = Model()
    model.schedule = RandomActivation(model)
    model.current_step = state.get("model_step", 0)
    model.crop_options = ["corn", "soy", "wheat"]
    model.area_split = 4
    
    # Recreate components with current state
    # Field
    field_settings = state["settings"]["field"]
    field = Field("f1", model, field_settings,
                  truncated_normal_pars={
                      "corn": [0.5, 0.1, 0, 1],
                      "soy": [0.5, 0.1, 0, 1],
                      "wheat": [0.5, 0.1, 0, 1]
                  })
    
    # Restore field state from simulation
    field_state = state["components"]["field"]
    field.crops = field_state.get("crops", ["corn"])
    field.te = field_state.get("tech", "sprinkler")
    field.pumping_rate = field_state.get("pumping_rate", 0)
    field.irr_vol_per_field = field_state.get("irrigation_volume", 0)
    
    # Create yield array (simplified - normally from field simulation)
    n_s = model.area_split
    n_c = len(model.crop_options)
    field.y = np.ones((n_s, n_c, 1)) * field_state.get("yield", 0) / n_s
    field.pre_te = field.te
    field.i_crop = np.zeros((n_s, n_c, 1))
    field.i_crop[:, 0, 0] = 1  # corn
    field.pre_i_crop = field.i_crop.copy()
    
    # Well
    well_settings = state["settings"]["well"]
    well_settings["init"]["st"] = state["components"]["well"]["st"]
    well = Well("w1", model, well_settings)
    
    # Simulate well energy consumption (simplified)
    well.e = field.pumping_rate * 0.001  # Convert to PJ (simplified)
    
    # Finance
    finance_settings = state["settings"]["finance"]
    finance = Finance("fin1", model, finance_settings)
    
    print(f"\nFinance inputs:")
    print(f"  Field yield: {field_state.get('yield', 0):.2f} (1e4 bu)")
    print(f"  Irrigation volume: {field.irr_vol_per_field:.2f} m-ha")
    print(f"  Well energy: {well.e:.4f} PJ")
    
    # Run finance step
    profit = finance.step(fields={"f1": field}, wells={"w1": well})
    
    print(f"\nFinance results:")
    print(f"  Revenue: ${finance.rev:.2f} (1e4$)")
    print(f"  Energy cost: ${finance.cost_e:.2f} (1e4$)")
    print(f"  Tech cost: ${finance.cost_tech:.2f} (1e4$)")
    print(f"  Profit: ${profit:.2f} (1e4$)")
    
    # Update state
    model.current_step += 1
    state["workflow_step"] = "finance_calculation"
    state["model_step"] = model.current_step
    state["components"]["finance"].update({
        "profit": float(profit),
        "revenue": float(finance.rev),
        "energy_cost": float(finance.cost_e),
        "tech_cost": float(finance.cost_tech)
    })
    
    print(" FINANCE STEP COMPLETED")
    
    # Save
    faasr_data["state"] = state
    
    with open(output1, "w") as f:
        json.dump(faasr_data, f, indent=2)
    
    try:
        faasr_put_file(
            server_name="S3",
            local_folder="",
            local_file=output1,
            remote_folder="pychamp-workflow",
            remote_file=output1
        )
        print("Updated payload uploaded to S3")
    except NameError:
        print("Running locally - saved to file")

if __name__ == "__main__":
    finance_step_faasr()