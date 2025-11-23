"""
FaaSr Step: Field Simulation
Simulates crop growth and irrigation water use
"""

import sys
import json
import subprocess
import numpy as np

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

def field_step_faasr(output1="payload"):
    """Simulate field crop growth"""
    
    # Download state from S3
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
        print(f"❌ Could not download payload: {e}")
        return
    
    install_dependencies()
    
    # Import after installation
    from mesa import Model
    from mesa.time import RandomActivation
    from py_champ.components.field import Field
    
    print("\n" + "=" * 60)
    print("Simulating Field Step")
    print("=" * 60)
    
    # Get state
    state = faasr_data.get("state", {})
    if not state or "settings" not in state:
        print(" No valid state found")
        return
    
    print(f"Previous step: {state.get('workflow_step')}")
    
    # Recreate model and field
    model = Model()
    model.schedule = RandomActivation(model)
    model.current_step = state.get("model_step", 0)
    model.crop_options = ["corn", "soy", "wheat"]
    model.area_split = 4
    
    # Get field settings and recreate
    field_settings = state["settings"]["field"]
    field = Field("f1", model, field_settings, 
                  truncated_normal_pars={
                      "corn": [0.5, 0.1, 0, 1],
                      "soy": [0.5, 0.1, 0, 1],
                      "wheat": [0.5, 0.1, 0, 1]
                  })
    model.schedule.add(field)
    
    print(f"\nField state before step:")
    print(f"  Area: {field.field_area} ha")
    print(f"  Current crops: {field.crops}")
    print(f"  Current tech: {field.te}")
    
    # Simulation inputs (simplified)
    # In real scenario, these would come from optimization/decision making
    n_s = model.area_split
    n_c = len(model.crop_options)
    
    # Irrigation depth: 10 cm for all fields/crops
    irr_depth = np.ones((n_s, n_c, 1)) * 10.0  # cm
    
    # Crop indicators: all growing corn (first crop)
    i_crop = np.zeros((n_s, n_c, 1))
    i_crop[:, 0, 0] = 1  # First crop (corn) for all sections
    
    # Technology: sprinkler
    i_te = "sprinkler"
    
    # Precipitation available water
    prec_aw = {"corn": 20.0, "soy": 18.0, "wheat": 15.0}  # cm
    
    print(f"\nSimulation inputs:")
    print(f"  Irrigation depth: {irr_depth[0,0,0]} cm")
    print(f"  Technology: {i_te}")
    print(f"  Precipitation: {prec_aw}")
    
    # Run field step
    y, avg_y_y, irr_vol = field.step(irr_depth, i_crop, i_te, prec_aw)
    
    print(f"\nField state after step:")
    print(f"  Total yield: {np.sum(y):.2f} (1e4 bu)")
    print(f"  Avg yield rate: {avg_y_y:.4f}")
    print(f"  Irrigation volume: {irr_vol:.2f} m-ha")
    print(f"  Pumping rate: {field.pumping_rate:.2f} m-ha/day")
    
    # Update state
    model.current_step += 1
    state["workflow_step"] = "field_simulation"
    state["model_step"] = model.current_step
    state["components"]["field"].update({
        "crops": field.crops,
        "tech": field.te,
        "yield": float(np.sum(y)),
        "avg_yield_rate": float(avg_y_y),
        "irrigation_volume": float(irr_vol),
        "pumping_rate": float(field.pumping_rate)
    })
    
    print("FIELD STEP COMPLETED")
    
    # Save updated state
    faasr_data["state"] = state
    
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

if __name__ == "__main__":
    field_step_faasr()