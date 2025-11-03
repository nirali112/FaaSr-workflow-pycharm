# finance_step_faasr.py
import json
import os

def finance_step_faasr():
    """
    Calculate financial outcomes including costs and profits.
    """
    print("[finance_step_faasr] Starting finance step...")
    
    # Download state
    print("[finance_step_faasr] Downloading state...")
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
    finance = state["finance"]
    pumping_cost = state.get("pumping_cost", 0.0)
    
    # Get field economic results
    field_revenue = field["init"].get("revenue", 0.0)
    field_profit = field["init"].get("profit", 0.0)
    
    print(f"[finance_step_faasr] Calculating financial summary...")
    
    # Calculate total costs including pumping
    total_costs = (finance["cost"] * field["field_area"] / 100) + pumping_cost
    
    # Calculate net profit
    net_profit = field_revenue - total_costs
    
    # Calculate profit margin
    profit_margin = (net_profit / field_revenue * 100) if field_revenue > 0 else 0
    
    # Calculate water productivity (revenue per unit of water)
    irrigation_used = field["init"].get("irr_used", 0.0)
    water_productivity = field_revenue / irrigation_used if irrigation_used > 0 else 0
    
    # Update finance state
    finance["net_profit"] = net_profit
    finance["total_costs"] = total_costs
    finance["profit_margin"] = profit_margin
    finance["water_productivity"] = water_productivity
    
    # Update state
    state["finance"] = finance
    
    print(f"[finance_step_faasr] Financial summary:")
    print(f"  - Field revenue: ${field_revenue:.2f}")
    print(f"  - Field costs: ${total_costs - pumping_cost:.2f}")
    print(f"  - Pumping costs: ${pumping_cost:.2f}")
    print(f"  - Total costs: ${total_costs:.2f}")
    print(f"  - Net profit: ${net_profit:.2f}")
    print(f"  - Profit margin: {profit_margin:.1f}%")
    print(f"  - Water productivity: ${water_productivity:.2f}/mm")
    
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
    
    print("[finance_step_faasr] Finance step complete!")