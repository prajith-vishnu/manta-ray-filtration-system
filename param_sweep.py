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
    test_regimes = [False, True]                   # Laminar vs. storm surge turbulence
    particles_per_test = 200                       # Elevated sample size for data validity

    csv_filename = "simulation_telemetry.csv"

    print(f"Preparing data pipeline output file: {csv_filename}")

    regime_totals = {"Laminar": [], "Turbulent": []}

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Raker_Height_mm", "Flow_Speed_mms", "Flow_Regime", "Sample_Size", "Filtration_Efficiency_Pct"])

        total_runs = len(test_heights) * len(test_speeds) * len(test_regimes)
        current_run = 0

        print(f"Running {total_runs} distinct stress-test iterations completely headless...\n")
        print(f"{'RUN':<5} | {'RAKER HEIGHT':<14} | {'FLOW SPEED':<12} | {'REGIME':<10} | {'SYSTEM YIELD':<12}")
        print("-" * 65)

        # 🌪️ THE MASTER NESTED AUTOMATION LOOP
        for storm in test_regimes:
            regime = "Turbulent" if storm else "Laminar"
            for h in test_heights:
                for s in test_speeds:
                    current_run += 1

                    # Execute the underlying physics code silently behind the scenes
                    efficiency = run_polymer_simulation(
                        raker_height=h,
                        flow_speed_x=s,
                        total_particles=particles_per_test,
                        headless=True,
                        storm_mode=storm
                    )

                    # Write the exact telemetry data row into our spreadsheet file on disk
                    writer.writerow([h, s, regime, particles_per_test, f"{efficiency:.2f}"])
                    regime_totals[regime].append(efficiency)

                    # Stream live analytical updates straight to the terminal
                    print(f"#{current_run:<4} | {h:<12.1f} mm | {s:<10.1f} mm/s | {regime:<10} | {efficiency:.1f}%")

    print("\n====================================================")
    for regime, values in regime_totals.items():
        avg = sum(values) / len(values)
        print(f"{regime} average deflection purity: {avg:.1f}% (n={len(values)} runs)")
    print(f"SUCCESS: Sweep completed. Telemetry written to '{csv_filename}'.")
    print("====================================================")

if __name__ == "__main__":
    execute_parametric_sweep()