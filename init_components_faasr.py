# functions/init_components_faasr.py
import json
import os
import sys

# Import REAL PyChAMP components
try:
    from py_champ.components.aquifer import Aquifer
    from py_champ.components.field import Field
    from py_champ.components.well import Well
    from py_champ.components.finance import Finance
    PYCHAMP_AVAILABLE = True
    print("[init_components_faasr] ✓ PyChAMP library imported successfully!")
except ImportError as e:
    PYCHAMP_AVAILABLE = False
    print(f"[init_components_faasr] ✗ PyChAMP not available: {e}")
    print("[init_components_faasr] Falling back to simplified mode")


def init_components_faasr():
    """
    Initialize simulation using REAL PyChAMP library components.
    Creates actual PyChAMP objects, then serializes to JSON for cloud storage.
    """
    print("[init_components_faasr] Starting initialization...")
    print(f"[init_components_faasr] Python version: {sys.version}")
    print(f"[init_components_faasr] Using REAL PyChAMP: {PYCHAMP_AVAILABLE}")
    
    if not PYCHAMP_AVAILABLE:
        # Fallback to simple dict if PyChAMP not installed
        print("[init_components_faasr] WARNING: Using simplified components (no PyChAMP)")
        state = create_simplified_state()
    else:
        # Use REAL PyChAMP library
        state = create_pychamp_state()
    
    # Save to local file
    output_file = "pychamp_state.json"
    with open(output_file, "w") as f:
        json.dump(state, f, indent=2)
    
    print(f"[init_components_faasr] State saved to {output_file}")
    print(f"[init_components_faasr] File size: {os.path.getsize(output_file)} bytes")
    print("[init_components_faasr] State contents:")
    print(f"  - Aquifer storage: {state['aquifer']['init']['st']} m³")
    print(f"  - Field crop: {state['field']['crop']}")
    print(f"  - Using REAL PyChAMP: {state['metadata']['using_real_pychamp']}")
    
    # Upload to cloud storage
    print("[init_components_faasr] Uploading to cloud storage...")
    
    try:
        faasr_put_file(
            server_name="S3",
            local_folder="",
            local_file=output_file,
            remote_folder="pychamp-workflow",
            remote_file="state.json"
        )
        print("[init_components_faasr] State uploaded successfully!")
    except Exception as e:
        print(f"[init_components_faasr] Upload failed: {e}")
        print(f"[init_components_faasr] Error type: {type(e)}")
        # Don't fail the whole function - we still created the state
        print("[init_components_faasr] Continuing anyway (state was created locally)")
    
    print("[init_components_faasr] Initialization complete!")


def create_pychamp_state():
    """Create state using REAL PyChAMP library"""
    print("[init_components_faasr] Creating components with REAL PyChAMP...")
    
    # Create minimal model object
    class MinimalModel:
        """Minimal model to satisfy PyChAMP component requirements"""
        def __init__(self):
            self.schedule = None
            self.running = True
            self.crop_options = ["corn", "wheat", "soybean"]
            self.area_split = [1.0]
            self.tech_options = [{"name": "center_pivot", "efficiency": 0.75}]
    
    model = MinimalModel()
    
    # 1. Create Aquifer
    aquifer_settings = {
        "aq_a": 0.1,
        "aq_b": 10.0,
        "area": 100.0,
        "sy": 0.2,
        "init": {"st": 30.0, "dwl": 0.0}
    }
    aquifer = Aquifer(unique_id="aq1", model=model, **aquifer_settings)
    print(f"  ✓ Created Aquifer: {aquifer.unique_id}")
    
    # 2. Create Field
    field_settings = {
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
            "yield": 0.0, "revenue": 0.0, "profit": 0.0,
            "irr_alloc": 0.0, "irr_used": 0.0, "tech": 0
        }
    }
    field = Field(unique_id="f1", model=model, **field_settings)
    print(f"  ✓ Created Field: {field.unique_id}, crop: {field.crop}")
    
    # 3. Create Well
    well_settings = {
        "efficiency": 0.75,
        "max_capacity": 100.0,
        "pumping_cost_per_m3": 0.05
    }
    well = Well(unique_id="w1", model=model, **well_settings)
    print(f"  ✓ Created Well: {well.unique_id}")
    
    # 4. Create Finance
    finance_settings = {
        "crop_price": 4.0,
        "cost": 1.5
    }
    finance = Finance(unique_id="fin1", model=model, **finance_settings)
    print(f"  ✓ Created Finance: {finance.unique_id}")
    
    # Serialize to JSON
    state = {
        "aquifer": serialize_aquifer(aquifer),
        "field": serialize_field(field),
        "well": serialize_well(well),
        "finance": serialize_finance(finance),
        "behavior": {
            "unique_id": "b1",
            "satisfaction": 0.7,
            "uncertainty": 0.3,
            "satisfaction_threshold": 0.7,
            "uncertainty_threshold": 0.3
        },
        "decision": {},
        "pumping_cost": 0.0,
        "results": {},
        "metadata": {
            "using_real_pychamp": True,
            "pychamp_version": "1.0.0",
            "container": "custom"
        }
    }
    
    return state


def create_simplified_state():
    """Fallback: Create state without PyChAMP library"""
    return {
        "aquifer": {
            "unique_id": "aq1", "aq_a": 0.1, "aq_b": 10.0,
            "area": 100.0, "sy": 0.2,
            "init": {"st": 30.0, "dwl": 0.0}
        },
        "field": {
            "unique_id": "f1", "crop": "corn", "field_area": 50.0,
            "soil_moisture": 0.5, "tech_pumping_rate_coefs": [0.8, 1.2],
            "water_yield_curves": {
                "corn": [[0.0, 0.0, 0.0], [100.0, 1.0, 0.8]],
                "wheat": [[0.0, 0.0, 0.0], [90.0, 0.9, 0.75]],
                "soybean": [[0.0, 0.0, 0.0], [80.0, 0.85, 0.7]]
            },
            "prec_aw_id": "default", "irrigation_policy": "fixed",
            "irrigation_application": 30.0, "irrigation_status": True,
            "irrigation_system": "center_pivot", "tech_index": 0,
            "aw_dp": 0.1, "aw_runoff": 0.05,
            "init": {
                "yield": 0.0, "revenue": 0.0, "profit": 0.0,
                "irr_alloc": 0.0, "irr_used": 0.0, "tech": 0
            }
        },
        "well": {
            "unique_id": "w1", "efficiency": 0.75,
            "max_capacity": 100.0, "pumping_cost_per_m3": 0.05
        },
        "finance": {
            "unique_id": "fin1", "crop_price": 4.0, "cost": 1.5,
            "net_profit": 0.0, "total_costs": 0.0,
            "profit_margin": 0.0, "water_productivity": 0.0
        },
        "behavior": {
            "unique_id": "b1", "satisfaction": 0.7, "uncertainty": 0.3,
            "satisfaction_threshold": 0.7, "uncertainty_threshold": 0.3
        },
        "decision": {},
        "pumping_cost": 0.0,
        "results": {},
        "metadata": {
            "using_real_pychamp": False,
            "pychamp_version": "simplified",
            "container": "standard"
        }
    }


# Serialization helper functions
def serialize_aquifer(aquifer):
    """Convert PyChAMP Aquifer object to dict"""
    return {
        "unique_id": aquifer.unique_id,
        "aq_a": aquifer.aq_a,
        "aq_b": aquifer.aq_b,
        "area": aquifer.area,
        "sy": aquifer.sy,
        "init": {"st": aquifer.init["st"], "dwl": aquifer.init["dwl"]}
    }


def serialize_field(field):
    """Convert PyChAMP Field object to dict"""
    return {
        "unique_id": field.unique_id,
        "crop": field.crop,
        "field_area": field.field_area,
        "soil_moisture": field.soil_moisture,
        "tech_pumping_rate_coefs": field.tech_pumping_rate_coefs,
        "water_yield_curves": field.water_yield_curves,
        "prec_aw_id": field.prec_aw_id,
        "irrigation_policy": field.irrigation_policy,
        "irrigation_application": field.irrigation_application,
        "irrigation_status": field.irrigation_status,
        "irrigation_system": field.irrigation_system,
        "tech_index": field.tech_index,
        "aw_dp": field.aw_dp,
        "aw_runoff": field.aw_runoff,
        "init": {
            "yield": field.init.get("yield", 0.0),
            "revenue": field.init.get("revenue", 0.0),
            "profit": field.init.get("profit", 0.0),
            "irr_alloc": field.init.get("irr_alloc", 0.0),
            "irr_used": field.init.get("irr_used", 0.0),
            "tech": field.init.get("tech", 0)
        }
    }


def serialize_well(well):
    """Convert PyChAMP Well object to dict"""
    return {
        "unique_id": well.unique_id,
        "efficiency": well.efficiency,
        "max_capacity": well.max_capacity,
        "pumping_cost_per_m3": well.pumping_cost_per_m3
    }


def serialize_finance(finance):
    """Convert PyChAMP Finance object to dict"""
    return {
        "unique_id": finance.unique_id,
        "crop_price": finance.crop_price,
        "cost": finance.cost,
        "net_profit": getattr(finance, 'net_profit', 0.0),
        "total_costs": getattr(finance, 'total_costs', 0.0),
        "profit_margin": getattr(finance, 'profit_margin', 0.0),
        "water_productivity": getattr(finance, 'water_productivity', 0.0)
    }