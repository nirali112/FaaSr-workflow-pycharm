# results_step_faasr.py
import json
import os

def results_step_faasr():
    """
    Aggregate and display final results.
    Calculate sustainability metrics.
    """
    print("[results_step_faasr] Starting results step...")
    
    # Download state
    print("[results_step_faasr] Downloading final state...")
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
    
    field = state["field"]
    aquifer = state["aquifer"]
    well = state["well"]
    finance = state["finance"]
    behavior = state["behavior"]
    decision = state.get("decision", {})
    
    # Aggregate all results
    results = {
        "irrigation": {
            "decision": decision.get("action", "no_irrigation"),
            "amount": decision.get("amount", 0.0),
            "satisfaction": decision.get("satisfaction", 0.0),
            "uncertainty": decision.get("uncertainty", 0.0),
            "consumat_state": decision.get("consumat_state", "unknown")
        },
        "field": {
            "soil_moisture": field["soil_moisture"],
            "yield": field["init"].get("yield", 0.0),
            "revenue": field["init"].get("revenue", 0.0),
            "profit": field["init"].get("profit", 0.0),
            "irrigation_used": field["init"].get("irr_used", 0.0)
        },
        "aquifer": {
            "storage": aquifer["init"]["st"],
            "drawdown": aquifer["init"]["dwl"],
            "area": aquifer["area"],
            "specific_yield": aquifer["sy"]
        },
        "economics": {
            "net_profit": finance.get("net_profit", 0.0),
            "total_costs": finance.get("total_costs", 0.0),
            "profit_margin": finance.get("profit_margin", 0.0),
            "water_productivity": finance.get("water_productivity", 0.0),
            "pumping_cost": state.get("pumping_cost", 0.0)
        },
        "behavior": {
            "satisfaction": behavior.get("satisfaction", 0.7),
            "uncertainty": behavior.get("uncertainty", 0.3),
            "optimal_irrigation": behavior.get("optimal_irrigation", 0.0)
        }
    }
    
    # Calculate sustainability metrics
    sustainability_score = 0.0
    if aquifer["init"]["st"] > 20.0:  # Good storage
        sustainability_score += 0.4
    if field["soil_moisture"] > 0.6:  # Good soil moisture
        sustainability_score += 0.3
    if finance.get("net_profit", 0.0) > 0:  # Profitable
        sustainability_score += 0.3
    
    results["sustainability"] = {
        "score": sustainability_score,
        "water_availability": "Good" if aquifer["init"]["st"] > 20.0 else "Low",
        "soil_health": "Good" if field["soil_moisture"] > 0.6 else "Poor",
        "economic_viability": "Profitable" if finance.get("net_profit", 0.0) > 0 else "Loss"
    }
    
    # Store results in state
    state["results"] = results
    
    # # Print comprehensive summary
    # print(f"\n{'='*60}")
    # print(f"PYCHAMP SIMULATION RESULTS SUMMARY")
    # print(f"{'='*60}")
    
    # print(f"\n🌾 FIELD CONDITIONS:")
    # print(f"  - Crop: {field['crop']}")
    # print(f"  - Soil moisture: {field['soil_moisture']:.3f}")
    # print(f"  - Yield: {field['init'].get('yield', 0.0):.2f} tons")
    # print(f"  - Irrigation used: {field['init'].get('irr_used', 0.0):.1f} mm")
    
    # print(f"\n💧 AQUIFER STATUS:")
    # print(f"  - Storage: {aquifer['init']['st']:.2f} m³")
    # print(f"  - Drawdown: {aquifer['init']['dwl']:.2f} m")
    # print(f"  - Area: {aquifer['area']:.1f} km²")
    
    # print(f"\n💰 ECONOMIC OUTCOMES:")
    # print(f"  - Revenue: ${field['init'].get('revenue', 0.0):.2f}")
    # print(f"  - Net profit: ${finance.get('net_profit', 0.0):.2f}")
    # print(f"  - Profit margin: {finance.get('profit_margin', 0.0):.1f}%")
    # print(f"  - Water productivity: ${finance.get('water_productivity', 0.0):.2f}/mm")
    
    # print(f"\n🧠 BEHAVIORAL INSIGHTS:")
    # print(f"  - Decision: {decision.get('action', 'no_irrigation')}")
    # print(f"  - CONSUMAT state: {decision.get('consumat_state', 'unknown')}")
    # print(f"  - Satisfaction: {behavior.get('satisfaction', 0.7):.2f}")
    # print(f"  - Uncertainty: {behavior.get('uncertainty', 0.3):.2f}")
    # print(f"  - Optimal next irrigation: {behavior.get('optimal_irrigation', 0.0):.1f} mm")
    
    # print(f"\n🌱 SUSTAINABILITY ASSESSMENT:")
    # print(f"  - Overall score: {sustainability_score:.1f}/1.0")
    # print(f"  - Water availability: {results['sustainability']['water_availability']}")
    # print(f"  - Soil health: {results['sustainability']['soil_health']}")
    # print(f"  - Economic viability: {results['sustainability']['economic_viability']}")
    
    # print(f"\n{'='*60}")
    
    # Save final state
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)
    
    faasr_put_file(
        server_name="My_S3_Bucket",
        local_folder="",
        local_file="state.json",
        remote_folder="pychamp-workflow",
        remote_file="state.json"
    )
    
    print("[results_step_faasr] Results step complete!")
    print("[results_step_faasr] ✅ Full workflow executed successfully!")