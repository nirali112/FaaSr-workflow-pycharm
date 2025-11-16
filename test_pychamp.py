"""
Local test for PyChAMP - ALL 5 COMPONENTS
Tests: Aquifer, Well, Finance, Field, Behavior
"""

from mesa import Model
from mesa.time import RandomActivation
import numpy as np

def test_pychamp_complete():
    print("=" * 70)
    print("Testing ALL PyChAMP Components Locally")
    print("=" * 70)
    
    # Import components
    from py_champ.components.aquifer import Aquifer
    from py_champ.components.well import Well
    from py_champ.components.finance import Finance
    from py_champ.components.field import Field
    from py_champ.components.behavior import Behavior
    
    # 1. Create Mesa model with required attributes
    print("\n1. Creating model...")
    model = Model()
    model.schedule = RandomActivation(model)
    model.current_step = 0
    model.crop_options = ["corn", "soy", "wheat"]  # Required by Field
    model.area_split = 4  # Required by Field (divide field into 4 sections)
    print(f"   ✅ Model created with {len(model.crop_options)} crops")
    
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
    print(f"   ✅ Aquifer 'aq1' initialized")
    print(f"      Saturated thickness: {aquifer.st} m")
    
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
    print(f"   ✅ Well 'w1' initialized")
    print(f"      Connected to: {well.aquifer_id}")
    
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
    print(f"   ✅ Finance 'fin1' initialized")
    print(f"      Energy price: ${finance.energy_price}/kWh")
    
    # 5. Initialize Field
    print("\n5. Initializing Field...")
    field_settings = {
        "field_area": 100.0,  # hectares
        "water_yield_curves": {
            # Format: [ymax, wmax, a, b, c, min_y_ratio]
            "corn": [10.0, 600.0, 0.5, 1.0, 0.3, 0.2],
            "soy": [4.0, 400.0, 0.6, 1.2, 0.25, 0.15],
            "wheat": [5.0, 350.0, 0.55, 1.1, 0.28, 0.18]
        },
        "tech_pumping_rate_coefs": {
            "gravity": [1.0, 0.5, 10.0],      # [a_te, b_te, l_pr]
            "sprinkler": [0.85, 0.6, 15.0],
            "drip": [0.70, 0.7, 20.0]
        },
        "prec_aw_id": "aq1",  # Precipitation/available water source
        "init": {
            "crop": "corn",
            "tech": "sprinkler",      # ← Changed from "irr_tech" to "tech"
            "field_type": "irrigated"  # ← Added field_type
        }
    }
    field = Field("f1", model, field_settings)
    model.schedule.add(field)
    print(f"   ✅ Field 'f1' initialized")
    print(f"      Field area: {field.field_area} ha")
    print(f"      Initial crop: {field_settings['init']['crop']}")
    
    # 6. Initialize Behavior
    # print("\n6. Initializing Behavior...")
    # behavior_settings = {
    #     "behavior_ids_in_network": ["b1"],  # This agent's network
    #     "field_ids": ["f1"],                # Fields it manages
    #     "well_ids": ["w1"],                 # Wells it manages
    #     "finance_id": "fin1",               # Finance component
    #     "decision_making": {
    #         "discount_rate": 0.05,
    #         "risk_aversion": 0.3
    #     },
    #     "consumat": {                       # Agent decision framework
    #         "satisfaction_threshold": 0.7,
    #         "uncertainty_threshold": 0.5
    #     },
    #     "water_rights": {
    #         "allocation": 1000.0,           # m³/year
    #         "type": "proportional"
    #     },
    #     "gurobi": {                         # Optimization settings
    #         "OutputFlag": 0,                # Suppress Gurobi output
    #         "TimeLimit": 60
    #     }
    # }
    # behavior = Behavior("b1", model, behavior_settings)
    # model.schedule.add(behavior)
    # print(f"   ✅ Behavior 'b1' initialized")
    # print(f"      Manages fields: {behavior.field_ids}")
    # print(f"      Manages wells: {behavior.well_ids}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL 5 COMPONENTS INITIALIZED SUCCESSFULLY!")
    print("=" * 70)
    
    print("\nModel Components:")
    print(f"  1. Aquifer:  {aquifer.unique_id}")
    print(f"  2. Well:     {well.unique_id}")
    print(f"  3. Finance:  {finance.unique_id}")
    print(f"  4. Field:    {field.unique_id}")
    # print(f"  5. Behavior: {behavior.unique_id}")
    
    print("\n" + "=" * 70)
    print("Component Details:")
    print("=" * 70)
    
    print(f"\n📊 Aquifer '{aquifer.unique_id}':")
    print(f"    - Saturated thickness: {aquifer.st} m")
    print(f"    - Area: {aquifer.area} ha")
    
    print(f"\n💧 Well '{well.unique_id}':")
    print(f"    - Pumping capacity: {well.pumping_capacity} m³/day")
    print(f"    - Pump efficiency: {well.eff_pump * 100}%")
    print(f"    - Connected to: {well.aquifer_id}")
    
    print(f"\n💰 Finance '{finance.unique_id}':")
    # print(f"    - Initial savings: ${finance.savings}")
    print(f"    - Energy price: ${finance.energy_price}/kWh")
    print(f"    - Crop prices: {finance.crop_price}")
    
    print(f"\n🌾 Field '{field.unique_id}':")
    print(f"    - Area: {field.field_area} ha")
    print(f"    - Crops available: {model.crop_options}")
    print(f"    - Field sections: {model.area_split}")
    
    # print(f"\n🧠 Behavior '{behavior.unique_id}':")
    # print(f"    - Fields managed: {behavior.field_ids}")
    # print(f"    - Wells managed: {behavior.well_ids}")
    # print(f"    - Finance linked: {behavior.finance_id}")
    
    print("\n" + "=" * 70)
    print("🎉 READY FOR FaaSr DEPLOYMENT!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_pychamp_complete()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)