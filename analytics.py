import csv
import matplotlib.pyplot as plt
from collections import defaultdict

def generate_performance_report():
    print("====================================================")
    print("STARTING: Telemetry Parser & Analytics Charting Suite")
    print("====================================================")
    
    csv_filename = "simulation_telemetry.csv"
    
    # Structure to hold parsed data: { raker_height: ([speeds], [efficiencies]) }
    parsed_data = defaultdict(lambda: ([], []))
    
    print(f"Reading raw matrix telemetry from {csv_filename}...")
    
    # Read and sort the CSV rows
    with open(csv_filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            height = float(row['Raker_Height_mm'])
            speed = float(row['Flow_Speed_mms'])
            efficiency = float(row['Filtration_Efficiency_Pct'])
            
            parsed_data[height][0].append(speed)
            parsed_data[height][1].append(efficiency)
            
    # Initialize a professional multi-curve plotting arena
    plt.figure(figsize=(10, 6))
    
    # Distinct scientific color palette for different geometries
    color_map = {
        2.0: "#e53e3e",  # Red for small, risky rakers
        4.0: "#ecc94b",  # Yellow for intermediate rakers
        6.0: "#48bb78",  # Green for reliable rakers
        8.0: "#2b6cb0"   # Blue for robust, full-size rakers
    }
    
    print("Processing geometric performance curves...")
    
    # Loop through each height dataset and plot its dynamic curve line
    for height in sorted(parsed_data.keys()):
        speeds, efficiencies = parsed_data[height]
        
        # Sort values by speed so lines trace perfectly left-to-right
        sorted_pairs = sorted(zip(speeds, efficiencies))
        sorted_speeds, sorted_efficiencies = zip(*sorted_pairs)
        
        current_color = color_map.get(height, "#4a5568")
        
        # Plot the main performance line
        plt.plot(
            sorted_speeds, sorted_efficiencies, 
            marker='o', markersize=6, linewidth=2.5, 
            color=current_color, label=f"Raker Height: {height:.1f} mm"
        )
        
    # Standard Scientific Presentation Labeling
    plt.axhline(y=100.0, color='#718096', linestyle=':', alpha=0.7, label="Ideal 100% Efficiency Target")
    
    plt.xlim(100, 650)
    plt.ylim(50, 105)
    
    plt.xlabel('Fluid Cross-Flow Velocity (mm/s)', fontsize=11, fontweight='bold')
    plt.ylabel('Filtration Efficiency Percentage (%)', fontsize=11, fontweight='bold')
    plt.title('Manta Matrix Parametric Optimization Sweep Curves', fontsize=12, fontweight='bold', pad=15)
    
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='lower right', fontsize=10, frameon=True, facecolor='#f7fafc')
    
    print("Rendering Optimization Curve Matrix Canvas...")
    plt.show()

if __name__ == "__main__":
    generate_performance_report()