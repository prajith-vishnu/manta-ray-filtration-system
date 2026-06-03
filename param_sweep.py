import os
import csv
# Import our modular physics engine function directly from your simulations folder
from simulations.flow_model import run_polymer_simulation

def execute_parametric_sweep():
    print("====================================================")
    print("STARTING: Automated Parametric Geometric Sweep Matrix")
    print("====================================================")
    
    # 📐 THE TESTING VARIABLES (Geometric Shape Array vs. Intake Velocity Array)
    test_heights = [2.0, 4.0, 6.0, 8.0]            # Varying gill raker heights (mm)
    test_speeds = [150.0, 250.0, 400.0, 600.0]     # Varying water velocity vectors (mm/s)
    particles_per_test = 200                       # Elevated sample size for data validity
    
    csv_filename = "simulation_telemetry.csv"
    
    # Check if file already exists so we don't accidentally write duplicate headers
    file_exists = os.path.isfile(csv_filename)
    
    print(f"Preparing data pipeline output file: {csv_filename}")
    
    # Open the CSV file in append mode ('a') so we build a permanent running history of test data
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # If the spreadsheet is brand new, establish the index headers
        if not file_exists:
            writer.writerow(["Raker_Height_mm", "Flow_Speed_mms", "Sample_Size", "Filtration_Efficiency_Pct"])
        
        total_runs = len(test_heights) * len(test_speeds)
        current_run = 0
        
        print(f"Running {total_runs} distinct stress-test iterations completely headless...\n")
        print(f"{'RUN':<5} | {'RAKER HEIGHT':<14} | {'FLOW SPEED':<12} | {'SYSTEM YIELD':<12}")
        print("-" * 52)
        
        # 🌪️ THE MASTER NESTED AUTOMATION LOOP
        for h in test_heights:
            for s in test_speeds:
                current_run += 1
                
                # Execute the underlying physics code silently behind the scenes
                efficiency = run_polymer_simulation(
                    raker_height=h, 
                    flow_speed_x=s, 
                    total_particles=particles_per_test, 
                    headless=True
                )
                
                # Write the exact telemetry data row into our spreadsheet file on disk
                writer.writerow([h, s, particles_per_test, f"{efficiency:.2f}"])
                
                # Stream live analytical updates straight to the terminal
                print(f"#{current_run:<4} | {h:<12.1f} mm | {s:<10.1f} mm/s | {efficiency:.1f}%")
                
    print("\n====================================================")
    print(f"SUCCESS: Sweep completed. Telemetry appended to '{csv_filename}'.")
    print("====================================================")

if __name__ == "__main__":
    execute_parametric_sweep()