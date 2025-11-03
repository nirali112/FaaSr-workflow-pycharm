# aquifer_step_faasr.py
import json
import os

def aquifer_step_faasr():
    """
    Update aquifer conditions based on pumping.
    Calculate groundwater storage and drawdown changes.
    """
    print("[aquifer_step_faasr] Starting aquifer step...")
    
    # Download state
    print("[aquifer_step_faasr] Downloading state...")
    faasr_get_file(
        server_name="My_S3_Bucket",
        remote_folder="pychamp-workflow",
        remote_file="state.json",
        local_folder="",
        local_file="state.json"
    )
    
    # Load state
    with open("state.json", "r") as f:
        state = json.load(f)
    
    aquifer = state["aquifer"]
    field = state["field"]
    well = state["well"]
    
    # Get irrigation amount from field
    irrigation_used = field["init"].get("irr_used", 0.0)
    
    print(f"[aquifer_step_faasr] Processing pumping for {irrigation_used:.1f} mm irrigation")
    
    # Calculate pumping from aquifer
    if irrigation_used > 0:
        # Convert irrigation amount to pumping volume (accounting for well efficiency)
        pumping_volume = irrigation_used * field["field_area"] / 10000  # Convert to m³
        actual_pumping = pumping_volume / well["efficiency"]  # Account for well efficiency
    else:
        actual_pumping = 0.0
    
    # Natural recharge (simplified model)
    natural_recharge = aquifer["area"] * 0.001  # 1mm recharge per time step
    
    # Update aquifer storage using linear reservoir model
    current_storage = aquifer["init"]["st"]
    
    # Aquifer response to pumping
    storage_change = natural_recharge - actual_pumping
    new_storage = max(0, current_storage + storage_change)
    
    # Update drawdown (depth to water level)
    current_dwl = aquifer["init"]["dwl"]
    if new_storage < current_storage:
        # Pumping causes drawdown
        drawdown_increase = (current_storage - new_storage) / (aquifer["area"] * aquifer["sy"])
        new_dwl = current_dwl + drawdown_increase
    else:
        # Recharge reduces drawdown
        drawdown_decrease = (new_storage - current_storage) / (aquifer["area"] * aquifer["sy"])
        new_dwl = max(0, current_dwl - drawdown_decrease)
    
    # Update aquifer state
    aquifer["init"]["st"] = new_storage
    aquifer["init"]["dwl"] = new_dwl
    
    # Calculate pumping cost
    pumping_cost = actual_pumping * well["pumping_cost_per_m3"]
    
    # Update state
    state["aquifer"] = aquifer
    state["pumping_cost"] = pumping_cost
    
    print(f"[aquifer_step_faasr] Updated aquifer conditions:")
    print(f"  - Storage: {new_storage:.2f} m³")
    print(f"  - Drawdown: {new_dwl:.2f} m")
    print(f"  - Pumping: {actual_pumping:.2f} m³")
    print(f"  - Pumping cost: ${pumping_cost:.2f}")
    
    # Save and upload
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    faasr_put_file(
        server_name="My_S3_Bucket",
        local_folder="",
        local_file="state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )
    
    print("[aquifer_step_faasr] Aquifer step complete!")