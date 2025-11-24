"""
FaaSr Step: Results Aggregation
Summarizes all simulation results
"""

import sys
import json
import subprocess

def install_dependencies():
    """Install required packages"""
    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "numpy", "pandas"
    ])
    print("Dependencies installed")

def results_step_faasr(output1="payload"):
    """Aggregate and summarize results"""
    
    # Download from S3
    try:
        faasr_get_file(
            server_name="S3",
            remote_folder="pychamp-workflow",
            remote_file=output1,
            local_folder="",
            local_file=output1
        )
        print("Downloaded payload from S3")
    except NameError:
        print("Running locally")
    except Exception as e:
        print(f"Download error: {e}")
    
    # Read file
    try:
        with open(output1, "r") as f:
            faasr_data = json.load(f)
    except FileNotFoundError:
        print("No payload file")
        return
    
    install_dependencies()
        
    state = faasr_data.get("state", {})
    if not state:
        print("No state found")
        return
    
    components = state.get("components", {})
    
    # Aquifer results
    print("\n AQUIFER:")
    aquifer = components.get("aquifer", {})
    print(f"  Initial saturated thickness: 30.0 m")
    print(f"  Final saturated thickness: {aquifer.get('st', 0):.2f} m")
    print(f"  Water level change: {aquifer.get('dwl_change', 0):.2f} m")
    print(f"  Total withdrawal: {aquifer.get('withdrawal', 0):.2f} m-ha")
    
    # Well results
    print("\n WELL:")
    well = components.get("well", {})
    print(f"  Pumping capacity: {well.get('pumping_capacity', 0):.2f} m³/day")
    print(f"  Pump efficiency: {well.get('eff_pump', 0)*100:.1f}%")
    print(f"  Operating days: {well.get('pumping_days', 0)}")
    
    # Field results
    print("\n FIELD:")
    field = components.get("field", {})
    print(f"  Field area: {field.get('field_area', 0):.2f} ha")
    print(f"  Crops grown: {', '.join(field.get('crops', []))}")
    print(f"  Irrigation tech: {field.get('tech', 'unknown')}")
    print(f"  Total yield: {field.get('yield', 0):.2f} (1e4 bu)")
    print(f"  Irrigation volume: {field.get('irrigation_volume', 0):.2f} m-ha")
    
    # Finance results
    print("\n FINANCE:")
    finance = components.get("finance", {})
    print(f"  Revenue: ${finance.get('revenue', 0):.2f} (1e4$)")
    print(f"  Energy cost: ${finance.get('energy_cost', 0):.2f} (1e4$)")
    print(f"  Tech cost: ${finance.get('tech_cost', 0):.2f} (1e4$)")
    print(f"  PROFIT: ${finance.get('profit', 0):.2f} (1e4$)")
    
    # Workflow summary
    print("WORKFLOW SUMMARY:")
    print(f"  Total steps executed: {state.get('model_step', 0)}")
    print(f"  Final workflow step: {state.get('workflow_step', 'unknown')}")
    print(f"  Status: {state.get('status', 'unknown')}")
    
    print("PYCHAMP WORKFLOW COMPLETED SUCCESSFULLY!")
    
    # Save final results
    results_summary = {
        "aquifer_depletion_m": aquifer.get("st", 30) - 30.0,
        "total_yield_1e4bu": field.get("yield", 0),
        "profit_1e4dollar": finance.get("profit", 0),
        "workflow_steps": state.get("model_step", 0)
    }
    
    state["results_summary"] = results_summary
    faasr_data["state"] = state
    
    with open(output1, "w") as f:
        json.dump(faasr_data, f, indent=2)
    
    try:
        faasr_put_file(
            server_name="S3",
            local_folder="",
            local_file=output1,
            remote_folder="pychamp-workflow",
            remote_file=output1
        )
        print("\nFinal results uploaded to S3")
    except NameError:
        print("\nRunning locally - results saved")

if __name__ == "__main__":
    results_step_faasr()