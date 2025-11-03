# field_step_faasr.py
import json
import os

def field_step_faasr():
    """
    Update field conditions based on irrigation decision.
    Calculate crop yield, revenue, and profit.
    """
    print("[field_step_faasr] Starting field step...")
    
    # Download state
    print("[field_step_faasr] Downloading state...")
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
    
    field = state["field"]
    decision = state.get("decision", {})
    finance = state["finance"]
    
    # Extract irrigation decision
    irrigation_amount = decision.get("amount", 0.0)
    irrigation_action = decision.get("action", "no_irrigation")
    
    print(f"[field_step_faasr] Processing irrigation: {irrigation_action}, {irrigation_amount:.1f} mm")
    
    # Update soil moisture based on irrigation
    if irrigation_action == "irrigate" and irrigation_amount > 0:
        # Apply irrigation to soil moisture
        field["soil_moisture"] = min(1.0, field["soil_moisture"] + (irrigation_amount / 100.0))
        field["init"]["irr_used"] = irrigation_amount
        field["init"]["irr_alloc"] = irrigation_amount
    else:
        # Natural soil moisture decline
        field["soil_moisture"] = max(0.1, field["soil_moisture"] - 0.05)
        field["init"]["irr_used"] = 0.0
        field["init"]["irr_alloc"] = 0.0
    
    # Calculate crop yield based on water availability
    water_available = field["soil_moisture"] * 100  # Convert to mm equivalent
    
    # Get yield curve for current crop
    yield_curves = field["water_yield_curves"].get(field["crop"], [[0.0, 0.0, 0.0], [100.0, 1.0, 0.8]])
    
    # Interpolate yield based on water availability
    if len(yield_curves) >= 2:
        water_points = [curve[0] for curve in yield_curves]
        yield_points = [curve[1] for curve in yield_curves]
        
        # Simple linear interpolation
        if water_available <= water_points[0]:
            yield_ratio = yield_points[0]
        elif water_available >= water_points[-1]:
            yield_ratio = yield_points[-1]
        else:
            # Find the segment to interpolate
            for i in range(len(water_points) - 1):
                if water_points[i] <= water_available <= water_points[i + 1]:
                    w1, w2 = water_points[i], water_points[i + 1]
                    y1, y2 = yield_points[i], yield_points[i + 1]
                    yield_ratio = y1 + (y2 - y1) * (water_available - w1) / (w2 - w1)
                    break
            else:
                yield_ratio = yield_points[0]
    else:
        yield_ratio = 0.5  # Default if no yield curve
    
    # Calculate actual yield (tons per hectare)
    max_yield = 10.0  # Maximum potential yield for the crop
    actual_yield = yield_ratio * max_yield * field["field_area"] / 100  # Convert to total tons
    
    # Update field state
    field["init"]["yield"] = actual_yield
    
    # Calculate revenue and profit
    revenue = actual_yield * finance["crop_price"]
    cost = finance["cost"] * field["field_area"] / 100  # Cost per hectare
    profit = revenue - cost
    
    field["init"]["revenue"] = revenue
    field["init"]["profit"] = profit
    
    # Update state
    state["field"] = field
    
    print(f"[field_step_faasr] Updated field conditions:")
    print(f"  - Soil moisture: {field['soil_moisture']:.3f}")
    print(f"  - Irrigation used: {field['init']['irr_used']:.1f} mm")
    print(f"  - Yield: {actual_yield:.2f} tons")
    print(f"  - Revenue: ${revenue:.2f}")
    print(f"  - Profit: ${profit:.2f}")
    
    # Save and upload
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    faasr_put_file(
        server_name="S3",
        local_folder="",
        local_file="state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )
    
    print("[field_step_faasr] Field step complete!")