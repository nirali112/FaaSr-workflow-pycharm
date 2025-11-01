# init_components_faasr.py
import json
import os

def init_components_faasr():
    """
    Initialize all PyChamp components and save state to cloud storage.
    This is the FaaSr version - NO parameters, uses FaaSr functions.
    """
    print("[init_components_faasr] Starting initialization...")
    
    # Create initial state with all component data
    state = {
        "aquifer": {
            "unique_id": "aq1",
            "aq_a": 0.1,
            "aq_b": 10.0,
            "area": 100.0,
            "sy": 0.2,
            "init": {
                "st": 30.0,
                "dwl": 0.0
            }
        },
        "field": {
            "unique_id": "f1",
            "crop": "corn",
            "field_area": 50.0,
            "soil_moisture": 0.5,
            "tech_pumping_rate_coefs": [0.8, 1.2],
            "water_yield_curves": {
                "corn": [[0.0, 0.0, 0.0], [100.0, 1.0, 0.8]],
                "wheat": [[0.0, 0.0, 0.0], [90.0, 0.9, 0.75]],
                "soybean": [[0.0, 0.0, 0.0], [80.0, 0.85, 0.7]]
            },
            "prec_aw_id": "default",
            "irrigation_policy": "fixed",
            "irrigation_application": 30.0,
            "irrigation_status": True,
            "irrigation_system": "center_pivot",
            "tech_index": 0,
            "aw_dp": 0.1,
            "aw_runoff": 0.05,
            "init": {
                "yield": 0.0,
                "revenue": 0.0,
                "profit": 0.0,
                "irr_alloc": 0.0,
                "irr_used": 0.0,
                "tech": 0
            }
        },
        "well": {
            "unique_id": "w1",
            "efficiency": 0.75,
            "max_capacity": 100.0,
            "pumping_cost_per_m3": 0.05
        },
        "finance": {
            "unique_id": "fin1",
            "crop_price": 4.0,
            "cost": 1.5,
            "net_profit": 0.0,
            "total_costs": 0.0,
            "profit_margin": 0.0,
            "water_productivity": 0.0
        },
        "behavior": {
            "unique_id": "b1",
            "satisfaction_threshold": 0.7,
            "uncertainty_threshold": 0.3,
            "satisfaction": 0.7,
            "uncertainty": 0.3,
            "optimal_irrigation": 0.0,
            "last_profit": 0.0,
            "last_soil_moisture": 0.5,
            "last_storage": 30.0
        },
        "decision": {},
        "pumping_cost": 0.0,
        "results": {}
    }
    
    # Save state to local file
    with open("pychamp_state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    print("[init_components_faasr] State created successfully")
    print(f"  - Aquifer storage: {state['aquifer']['init']['st']} m³")
    print(f"  - Field crop: {state['field']['crop']}")
    print(f"  - Soil moisture: {state['field']['soil_moisture']}")
    
    # Upload state to cloud storage
    faasr_put_file(
        server_name="My_S3_Bucket",
        local_folder="",
        local_file="pychamp_state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )
    
    print("[init_components_faasr] State uploaded to cloud storage")
    print("[init_components_faasr] Initialization complete!")