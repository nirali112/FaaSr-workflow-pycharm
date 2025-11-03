# optimization_step_faasr.py
import json
import os

def optimization_step_faasr():
    """
    Optimize irrigation strategy for next period.
    Update satisfaction and uncertainty based on outcomes.
    """
    print("[optimization_step_faasr] Starting optimization step...")
    
    # Download state
    print("[optimization_step_faasr] Downloading state...")
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
    
    behavior = state["behavior"]
    field = state["field"]
    aquifer = state["aquifer"]
    finance = state["finance"]
    
    # Get current conditions
    current_soil_moisture = field["soil_moisture"]
    current_storage = aquifer["init"]["st"]
    current_profit = finance.get("net_profit", 0.0)
    
    print(f"[optimization_step_faasr] Optimizing for next period...")
    
    # Calculate optimal irrigation for next period
    max_irrigation = min(50.0, current_storage * 0.1)  # Don't use more than 10% of storage
    
    # Consider soil moisture - if already high, reduce irrigation
    if current_soil_moisture > 0.8:
        optimal_irrigation = max(0, max_irrigation * 0.5)
    elif current_soil_moisture < 0.3:
        optimal_irrigation = max_irrigation
    else:
        optimal_irrigation = max_irrigation * 0.7
    
    # Economic adjustment - if profit is low, be more conservative
    if current_profit < 0:
        optimal_irrigation *= 0.5  # Reduce irrigation if losing money
    
    # Update behavior parameters based on optimization results
    behavior["optimal_irrigation"] = optimal_irrigation
    behavior["last_profit"] = current_profit
    behavior["last_soil_moisture"] = current_soil_moisture
    behavior["last_storage"] = current_storage
    
    # Update satisfaction based on economic performance
    if current_profit > 10.0:
        behavior["satisfaction"] = min(1.0, behavior["satisfaction"] + 0.1)
    elif current_profit < 0:
        behavior["satisfaction"] = max(0.0, behavior["satisfaction"] - 0.1)
    
    # Update uncertainty based on water availability
    if current_storage < 10.0:  # Low storage
        behavior["uncertainty"] = min(1.0, behavior["uncertainty"] + 0.2)
    elif current_storage > 50.0:  # High storage
        behavior["uncertainty"] = max(0.0, behavior["uncertainty"] - 0.1)
    
    # Update state
    state["behavior"] = behavior
    
    print(f"[optimization_step_faasr] Optimization results:")
    print(f"  - Optimal irrigation: {optimal_irrigation:.1f} mm")
    print(f"  - Current satisfaction: {behavior['satisfaction']:.2f}")
    print(f"  - Current uncertainty: {behavior['uncertainty']:.2f}")
    print(f"  - Available storage: {current_storage:.2f} m³")
    print(f"  - Current profit: ${current_profit:.2f}")
    
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
    
    print("[optimization_step_faasr] Optimization step complete!")