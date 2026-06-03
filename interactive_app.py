import math
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

def run_interactive_app():
    # --- Initial Environment Parameter Baselines ---
    init_height = 8.0
    init_speed = 250.0
    total_particles = 40  # Optimized for real-time UI responsiveness
    
    channel_length = 100.0
    channel_height = 50.0
    time_step = 0.01
    
    rho_fluid = 1.025e-3  # Seawater density (g/mm^3)
    g = 9810.0            # Gravity (mm/s^2)
    v_suction = -60.0     # Downward suction velocity (mm/s)
    C_d = 0.47            # Drag coefficient
    
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

    # --- Setup Window Layout Frame ---
    fig, ax = plt.subplots(figsize=(12, 7.5))
    plt.subplots_adjust(bottom=0.28, left=0.1)  # Clean empty space at the bottom for UI controls
    
    # Anchor static plot elements
    ceiling_line = ax.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Enclosure Ceiling')
    floor_line = ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Suction Pores Bed')
    
    # Structure lists to hold line objects so we can wipe them cleanly during real-time slider shifts
    trajectory_lines = []
    raker_patches = []
    vector_arrows = []

    def compute_and_render_physics(raker_height, flow_speed_x):
        # 1. Clear out all older trajectory paths, rakers, and arrows from the canvas frame
        for line in trajectory_lines:
            line.remove()
        trajectory_lines.clear()
        
        for patch in raker_patches:
            patch.remove()
        raker_patches.clear()
        
        for arrow in vector_arrows:
            arrow.remove()
        vector_arrows.clear()
        
        # 2. Redraw the background fluid velocity arrows based on the new speed parameters
        grid_res_x, grid_res_y = 24, 12
        x_space = [i * (channel_length / (grid_res_x - 1)) for i in range(grid_res_x)]
        y_space = [i * (channel_height / (grid_res_y - 1)) for i in range(grid_res_y)]
        
        for wx in x_space[::2]:  
            for wy in y_space[::2]:
                local_suction = v_suction * (1.0 - (wy / channel_height))
                dx = flow_speed_x * 0.024
                dy = local_suction * 0.05
                for start_x in raker_start_positions:
                    if start_x <= wx <= start_x + raker_width and wy <= raker_height:
                        dy = raker_height * 0.5  
                arr = ax.arrow(wx, wy, dx, dy, head_width=0.7, head_length=1.0, color='#bee3f8', alpha=0.3)
                vector_arrows.append(arr)

        # 3. Redraw the bio-inspired gill rakers using the live slider height value
        for start_x in raker_start_positions:
            rx = [start_x, start_x + peak_offset, start_x + raker_width]
            ry = [0.0, raker_height, 0.0]
            poly_patch = ax.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9)[0]
            raker_patches.append(poly_patch)

        # 4. Run high-fidelity kinematic tracking loops for particle streams
        random.seed(101)  # Locked seed maintains structural continuity across variable shifts
        captured_count = 0
        
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
                sub_steps = 8
                dt = time_step / sub_steps
                escaped = False
                
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
                    
                    # Resolve boundary limits inside the micro-step loop
                    if particle_y > channel_height:
                        particle_y = channel_height
                        velocity_y = -velocity_y * 0.2
                    elif particle_y <= 0.0:
                        particle_y = 0.0
                        status = "ESCAPED"
                        escaped = True
                        break
                        
                    # Save precise sub-step positions to eliminate vector path clipping
                    x_paths.append(particle_x)
                    y_paths.append(particle_y)
                    elapsed_time += dt
                    
                if escaped:
                    break
                
            if status == "TRACKING":
                captured_count += 1
                line, = ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.6, linewidth=1.5)
            else:
                line, = ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.6, linewidth=1.5, linestyle=':')
            
            trajectory_lines.append(line)
            
        current_yield = (captured_count / total_particles) * 100
        ax.set_title(f'Manta Workspace UI App — Dynamic Live System Yield: {current_yield:.1f}%', fontsize=12, fontweight='bold', pad=15)
        fig.canvas.draw_idle()

    # --- Generate Interactive UI Sliders ---
    ax_height_slider = plt.axes([0.20, 0.14, 0.60, 0.03], facecolor='#e2e8f0')
    ax_speed_slider = plt.axes([0.20, 0.08, 0.60, 0.03], facecolor='#e2e8f0')
    
    slider_height = Slider(ax_height_slider, 'Raker Height (mm)', 0.0, 14.0, valinit=init_height, valfmt='%1.1f mm', color='#4a5568')
    slider_speed = Slider(ax_speed_slider, 'Flow Speed (mm/s)', 50.0, 800.0, valinit=init_speed, valfmt='%1.0f mm/s', color='#2b6cb0')
    
    # --- Event Handler Callback Trigger Engine ---
    def on_slider_manipulation(val):
        compute_and_render_physics(slider_height.val, slider_speed.val)
        
    slider_height.on_changed(on_slider_manipulation)
    slider_speed.on_changed(on_slider_manipulation)
    
    # --- Generate Interactive Reset UI Button ---
    ax_reset_btn = plt.axes([0.45, 0.02, 0.12, 0.04])
    reset_button = Button(ax_reset_btn, 'Reset Workspace', color='#cbd5e0', hovercolor='#a0aec0')
    
    def on_reset_click(event):
        slider_height.reset()
        slider_speed.reset()
        
    reset_button.on_clicked(on_reset_click)

    # Compile the layout viewport boundaries
    ax.set_xlim(-5, channel_length + 5)
    ax.set_ylim(-5, channel_height + 5)
    ax.set_xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.3)
    
    # Structural Legend Mapping
    for key, poly in polymer_profiles.items():
        ax.plot([], [], color=poly["color"], linewidth=2, label=poly["name"])
    ax.fill([], [], color='#4a5568', label="Bio-Inspired Gill Rakers")
    ax.legend(loc='upper right', fontsize=8)

    # Trigger Initial Launch Calculations
    compute_and_render_physics(init_height, init_speed)
    plt.show()

if __name__ == "__main__":
    run_interactive_app()