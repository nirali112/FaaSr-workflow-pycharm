import json
import sys
import subprocess

def init_components_faasr():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "numpy", "pandas", "mesa==2.1.1"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "git+https://github.com/philip928lin/PyCHAMP.git"])
    
    from py_champ.components.aquifer import Aquifer
    from py_champ.components.field import Field
    from py_champ.components.well import Well
    from py_champ.components.finance import Finance
    
    class MinimalModel:
        def __init__(self):
            self.schedule = None
            self.running = True
            self.crop_options = ["corn", "wheat", "soybean"]
            self.area_split = [1.0]
            self.tech_options = [{"name": "center_pivot", "efficiency": 0.75}]
    
    model = MinimalModel()
    
    aquifer = Aquifer(
        unique_id="aq1",
        model=model,
        aq_a=0.1,
        aq_b=10.0,
        area=100.0,
        sy=0.2,
        init={"st": 30.0, "dwl": 0.0}
    )
    
    field = Field(
        unique_id="f1",
        model=model,
        crop="corn",
        field_area=50.0,
        soil_moisture=0.5,
        tech_pumping_rate_coefs=[0.8, 1.2],
        water_yield_curves={
            "corn": [[0.0, 0.0, 0.0], [100.0, 1.0, 0.8]],
            "wheat": [[0.0, 0.0, 0.0], [90.0, 0.9, 0.75]],
            "soybean": [[0.0, 0.0, 0.0], [80.0, 0.85, 0.7]]
        },
        prec_aw_id="default",
        irrigation_policy="fixed",
        irrigation_application=30.0,
        irrigation_status=True,
        irrigation_system="center_pivot",
        tech_index=0,
        aw_dp=0.1,
        aw_runoff=0.05,
        init={"yield": 0.0, "revenue": 0.0, "profit": 0.0, "irr_alloc": 0.0, "irr_used": 0.0, "tech": 0}
    )
    
    well = Well(
        unique_id="w1",
        model=model,
        efficiency=0.75,
        max_capacity=100.0,
        pumping_cost_per_m3=0.05
    )
    
    finance = Finance(
        unique_id="fin1",
        model=model,
        crop_price=4.0,
        cost=1.5
    )
    
    state = {
        "aquifer": {
            "unique_id": aquifer.unique_id,
            "aq_a": aquifer.aq_a,
            "aq_b": aquifer.aq_b,
            "area": aquifer.area,
            "sy": aquifer.sy,
            "init": {"st": aquifer.init["st"], "dwl": aquifer.init["dwl"]}
        },
        "field": {
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
        },
        "well": {
            "unique_id": well.unique_id,
            "efficiency": well.efficiency,
            "max_capacity": well.max_capacity,
            "pumping_cost_per_m3": well.pumping_cost_per_m3
        },
        "finance": {
            "unique_id": finance.unique_id,
            "crop_price": finance.crop_price,
            "cost": finance.cost,
            "net_profit": 0.0,
            "total_costs": 0.0,
            "profit_margin": 0.0,
            "water_productivity": 0.0
        },
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
            "using_real_pychamp": True
        }
    }
    
    with open("pychamp_state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    faasr_put_file(
        server_name="S3",
        local_folder="",
        local_file="pychamp_state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )