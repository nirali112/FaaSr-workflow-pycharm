"""
FaaSr Step 1: Initialize PyChAMP Components
This script initializes Aquifer, Well, Finance, and Field components
and saves the state for the next workflow step.
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
    print("✅ Dependencies installed")

def init_components_faasr():
    """Initialize PyChAMP components - FaaSr entry point"""
    
    # Read FaaSr input (if exists from previous workflow)
    try:
        with open("faasr_data.json", "r") as f:
            faasr_data = json.load(f)
    except FileNotFoundError:
        faasr_data = {}  # First run, no previous data
    
    install_dependencies()
    
    # Import after installation
    from mesa import Model
    from mesa.time import RandomActivation
    from py_champ.components.aquifer import Aquifer
    from py_champ.components.well import Well
    from py_champ.components.finance import Finance
    from py_champ.components.field import Field
    
    print("\n" + "=" * 60)
    print("Initializing PyChAMP Components in FaaSr")
    print("=" * 60)
    
    # 1. Create Mesa model
    print("\n1. Creating model...")
    model = Model()
    model.schedule = RandomActivation(model)
    model.current_step = 0
    model.crop_options = ["corn", "soy", "wheat"]
    model.area_split = 4
    print(f"   ✅ Model created")
    
    # 2. Initialize Aquifer
    print("\n2. Initializing Aquifer...")
    aquifer_settings = {
        "aq_a": 0.1,
        "aq_b": 10.0,
        "area": 100.0,
        "sy": 0.2,
        "init": {"st": 30.0, "dwl": 0.0}
    }
    aquifer = Aquifer("aq1", model, aquifer_settings)
    model.schedule.add(aquifer)
    print(f"   ✅ Aquifer initialized: st={aquifer.st}m")
    
    # 3. Initialize Well
    print("\n3. Initializing Well...")
    well_settings = {
        "r": 0.2032,
        "k": 15.0,
        "sy": 0.2,
        "rho": 1000.0,
        "g": 9.81,
        "eff_pump": 0.75,
        "eff_well": 0.85,
        "aquifer_id": "aq1",
        "pumping_capacity": 100.0,
        "init": {
            "st": 30.0,
            "l_wt": 5.0,
            "pumping_days": 90
        }
    }
    well = Well("w1", model, well_settings)
    model.schedule.add(well)
    print(f"   ✅ Well initialized: connected to {well.aquifer_id}")
    
    # 4. Initialize Finance
    print("\n4. Initializing Finance...")
    finance_settings = {
        "energy_price": 0.12,
        "crop_price": {
            "corn": 5.0,
            "soy": 10.0,
            "wheat": 3.0
        },
        "crop_cost": {
            "corn": 400.0,
            "soy": 300.0,
            "wheat": 250.0
        },
        "irr_tech_operational_cost": {
            "gravity": 50.0,
            "sprinkler": 100.0,
            "drip": 150.0
        },
        "irr_tech_change_cost": {
            "gravity": 1000.0,
            "sprinkler": 2000.0,
            "drip": 3000.0
        },
        "crop_change_cost": 200.0,
        "init": {"savings": 10000.0}
    }
    finance = Finance("fin1", model, finance_settings)
    model.schedule.add(finance)
    print(f"   ✅ Finance initialized: energy_price=${finance.energy_price}/kWh")
    
    # 5. Initialize Field
    print("\n5. Initializing Field...")
    field_settings = {
        "field_area": 100.0,
        "water_yield_curves": {
            "corn": [10.0, 600.0, 0.5, 1.0, 0.3, 0.2],
            "soy": [4.0, 400.0, 0.6, 1.2, 0.25, 0.15],
            "wheat": [5.0, 350.0, 0.55, 1.1, 0.28, 0.18]
        },
        "tech_pumping_rate_coefs": {
            "gravity": [1.0, 0.5, 10.0],
            "sprinkler": [0.85, 0.6, 15.0],
            "drip": [0.70, 0.7, 20.0]
        },
        "prec_aw_id": "aq1",
        "init": {
            "crop": "corn",
            "tech": "sprinkler",
            "field_type": "irrigated"
        }
    }
    field = Field("f1", model, field_settings)
    model.schedule.add(field)
    print(f"   ✅ Field initialized: area={field.field_area}ha, crop={field.crops[0]}")
    
    # 6. Create state for next workflow step
    print("\n6. Creating state...")
    state = {
        "workflow_step": "init_components",
        "status": "completed",
        "model_step": model.current_step,
        "components": {
            "aquifer": {
                "id": aquifer.unique_id,
                "st": aquifer.st,
                "dwl": aquifer.dwl,
                "area": aquifer.area
            },
            "well": {
                "id": well.unique_id,
                "aquifer_id": well.aquifer_id,
                "pumping_capacity": well.pumping_capacity,
                "eff_pump": well.eff_pump,
                "st": well.st,
                "pumping_days": well.pumping_days
            },
            "finance": {
                "id": finance.unique_id,
                "energy_price": finance.energy_price,
                "crop_price": finance.crop_price,
                "crop_cost": finance.crop_cost
            },
            "field": {
                "id": field.unique_id,
                "field_area": field.field_area,
                "crops": field.crops,
                "tech": field.te
            }
        },
        "settings": {
            "aquifer": aquifer_settings,
            "well": well_settings,
            "finance": finance_settings,
            "field": field_settings
        }
    }
    
    print("\n" + "=" * 60)
    print("✅ ALL COMPONENTS INITIALIZED SUCCESSFULLY")
    print("=" * 60)
    print(f"Components: {list(state['components'].keys())}")
    
    # Save state for next FaaSr action
    faasr_data["state"] = state
    
    # Write output for next step
    with open("faasr_output.json", "w") as f:
        json.dump(faasr_data, f, indent=2)
    
    print("\n✅ State saved to faasr_output.json")
    
    # Return simple success message for FaaSr
    return "SUCCESS"

# FaaSr entry point
if __name__ == "__main__":
    try:
        result = init_components_faasr()
        print(f"\n✅ FaaSr step completed: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise