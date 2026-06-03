import math
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

def run_interactive_app():
    # --- Initial Environment Parameter Baselines ---
    init_height = 8.0
    init_speed = 250.0
    total_particles = 40  
    
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
        "PP":   {"name": "Polypropylene (PP)",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#4299e1", "active": True},
        "LDPE": {"name": "Low-Density Poly (LDPE)",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#48bb78", "active": True},
        "PS":   {"name": "Polystyrene (PS)",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#ecc94b", "active": True},
        "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#ed64a6", "active": True},
        "PVC":  {"name": "Polyvinyl Chloride (PVC)", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#e53e3e", "active": True}
    }

    # --- Application State Registry ---
    app_state = {"storm_mode": False}

    # --- Setup Window Layout Frame ---
    fig, ax = plt.subplots(figsize=(13, 8))
    plt.subplots_adjust(bottom=0.28, left=0.08, right=0.82)  
    
    ceiling_line = ax.axhline(y=channel_height, color='#2b6cb0', linestyle='--', linewidth=2, label='Enclosure Ceiling')
    floor_line = ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Suction Pores Bed')
    
    trajectory_lines = []
    raker_patches = []
    vector_arrows = []
    hud_boxes = []  

    def compute_and_render_physics(raker_height, flow_speed_x):
        # 1. Clear older frame assets cleanly
        for line in trajectory_lines:
            line.remove()
        trajectory_lines.clear()
        
        for patch in raker_patches:
            patch.remove()
        raker_patches.clear()
        
        for arrow in vector_arrows:
            arrow.remove()
        vector_arrows.clear()
        
        for box in hud_boxes:
            box.remove()
        hud_boxes.clear()
        
        # Locked seed maintains structural continuity across variable shifts, but shifts during storm mode
        random.seed(105 if app_state["storm_mode"] else 101)
        
        # 2. Redraw background current vectors (Warped dynamically if Storm Mode is active)
        grid_res_x, grid_res_y = 24, 12
        x_space = [i * (channel_length / (grid_res_x - 1)) for i in range(grid_res_x)]
        y_space = [i * (channel_height / (grid_res_y - 1)) for i in range(grid_res_y)]
        
        for wx in x_space[::2]:  
            for wy in y_space[::2]:
                local_suction = v_suction * (1.0 - (wy / channel_height))
                dx = flow_speed_x * 0.024
                dy = local_suction * 0.05
                
                # If storm mode is triggered, introduce sinusoidal fluid eddies
                if app_state["storm_mode"]:
                    dy += math.sin(wx * 0.15 + wy * 0.2) * 2.5
                    dx += math.cos(wy * 0.4) * 1.0
                    
                for start_x in raker_start_positions:
                    if start_x <= wx <= start_x + raker_width and wy <= raker_height:
                        dy = raker_height * 0.5  
                arr = ax.arrow(wx, wy, dx, dy, head_width=0.7, head_length=1.0, color='#bee3f8', alpha=0.3)
                vector_arrows.append(arr)

        # 3. Redraw raker structures
        for start_x in raker_start_positions:
            rx = [start_x, start_x + peak_offset, start_x + raker_width]
            ry = [0.0, raker_height, 0.0]
            poly_patch = ax.fill(rx, ry, color='#4a5568', edgecolor='#2d3748', alpha=0.9)[0]
            raker_patches.append(poly_patch)

        # 4. Filter out inactive polymers
        available_keys = [k for k, p in polymer_profiles.items() if p["active"]]
        
        if not available_keys:
            hud_panel = ax.text(
                1.5, 48.5, "SYSTEM PAUSED\n-------------------------\nSelect at least one polymer\nfrom the console to inject.", 
                fontsize=9, fontfamily='monospace', fontweight='bold', verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#fee2e2', edgecolor='#f87171', alpha=0.95)
            )
            hud_boxes.append(hud_panel)
            ax.set_title('Manta Computational Fluid Dynamics Workspace Dashboard', fontsize=12, fontweight='bold', pad=15)
            fig.canvas.draw_idle()
            return

        # 5. Run kinematic physics tracking loops
        captured_count = 0
        
        for p_id in range(total_particles):
            poly_key = random.choice(available_keys)
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
                    
                    # 🌪️ CRITICAL FLUID TURBULENCE INJECTION
                    if app_state["storm_mode"]:
                        # Introduces intense, high-frequency kinetic buffeting forces
                        total_a_y += random.uniform(-45000.0, 45000.0)
                    
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
                            # Bounce calculation handling
                            velocity_y = abs(velocity_y) * 0.7 + 160.0  
                            particle_y = current_wall_height + 0.1
                    
                    if particle_y > channel_height:
                        particle_y = channel_height
                        velocity_y = -velocity_y * 0.2
                    elif particle_y <= 0.0:
                        particle_y = 0.0
                        status = "ESCAPED"
                        escaped = True
                        break
                        
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
        
        # 📊 GENERATE CRITICAL TELEMETRY HUD DATA FRAME
        escaped_count = total_particles - captured_count
        flow_profile_string = "STORM SURGE [CRITICAL]" if app_state["storm_mode"] else "LAMINAR [STABLE]"
        
        if current_yield == 100.0:
            status_label = "[OK] OPTIMAL YIELD"
        elif current_yield >= 85.0:
            status_label = "[WARN] MINOR LEAKAGE"
        else:
            status_label = "[CRIT] SYSTEM FAILURE"
        
        hud_string = (
            f"SYSTEM CORE TELEMETRY\n"
            f"-------------------------\n"
            f"Flow Speed    : {flow_speed_x:.0f} mm/s\n"
            f"Raker Height  : {raker_height:.1f} mm\n"
            f"Flow Regime   : {flow_profile_string}\n"
            f"Stream Sample : {total_particles} units\n"
            f"Captured Core : {captured_count}\n"
            f"Escaped Waste : {escaped_count}\n"
            f"-------------------------\n"
            f"SYSTEM YIELD  : {current_yield:.1f}%\n"
            f"STATUS        : {status_label}"
        )
        
        box_face = "#fef2f2" if current_yield < 100.0 or app_state["storm_mode"] else "#f8fafc"
        box_edge = "#f87171" if current_yield < 100.0 or app_state["storm_mode"] else "#cbd5e0"
        
        hud_panel = ax.text(
            1.5, 48.5, hud_string, fontsize=9, fontfamily='monospace', fontweight='bold',
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.6', facecolor=box_face, edgecolor=box_edge, alpha=0.92)
        )
        hud_boxes.append(hud_panel)
        
        ax.set_title('Manta Computational Fluid Dynamics Workspace Dashboard', fontsize=12, fontweight='bold', pad=15)
        fig.canvas.draw_idle()

    # --- Generate Interactive UI Sliders ---
    ax_height_slider = plt.axes([0.18, 0.14, 0.55, 0.03], facecolor='#e2e8f0')
    ax_speed_slider = plt.axes([0.18, 0.08, 0.55, 0.03], facecolor='#e2e8f0')
    
    slider_height = Slider(ax_height_slider, 'Raker Height (mm)', 0.0, 14.0, valinit=init_height, valfmt='%1.1f mm', color='#4a5568')
    slider_speed = Slider(ax_speed_slider, 'Flow Speed (mm/s)', 50.0, 800.0, valinit=init_speed, valfmt='%1.0f mm/s', color='#2b6cb0')
    
    def on_slider_manipulation(val):
        compute_and_render_physics(slider_height.val, slider_speed.val)
        
    slider_height.on_changed(on_slider_manipulation)
    slider_speed.on_changed(on_slider_manipulation)
    
    # --- Generate Interactive Material Checkboxes (Right Console) ---
    ax_check_bounds = plt.axes([0.84, 0.38, 0.14, 0.25], facecolor='#f7fafc')
    poly_keys_list = list(polymer_profiles.keys())
    checkbox_labels = [polymer_profiles[k]["name"].split(" (")[0] for k in poly_keys_list]
    checkbox_actives = [polymer_profiles[k]["active"] for k in poly_keys_list]
    
    material_checkboxes = CheckButtons(ax_check_bounds, checkbox_labels, checkbox_actives)
    
    for i, key in enumerate(poly_keys_list):
        material_checkboxes.labels[i].set_color(polymer_profiles[key]["color"])
        material_checkboxes.labels[i].set_fontweight("bold")
        material_checkboxes.labels[i].set_fontsize(8)
    
    def on_checkbox_toggle(label):
        for key in polymer_profiles.keys():
            if polymer_profiles[key]["name"].startswith(label):
                polymer_profiles[key]["active"] = not polymer_profiles[key]["active"]
                break
        compute_and_render_physics(slider_height.val, slider_speed.val)
        
    material_checkboxes.on_clicked(on_checkbox_toggle)
    
    # --- Generate Interactive Reset UI Button ---
    ax_reset_btn = plt.axes([0.22, 0.02, 0.14, 0.04])
    reset_button = Button(ax_reset_btn, 'Reset Workspace', color='#cbd5e0', hovercolor='#a0aec0')
    
    def on_reset_click(event):
        app_state["storm_mode"] = False
        storm_button.color = '#feb2b2'
        storm_button.label.set_text('Trigger Storm Mode')
        slider_height.reset()
        slider_speed.reset()
        for i, key in enumerate(poly_keys_list):
            if not polymer_profiles[key]["active"]:
                material_checkboxes.set_active(i)
        
    reset_button.on_clicked(on_reset_click)

    # --- Generate Interactive Storm Mode Toggle Button ---
    ax_storm_btn = plt.axes([0.42, 0.02, 0.18, 0.04])
    storm_button = Button(ax_storm_btn, 'Trigger Storm Mode', color='#feb2b2', hovercolor='#fc8181')
    
    def on_storm_click(event):
        app_state["storm_mode"] = not app_state["storm_mode"]
        if app_state["storm_mode"]:
            storm_button.color = '#f56565'
            storm_button.label.set_text('Deactivate Storm Mode')
        else:
            storm_button.color = '#feb2b2'
            storm_button.label.set_text('Trigger Storm Mode')
        compute_and_render_physics(slider_height.val, slider_speed.val)
        
    storm_button.on_clicked(on_storm_click)

    # Compile layout parameters
    ax.set_xlim(-5, channel_length + 5)
    ax.set_ylim(-5, channel_height + 5)
    ax.set_xlabel('Filter Channel Length (mm)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Filter Channel Height (mm)', fontsize=11, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.3)
    
    for key, poly in polymer_profiles.items():
        ax.plot([], [], color=poly["color"], linewidth=2, label=poly["name"])
    ax.fill([], [], color='#4a5568', label="Bio-Inspired Gill Rakers")
    ax.legend(loc='upper right', fontsize=8)

    compute_and_render_physics(init_height, init_speed)
    plt.show()

if __name__ == "__main__":
    run_interactive_app()