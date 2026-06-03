import math
import time
import matplotlib.pyplot as plt

def run_visual_simulation():
    print("====================================================")
    print("RUNNING: Phase 4.1 True Geometric Ricochet Engine")
    print("====================================================")
    
    channel_length = 100.0
    channel_height = 50.0
    flow_speed_x = 250.0
    
    particle_x = 0.0
    particle_y = 8.5  
    velocity_y = 0.0 
    
    time_step = 0.01 
    elapsed_time = 0.0
    
    x_coordinates = [particle_x]
    y_coordinates = [particle_y]
    
    raker_start_positions = [20.0, 35.0, 50.0, 65.0, 80.0]
    raker_height = 8.0
    raker_width = 6.0
    
    # Calculate the peak X-coordinate for the slope equation
    raker_peak_offset = raker_width * 1.5 
    
    while particle_x < channel_length:
        particle_x += flow_speed_x * time_step
        
        velocity_y -= 1200.0 * time_step  
        wobble = math.sin(elapsed_time * 20) * 0.5
        
        particle_y += (velocity_y * time_step) + wobble
        
        # 3. TRUE GEOMETRIC COLLISION MATHEMATICS
        for start_x in raker_start_positions:
            peak_x = start_x + raker_peak_offset
            
            # Check if the particle is currently over the slanted leading edge
            if start_x <= particle_x <= peak_x:
                
                # Calculate the exact height of the slanted wall at this specific X coordinate
                slope = raker_height / raker_peak_offset
                wall_height_at_x = slope * (particle_x - start_x)
                
                # Did the particle physically touch the slanted slope?
                if particle_y <= wall_height_at_x:
                    velocity_y = 200.0  # Upward ricochet vector
                    particle_y = wall_height_at_x + 0.5  # Bump to prevent glitching inside the wall
                    print(f"[{elapsed_time:.2f}s] RICOCHET at X: {particle_x:.1f}mm | Wall Height: {wall_height_at_x:.1f}mm")
        
        if particle_y > channel_height:
            particle_y = channel_height
            velocity_y = -velocity_y * 0.5  
        elif particle_y < 0.0:
            particle_y = 0.0
            velocity_y = 0.0  
            
        x_coordinates.append(particle_x)
        y_coordinates.append(particle_y)
        elapsed_time += time_step
        
    print("Kinematics Calculated. Processing 2D Visual Map...")
    
    plt.figure(figsize=(10, 5))
    plt.plot(x_coordinates, y_coordinates, color='#e53e3e', marker='.', linestyle='-', linewidth=2, label='Microplastic Ricochet Path')
    
    plt.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Channel Ceiling (50mm)')
    plt.axhline(y=0, color='#2b6cb0', linestyle='--', linewidth=2, label='Channel Floor (0mm)')
    
    for i, start_x in enumerate(raker_start_positions):
        rx = [start_x, start_x + raker_peak_offset, start_x + raker_width]
        ry = [0.0, raker_height, 0.0]
        label_text = "Bio-Inspired Gill Rakers" if i == 0 else ""
        plt.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9, label=label_text)
    
    plt.xlim(-5, channel_length + 5)
    plt.ylim(-5, channel_height + 5)
    plt.xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
    plt.ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
    plt.title('Phase 4.1: True Geometric Manta Ray Ricochet Separation', fontsize=13, fontweight='bold', pad=15)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left')
    
    print("Visual Structural Layout Generated. Opening Window...")
    plt.show()

if __name__ == "__main__":
    run_visual_simulation()