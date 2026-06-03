import math
import random
import matplotlib.pyplot as plt

def run_polymer_simulation():
    print("====================================================")
    print("RUNNING: Phase 6 Polymer Diversity & Drag Engine")
    print("====================================================")
    
    # Environment Constants
    channel_length = 100.0
    channel_height = 50.0
    flow_speed_x = 250.0
    time_step = 0.01
    
    rho_fluid = 1.025e-3  # Seawater density: 1.025 g/cm^3 mapped to g/mm^3
    g = 9810.0            # Gravity: 9810 mm/s^2
    v_suction = -60.0     # Downward water suction velocity (mm/s)
    C_d = 0.47            # Drag coefficient for a spherical particle
    
    # Raker Matrix Defs
    raker_start_positions = [20.0, 35.0, 50.0, 65.0, 80.0]
    raker_height = 8.0
    raker_width = 8.0        
    peak_offset = 6.0        
    
    # Polymer Database Dictionary (Density in g/mm^3, Size range in mm)
    polymer_profiles = {
        "PP":   {"name": "Polypropylene (PP)",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#4299e1"},
        "LDPE": {"name": "Low-Density Poly (LDPE)",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#48bb78"},
        "PS":   {"name": "Polystyrene (PS)",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#ecc94b"},
        "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#ed64a6"},
        "PVC":  {"name": "Polyvinyl Chloride (PVC)", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#e53e3e"}
    }
    
    total_particles = 60
    stats = {key: {"tested": 0, "captured": 0} for key in polymer_profiles.keys()}
    
    plt.figure(figsize=(12, 6.5))
    random.seed(101)  # Anchored seed for experimental tracking
    
    print(f"Injecting mixed polymer stream ({total_particles} particles)...")
    
    for p_id in range(total_particles):
        # Pick a random polymer type from our material database
        poly_key = random.choice(list(polymer_profiles.keys()))
        poly = polymer_profiles[poly_key]
        
        # Calculate individual physical characteristics
        radius = random.uniform(poly["size_range"][0], poly["size_range"][1]) / 2.0
        volume = (4.0 / 3.0) * math.pi * (radius ** 3)
        mass = poly["density"] * volume
        cross_area = math.pi * (radius ** 2)
        
        # Compute constant buoyancy/gravitational baseline acceleration component
        a_buoy = ((poly["density"] - rho_fluid) / poly["density"]) * g
        
        # Dispersion mechanics across input channel mouth
        particle_x = 0.0
        particle_y = 5.0 + random.uniform(0.0, 40.0)
        velocity_y = 0.0
        elapsed_time = 0.0
        
        x_paths = [particle_x]
        y_paths = [particle_y]
        status = "TRACKING"
        
        while particle_x < channel_length:
            sub_steps = 10
            dt = time_step / sub_steps
            
            for _ in range(sub_steps):
                particle_x += flow_speed_x * dt
                
                # Dynamic Fluid Drag Equation (competing with buoyancy/suction)
                relative_v_y = velocity_y - v_suction
                drag_force = -0.5 * C_d * rho_fluid * cross_area * relative_v_y * abs(relative_v_y)
                a_drag = drag_force / mass
                
                # Net total kinematics resolution
                wobble = math.sin(elapsed_time * 25 + p_id) * 0.2
                total_a_y = a_buoy + a_drag
                
                velocity_y += total_a_y * dt
                particle_y += (velocity_y * dt) + (wobble / sub_steps)
                
                # Boundary Raker Structural Collision Matrix
                for start_x in raker_start_positions:
                    peak_x = start_x + peak_offset
                    end_x = start_x + raker_width
                    current_wall_height = 0.0
                    
                    if start_x <= particle_x <= peak_x:
                        current_wall_height = (raker_height / peak_offset) * (particle_x - start_x)
                    elif peak_x < particle_x <= end_x:
                        current_wall_height = raker_height - ((raker_height / (raker_width - peak_offset)) * (particle_x - peak_x))
                        
                    if start_x <= particle_x <= end_x and particle_y <= current_wall_height:
                        velocity_y = abs(velocity_y) * 0.8 + 150.0  # Elastic momentum ricochet bounce
                        particle_y = current_wall_height + 0.1
            
            if particle_y > channel_height:
                particle_y = channel_height
                velocity_y = -velocity_y * 0.2
            elif particle_y <= 0.0:
                particle_y = 0.0
                status = "ESCAPED"
                break
                
            x_paths.append(particle_x)
            y_paths.append(particle_y)
            elapsed_time += time_step
            
        # Log analytics criteria
        stats[poly_key]["tested"] += 1
        if status == "TRACKING":
            stats[poly_key]["captured"] += 1
            plt.plot(x_paths, y_paths, color=poly["color"], alpha=0.5, linewidth=1.5)
        else:
            plt.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5, linestyle=':')

    # Print out material-specific analytics metrics
    print("\n----------------------------------------------------")
    print("POLYMER MATERIAL EFFICIENCY BREAKDOWN:")
    print("----------------------------------------------------")
    grand_tested = 0
    grand_captured = 0
    
    for key, data in stats.items():
        grand_tested += data["tested"]
        grand_captured += data["captured"]
        pct = (data["captured"] / data["tested"] * 100) if data["tested"] > 0 else 0
        print(f"{polymer_profiles[key]['name']:<26} | Captured: {data['captured']}/{data['tested']} | Yield: {pct:.1f}%")
        
    global_yield = (grand_captured / grand_tested) * 100
    print(f"\nOVERALL SIMULATION CORE YIELD: {global_yield:.1f}%")
    print("----------------------------------------------------")
    
    # Plot Environment Layout Configurations
    plt.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Enclosure Ceiling')
    plt.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Suction Pores Bed')
    
    for start_x in raker_start_positions:
        rx = [start_x, start_x + peak_offset, start_x + raker_width]
        ry = [0.0, raker_height, 0.0]
        plt.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9)
    
    # Dynamic Legend Generation maps directly to polymer matrix metrics
    for key, poly in polymer_profiles.items():
        plt.plot([], [], color=poly["color"], linewidth=2, label=f"{poly['name']}")
    plt.fill([], [], color='#4a5568', label="Bio-Inspired Gill Rakers")
    
    plt.xlim(-5, channel_length + 5)
    plt.ylim(-5, channel_height + 5)
    plt.xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
    plt.ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
    plt.title(f'Phase 6: Polymorphic Fluid Matrix Testing — Total System Yield: {global_yield:.1f}%', fontsize=12, fontweight='bold', pad=15)
    plt.grid(True, linestyle=':', alpha=0.4)
    plt.legend(loc='upper right', fontsize=9)
    plt.show()

if __name__ == "__main__":
    run_polymer_simulation()