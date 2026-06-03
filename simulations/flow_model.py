import math
import random
import matplotlib.pyplot as plt

def run_multi_particle_simulation():
    print("====================================================")
    print("RUNNING: High-Fidelity Sub-Stepping Physics Engine")
    print("====================================================")
    
    # Macro Channel Enclosure Parameters
    channel_length = 100.0
    channel_height = 50.0
    flow_speed_x = 250.0
    time_step = 0.01  # Macro frame rate update interval
    
    # Redefined Clean Downstream-Slanted Fin Geometry
    raker_start_positions = [20.0, 35.0, 50.0, 65.0, 80.0]
    raker_height = 8.0
    raker_width = 8.0        # Total footprint base width (mm)
    peak_offset = 6.0        # Pushes peak 75% downstream for clean hydrodynamic slant
    
    total_particles = 50
    successful_captures = 0
    escaped_particles = 0
    
    plt.figure(figsize=(11, 6))
    random.seed(42)  # Maintain experimental reproducibility
    
    print(f"Processing vector fields for {total_particles} streams...")
    
    for p_id in range(total_particles):
        # Disperse starting elevations symmetrically along the intake mouth
        particle_x = 0.0
        particle_y = 5.0 + (p_id * (40.0 / total_particles)) + random.uniform(-0.5, 0.5)
        
        velocity_y = 0.0
        elapsed_time = 0.0
        
        x_paths = [particle_x]
        y_paths = [particle_y]
        status = "TRACKING"
        
        while particle_x < channel_length:
            # PHYSICS SUB-STEPPING ENGINE (Divides macro frames by 10 to halt tunneling)
            sub_steps = 10
            dt = time_step / sub_steps
            
            for _ in range(sub_steps):
                particle_x += flow_speed_x * dt
                
                # Apply localized downward suction component + vortex micro-vibration
                velocity_y -= 1200.0 * dt  
                wobble = math.sin(elapsed_time * 20 + p_id) * 0.4
                particle_y += (velocity_y * dt) + (wobble / sub_steps)
                
                # COMPREHENSIVE TWO-SLOPE COLLISION MATRIX
                for start_x in raker_start_positions:
                    peak_x = start_x + peak_offset
                    end_x = start_x + raker_width
                    
                    # Initializing dynamic baseline height variable
                    current_wall_height = 0.0
                    
                    # Slope Segment A: Long Gentle Leading Edge
                    if start_x <= particle_x <= peak_x:
                        slope_a = raker_height / peak_offset
                        current_wall_height = slope_a * (particle_x - start_x)
                    
                    # Slope Segment B: Sharp Steep Trailing Edge
                    elif peak_x < particle_x <= end_x:
                        slope_b = raker_height / (raker_width - peak_offset)
                        current_wall_height = raker_height - (slope_b * (particle_x - peak_x))
                    
                    # Execution of strict surface boundary collision constraint
                    if start_x <= particle_x <= end_x:
                        if particle_y <= current_wall_height:
                            # Elastic vector bounce response
                            velocity_y = 210.0  
                            particle_y = current_wall_height + 0.1  # Micro-displacement to clear skin surface
            
            # Global Container Constraints
            if particle_y > channel_height:
                particle_y = channel_height
                velocity_y = -velocity_y * 0.3
                
            elif particle_y <= 0.0:
                particle_y = 0.0
                status = "ESCAPED"
                break
                
            x_paths.append(particle_x)
            y_paths.append(particle_y)
            elapsed_time += time_step
            
        if status == "TRACKING":
            successful_captures += 1
            plt.plot(x_paths, y_paths, color='#319795', alpha=0.4, linewidth=1.5)
        else:
            escaped_particles += 1
            plt.plot(x_paths, y_paths, color='#dd6b20', alpha=0.6, linewidth=1.5, linestyle=':')

    efficiency_percentage = (successful_captures / total_particles) * 100
    
    print("\n----------------------------------------------------")
    print(f"HIGH-FIDELITY DIAGNOSTIC REPORT:")
    print(f"System Efficiency Yield: {efficiency_percentage:.1f}%")
    print("----------------------------------------------------")
    
    # Render Physical Enclosure Elements
    plt.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Filter Housing Ceiling')
    plt.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Porous Filter Floor (Suction Bed)')
    
    # Map Clean Continuous Slanted Fins to the Canvas Workspace
    for i, start_x in enumerate(raker_start_positions):
        rx = [start_x, start_x + peak_offset, start_x + raker_width]
        ry = [0.0, raker_height, 0.0]
        label_text = "Bio-Inspired Gill Rakers" if i == 0 else ""
        plt.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9, label=label_text)
    
    plt.plot([], [], color='#319795', linewidth=2, label=f'Captured Trajectories ({successful_captures})')
    plt.plot([], [], color='#dd6b20', linewidth=2, linestyle=':', label=f'Escaped Trajectories ({escaped_particles})')
    
    plt.xlim(-5, channel_length + 5)
    plt.ylim(-5, channel_height + 5)
    plt.xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
    plt.ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
    plt.title(f'Phase 5.1: High-Fidelity Multi-Particle Fluid Simulation Matrix', fontsize=12, fontweight='bold', pad=15)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='upper right')
    
    plt.show()

if __name__ == "__main__":
    run_multi_particle_simulation()