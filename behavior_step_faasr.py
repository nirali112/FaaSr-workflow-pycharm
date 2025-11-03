# behavior_step_faasr.py
import json
import os

def behavior_step_faasr():
    """
    Simulate farmer behavior and make irrigation decision.
    Downloads state, makes decision, uploads updated state.
    """
    print("[behavior_step_faasr] Starting behavior step...")
    
    # Download state from cloud storage
    print("[behavior_step_faasr] Downloading state from cloud...")
    faasr_get_file(
        server_name="S3",
        remote_folder="pychamp-workflow",
        remote_file="state.json",
        local_folder="",
        local_file="state.json"
    )
    
    # Load state
    with open("state.json", "r") as f:
        state = json.load(f)
    
    print("[behavior_step_faasr] State loaded successfully")
    
    # Extract behavior and field data
    behavior = state["behavior"]
    field = state["field"]
    aquifer = state["aquifer"]
    finance = state["finance"]
    
    # Get current conditions
    current_satisfaction = behavior["satisfaction"]
    current_uncertainty = behavior["uncertainty"]
    satisfaction_threshold = behavior["satisfaction_threshold"]
    uncertainty_threshold = behavior["uncertainty_threshold"]
    
    soil_moisture = field["soil_moisture"]
    aquifer_storage = aquifer["init"]["st"]
    
    print(f"[behavior_step_faasr] Current satisfaction: {current_satisfaction:.2f}")
    print(f"[behavior_step_faasr] Current uncertainty: {current_uncertainty:.2f}")
    print(f"[behavior_step_faasr] Soil moisture: {soil_moisture:.2f}")
    print(f"[behavior_step_faasr] Aquifer storage: {aquifer_storage:.2f} m³")
    
    # Simulate decision-making based on CONSUMAT framework
    # Determine CONSUMAT state
    if current_satisfaction > satisfaction_threshold:
        if current_uncertainty <= uncertainty_threshold:
            consumat_state = "repetition"
        else:
            consumat_state = "imitation"
    else:
        if current_uncertainty <= uncertainty_threshold:
            consumat_state = "deliberation"
        else:
            consumat_state = "social_comparison"
    
    print(f"[behavior_step_faasr] CONSUMAT state: {consumat_state}")
    
    # Make irrigation decision based on state
    if consumat_state == "repetition":
        # High satisfaction, low uncertainty - repeat last action
        irrigation_action = "irrigate"
        irrigation_amount = 30.0  # Default amount
        
    elif consumat_state == "imitation":
        # High satisfaction, high uncertainty - continue but be cautious
        irrigation_action = "irrigate"
        irrigation_amount = 25.0  # Slightly reduced
        
    elif consumat_state == "deliberation":
        # Low satisfaction, low uncertainty - optimize carefully
        if soil_moisture < 0.3:
            irrigation_action = "irrigate"
            irrigation_amount = 35.0  # Increase to improve conditions
        elif aquifer_storage < 15.0:
            irrigation_action = "irrigate"
            irrigation_amount = 20.0  # Conserve water
        else:
            irrigation_action = "irrigate"
            irrigation_amount = 30.0  # Normal amount
            
    else:  # social_comparison
        # Low satisfaction, high uncertainty - be very conservative
        if aquifer_storage < 10.0:
            irrigation_action = "no_irrigation"
            irrigation_amount = 0.0
        else:
            irrigation_action = "irrigate"
            irrigation_amount = 15.0  # Minimal irrigation
    
    # Consider water availability - don't irrigate if storage is critical
    if aquifer_storage < 5.0:
        print("[behavior_step_faasr] WARNING: Critical water shortage!")
        irrigation_action = "no_irrigation"
        irrigation_amount = 0.0
    
    # Consider soil moisture - reduce if already high
    if soil_moisture > 0.8:
        print("[behavior_step_faasr] Soil moisture high, reducing irrigation")
        irrigation_amount = irrigation_amount * 0.5
    
    # Create decision object
    decision = {
        "action": irrigation_action,
        "amount": irrigation_amount,
        "satisfaction": current_satisfaction,
        "uncertainty": current_uncertainty,
        "consumat_state": consumat_state,
        "reasoning": f"State: {consumat_state}, Storage: {aquifer_storage:.1f}m³, Soil: {soil_moisture:.2f}"
    }
    
    # Update state with decision
    state["decision"] = decision
    
    print(f"[behavior_step_faasr] Decision made:")
    print(f"  - Action: {irrigation_action}")
    print(f"  - Amount: {irrigation_amount:.1f} mm")
    print(f"  - CONSUMAT state: {consumat_state}")
    print(f"  - Reasoning: {decision['reasoning']}")
    
    # Save updated state to local file
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    print("[behavior_step_faasr] State updated locally")
    
    # Upload updated state back to cloud storage
    faasr_put_file(
        server_name="S3",
        local_folder="",
        local_file="state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )
    
    print("[behavior_step_faasr] State uploaded to cloud")
    print("[behavior_step_faasr] Behavior step complete!")