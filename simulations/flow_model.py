import math
import random
import matplotlib.pyplot as plt

def run_polymer_simulation(raker_height=8.0, flow_speed_x=250.0, total_particles=60, headless=False):
    """
    Advanced CFD Engine optimized for parametric sweeps.
    Accepts dynamic raker heights and water speeds.
    If headless=True, it skips plotting for lightning-fast data crunching.
    """
    if not headless:
        print("====================================================")
        print(f"RUNNING: CFD Engine | Height: {raker_height}mm | Speed: {flow_speed_x}mm/s")
        print("====================================================")
    
    # Environment Constants
    channel_length = 100.0
    channel_height = 50.0
    time_step = 0.01
    
    rho_fluid = 1.025e-3  # Seawater density (g/mm^3)
    g = 9810.0            # Gravity (mm/s^2)
    v_suction = -60.0     # Downward suction velocity (mm/s)
    C_d = 0.47            # Drag coefficient for spheres
    
    # Raker Matrix Configuration (Using the dynamic variables now!)
    raker_start_positions = [20.0, 35.0, 50.0, 65.0, 80.0]
    raker_width = 8.0        
    peak_offset = 6.0        
    
    polymer_profiles = {
        "PP":   {"name": "Polypropylene (PP)",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#4299e1"},
        "LDPE": {"name": "Low-Density Poly (LDPE)",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#48bb78"},
        "PS":   {"name": "Polystyrene (PS)",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#ecc94b"},
        "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#ed64a6"},
        "PVC":  {"name": "Polyvinyl Chloride (PVC)", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#e53e3e"}
    }
    
    stats = {key: {"tested": 0, "captured": 0} for key in polymer_profiles.keys()}
    
    # Setup plotting canvas only if not headless
    if not headless:
        fig, ax = plt.subplots(figsize=(12, 6.5))
    
    random.seed(101)
    
    # 🌊 WATER CURRENT BACKGROUND ENGINE (Calculated if not headless)
    if not headless:
        print("Generating background fluid vector fields (Water Currents)...")
        grid_res_x, grid_res_y = 40, 25
        x_space = [i * (channel_length / (grid_res_x - 1)) for i in range(grid_res_x)]
        y_space = [i * (channel_height / (grid_res_y - 1)) for i in range(grid_res_y)]
        
        for wx in x_space[::2]:  
            for wy in y_space[::2]:
                local_suction = v_suction * (1.0 - (wy / channel_height))
                dx, dy = 6.0, local_suction * 0.05
                for start_x in raker_start_positions:
                    if start_x <= wx <= start_x + raker_width and wy <= raker_height:
                        dy = raker_height * 0.5  
                ax.arrow(wx, wy, dx, dy, head_width=0.6, head_length=0.9, color='#bee3f8', alpha=0.35)

    if not headless:
        print(f"Simulating polymer physics trajectories...")
        
    for p_id in range(total_particles):
        poly_key = random.choice(list(polymer_profiles.keys()))
        poly = polymer_profiles[poly_key]
        
        radius = random.uniform(poly["size_range"][0], poly["size_range"][1]) / 2.0
        volume = (4.0 / 3.0) * math.pi * (radius ** 3)
        mass = poly["density"] * volume
        cross_area = math.pi * (radius ** 2)
        
        a_buoy = ((poly["density"] - rho_fluid) / poly["density"]) * g
        
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
                
                relative_v_y = velocity_y - v_suction
                drag_force = -0.5 * C_d * rho_fluid * cross_area * relative_v_y * abs(relative_v_y)
                a_drag = drag_force / mass
                
                wobble = math.sin(elapsed_time * 25 + p_id) * 0.2
                total_a_y = a_buoy + a_drag
                
                velocity_y += total_a_y * dt
                particle_y += (velocity_y * dt) + (wobble / sub_steps)
                
                for start_x in raker_start_positions:
                    peak_x = start_x + peak_offset
                    end_x = start_x + raker_width
                    current_wall_height = 0.0
                    
                    if start_x <= particle_x <= peak_x:
                        current_wall_height = (raker_height / peak_offset) * (particle_x - start_x)
                    elif peak_x < particle_x <= end_x:
                        current_wall_height = raker_height - ((raker_height / (raker_width - peak_offset)) * (particle_x - peak_x))
                        
                    if start_x <= particle_x <= end_x and particle_y <= current_wall_height:
                        velocity_y = abs(velocity_y) * 0.8 + 150.0  
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
            
        stats[poly_key]["tested"] += 1
        if status == "TRACKING":
            stats[poly_key]["captured"] += 1
            if not headless:
                ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.6, linewidth=1.5)
        else:
            if not headless:
                ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5, linestyle=':')

    grand_tested = sum(d["tested"] for d in stats.values())
    grand_captured = sum(d["captured"] for d in stats.values())
    global_yield = (grand_captured / grand_tested) * 100
    
    if not headless:
        print("\n----------------------------------------------------")
        print("POLYMER MATERIAL EFFICIENCY BREAKDOWN:")
        print("----------------------------------------------------")
        for key, data in stats.items():
            pct = (data["captured"] / data["tested"] * 100) if data["tested"] > 0 else 0
            print(f"{polymer_profiles[key]['name']:<26} | Captured: {data['captured']}/{data['tested']} | Yield: {pct:.1f}%")
        print(f"\nOVERALL SIMULATION CORE YIELD: {global_yield:.1f}%")
        print("----------------------------------------------------")
    
        # Plot Environment Accents
        ax.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Enclosure Ceiling')
        ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Suction Pores Bed')
        
        for start_x in raker_start_positions:
            rx = [start_x, start_x + peak_offset, start_x + raker_width]
            ry = [0.0, raker_height, 0.0]
            ax.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9)
        
        # Legend Maps
        ax.plot([], [], color='#bee3f8', alpha=0.7, linewidth=3, label="Water Vector Current")
        for key, poly in polymer_profiles.items():
            ax.plot([], [], color=poly["color"], linewidth=2, label=f"{poly['name']}")
        ax.fill([], [], color='#4a5568', label="Bio-Inspired Gill Rakers")
        
        ax.set_xlim(-5, channel_length + 5)
        ax.set_ylim(-5, channel_height + 5)
        ax.set_xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
        ax.set_title(f'Phase 6.1: Manta Ray CFD Engine — Yield: {global_yield:.1f}%', fontsize=12, fontweight='bold', pad=15)
        ax.grid(True, linestyle=':', alpha=0.3)
        ax.legend(loc='upper right', fontsize=9)
        plt.show()

    # CRITICAL: Return the yield percentage so our automated loop can save it!
    return global_yield

if __name__ == "__main__":
    # Default visual run if executed manually
    run_polymer_simulation(raker_height=8.0, flow_speed_x=250.0, total_particles=60, headless=False)