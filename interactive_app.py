import os
import csv
import math
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

# Set the dark theme environment before creating layout elements
plt.style.use('dark_background')

def run_interactive_app():
    # --- Initial Environment Parameter Baselines ---
    init_height = 8.0
    init_speed = 250.0
    init_particles = 40  # Controlled via slider now
    
    channel_length = 100.0  # mm
    channel_height = 50.0   # mm
    channel_depth = 50.0    # mm 
    time_step = 0.01
    
    rho_fluid = 1.025e-3  # Seawater density (g/mm^3)
    g = 9810.0            # Gravity (mm/s^2)
    v_suction = -60.0     # Downward suction velocity (mm/s)
    C_d = 0.47            # Drag coefficient
    
    raker_start_positions = [20.0, 35.0, 50.0, 65.0, 80.0]
    raker_width = 8.0        
    peak_offset = 6.0        
    
    polymer_profiles = {
        "PP":   {"name": "Polypropylene (PP)",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#63b3ed", "active": True},
        "LDPE": {"name": "Low-Density Poly (LDPE)",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#68d391", "active": True},
        "PS":   {"name": "Polystyrene (PS)",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#f6e05e", "active": True},
        "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#f687b3", "active": True},
        "PVC":  {"name": "Polyvinyl Chloride (PVC)", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#fc8181", "active": True}
    }

    # --- Persistent Application State Dictionary ---
    app_state = {
        "storm_mode": False,
        "current_yield": 100.0,
        "q_intake": 0.0,
        "q_filtrate": 0.0,
        "escaped_count": 0
    }

    # --- Setup Window Layout Frame ---
    fig, ax = plt.subplots(figsize=(13, 8.5), facecolor='#0f172a')
    ax.set_facecolor('#1e293b') 
    plt.subplots_adjust(bottom=0.34, left=0.08, right=0.82)  # Expanded bottom space for 3 sliders + button row
    
    ceiling_line = ax.axhline(y=channel_height, color='#3182ce', linestyle='--', linewidth=2, label='Enclosure Ceiling')
    floor_line = ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, label='Suction Pores Bed')
    
    trajectory_lines = []
    raker_patches = []
    vector_arrows = []
    hud_boxes = []  

    def compute_and_render_physics(raker_height, flow_speed_x, particle_count):
        particle_count = int(particle_count)
        
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
        
        # Revert export save button styling on slider updates
        export_button.color = '#334155'
        export_button.label.set_text('Export Diagnostics')
        
        random.seed(105 if app_state["storm_mode"] else 101)
        
        # 1. Redraw background current vectors
        grid_res_x, grid_res_y = 24, 12
        x_space = [i * (channel_length / (grid_res_x - 1)) for i in range(grid_res_x)]
        y_space = [i * (channel_height / (grid_res_y - 1)) for i in range(grid_res_y)]
        
        for wx in x_space[::2]:  
            for wy in y_space[::2]:
                local_suction = v_suction * (1.0 - (wy / channel_height))
                dx = flow_speed_x * 0.024
                dy = local_suction * 0.05
                
                if app_state["storm_mode"]:
                    dy += math.sin(wx * 0.15 + wy * 0.2) * 2.5
                    dx += math.cos(wy * 0.4) * 1.0
                    
                for start_x in raker_start_positions:
                    if start_x <= wx <= start_x + raker_width and wy <= raker_height:
                        dy = raker_height * 0.5  
                arr = ax.arrow(wx, wy, dx, dy, head_width=0.7, head_length=1.0, color='#93c5fd', alpha=0.25)
                vector_arrows.append(arr)

        # 2. Redraw raker structures
        for start_x in raker_start_positions:
            rx = [start_x, start_x + peak_offset, start_x + raker_width]
            ry = [0.0, raker_height, 0.0]
            poly_patch = ax.fill(rx, ry, color='#475569', edgecolor='#64748b', alpha=0.95)[0]
            raker_patches.append(poly_patch)

        available_keys = [k for k, p in polymer_profiles.items() if p["active"]]
        
        if not available_keys:
            hud_panel = ax.text(
                1.5, 48.5, "SYSTEM STATUS: PAUSED\n-------------------------\nSelect at least one polymer\nfrom console to inject.", 
                fontsize=9, fontfamily='monospace', fontweight='bold', color='#fca5a5', verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#7f1d1d', edgecolor='#f87171', alpha=0.95)
            )
            hud_boxes.append(hud_panel)
            ax.set_title('Manta Advanced CFD Real-Time Analytics Dashboard', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
            fig.canvas.draw_idle()
            return

        # 3. Run high-fidelity kinematics loop
        captured_count = 0
        
        for p_id in range(particle_count):
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
                    
                    if app_state["storm_mode"]:
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
                line, = ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5)
            else:
                line, = ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5, linestyle=':')
            
            trajectory_lines.append(line)
            
        current_yield = (captured_count / particle_count) * 100
        escaped_count = particle_count - captured_count
        
        # 🌊 4. FLUID DYNAMICS VOLUMETRIC METRICS PANEL
        intake_area_cm2 = (channel_height * channel_depth) / 100.0
        speed_cm_s = flow_speed_x / 10.0
        q_intake_l_min = intake_area_cm2 * speed_cm_s * 0.06
        
        clogging_coefficient = 1.0 if raker_height >= 4.0 else (0.4 + 0.15 * raker_height)
        q_filtrate_l_min = q_intake_l_min * 0.45 * clogging_coefficient

        # Cache variables to global state register for CSV exporter context mapping
        app_state["current_yield"] = current_yield
        app_state["q_intake"] = q_intake_l_min
        app_state["q_filtrate"] = q_filtrate_l_min
        app_state["escaped_count"] = escaped_count

        # 📊 RENDER INDUSTRIAL HUD PANEL
        flow_profile_string = "STORM CRISIS" if app_state["storm_mode"] else "LAMINAR STABLE"
        purity_index = current_yield 
        status_label = "[OK] PURITY NOMINAL" if purity_index == 100.0 else "[CRIT] FILTRATE POLLUTED"
        
        hud_string = (
            f" ⚡ FLUID CONTAMINATION SYSTEMS HUD\n"
            f" -------------------------------------\n"
            f" Flow Velocity Rate  : {flow_speed_x:.0f} mm/s\n"
            f" Gill Raker Profile   : {raker_height:.1f} mm\n"
            f" Flow Hydro-Regime   : {flow_profile_string}\n"
            f" -------------------------------------\n"
            f" Channel Intake Flux : {q_intake_l_min:.1f} L/min\n"
            f" Bottom Filtrate Flow: {q_filtrate_l_min:.1f} L/min\n"
            f" -------------------------------------\n"
            f" Injected Debris Load: {particle_count} Units\n"
            f" Deflected Retentate : {captured_count} Units\n"
            f" Filtrate Pollutants : {escaped_count} Units\n"
            f" -------------------------------------\n"
            f" FILTRATE PURITY INDEX: {purity_index:.1f}%\n"
            f" CONSOLE ALARM STATUS : {status_label}"
        )
        
        box_face = "#1e1b4b" if purity_index == 100.0 and not app_state["storm_mode"] else "#451a03" if purity_index >= 85.0 else "#7f1d1d"
        box_edge = "#3b82f6" if purity_index == 100.0 and not app_state["storm_mode"] else "#f59e0b" if purity_index >= 85.0 else "#ef4444"
        text_color = "#38bdf8" if purity_index == 100.0 and not app_state["storm_mode"] else "#fbbf24" if purity_index >= 85.0 else "#fca5a5"
        
        hud_panel = ax.text(
            1.5, 48.5, hud_string, fontsize=9, fontfamily='monospace', fontweight='bold', color=text_color,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.6', facecolor=box_face, edgecolor=box_edge, alpha=0.95)
        )
        hud_boxes.append(hud_panel)
        
        ax.set_title('Manta Advanced CFD Real-Time Analytics Dashboard', color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
        fig.canvas.draw_idle()

    # --- Generate Interactive UI Sliders ---
    ax_height_slider = plt.axes([0.18, 0.22, 0.55, 0.025], facecolor='#334155')
    ax_speed_slider = plt.axes([0.18, 0.16, 0.55, 0.025], facecolor='#334155')
    ax_load_slider = plt.axes([0.18, 0.10, 0.55, 0.025], facecolor='#334155')
    
    slider_height = Slider(ax_height_slider, 'Raker Height (mm)', 0.0, 14.0, valinit=init_height, valfmt='%1.1f mm', color='#64748b')
    slider_speed = Slider(ax_speed_slider, 'Flow Speed (mm/s)', 50.0, 800.0, valinit=init_speed, valfmt='%1.0f mm/s', color='#3b82f6')
    slider_particles = Slider(ax_load_slider, 'Debris Load (PPM)', 10.0, 100.0, valinit=init_particles, valfmt='%1.0f Units', color='#a855f7')
    
    def on_slider_manipulation(val):
        compute_and_render_physics(slider_height.val, slider_speed.val, slider_particles.val)
        
    slider_height.on_changed(on_slider_manipulation)
    slider_speed.on_changed(on_slider_manipulation)
    slider_particles.on_changed(on_slider_manipulation)
    
    # --- Generate Interactive Material Checkboxes (Right Console) ---
    ax_check_bounds = plt.axes([0.84, 0.38, 0.14, 0.25], facecolor='#1e293b')
    poly_keys_list = list(polymer_profiles.keys())
    checkbox_labels = [polymer_profiles[k]["name"].split(" (")[0] for k in poly_keys_list]
    checkbox_actives = [polymer_profiles[k]["active"] for k in poly_keys_list]
    
    num_polymers = len(poly_keys_list)
    
    material_checkboxes = CheckButtons(
        ax=ax_check_bounds, 
        labels=checkbox_labels, 
        actives=checkbox_actives,
        label_props={'color': ['#ffffff'] * num_polymers, 'fontweight': ['bold'] * num_polymers, 'fontsize': [9] * num_polymers},
        frame_props={'edgecolor': ['#94a3b8'] * num_polymers, 'facecolor': ['#334155'] * num_polymers, 'linewidth': [1.5] * num_polymers},
        check_props={'color': ['#ffffff'] * num_polymers, 'linewidth': [2.5] * num_polymers}
    )
    
    def on_checkbox_toggle(label):
        for key in polymer_profiles.keys():
            if polymer_profiles[key]["name"].startswith(label):
                polymer_profiles[key]["active"] = not polymer_profiles[key]["active"]
                break
        compute_and_render_physics(slider_height.val, slider_speed.val, slider_particles.val)
        
    material_checkboxes.on_clicked(on_checkbox_toggle)
    
    # --- Generate Interactive Reset UI Button ---
    ax_reset_btn = plt.axes([0.18, 0.02, 0.14, 0.04])
    reset_button = Button(ax_reset_btn, 'Reset Console', color='#334155', hovercolor='#475569')
    reset_button.label.set_color('#f8fafc')
    reset_button.label.set_fontweight('bold')
    
    def on_reset_click(event):
        app_state["storm_mode"] = False
        storm_button.color = '#7f1d1d'
        storm_button.label.set_text('Trigger Storm Mode')
        slider_height.reset()
        slider_speed.reset()
        slider_particles.reset()
        for i, key in enumerate(poly_keys_list):
            if not polymer_profiles[key]["active"]:
                material_checkboxes.set_active(i)
        
    reset_button.on_clicked(on_reset_click)

    # --- Generate Interactive Storm Mode Toggle Button ---
    ax_storm_btn = plt.axes([0.35, 0.02, 0.18, 0.04])
    storm_button = Button(ax_storm_btn, 'Trigger Storm Mode', color='#7f1d1d', hovercolor='#991b1b')
    storm_button.label.set_color('#fca5a5')
    storm_button.label.set_fontweight('bold')
    
    def on_storm_click(event):
        app_state["storm_mode"] = not app_state["storm_mode"]
        if app_state["storm_mode"]:
            storm_button.color = '#b91c1c'
            storm_button.label.set_text('Deactivate Storm Mode')
        else:
            storm_button.color = '#7f1d1d'
            storm_button.label.set_text('Trigger Storm Mode')
        compute_and_render_physics(slider_height.val, slider_speed.val, slider_particles.val)
        
    storm_button.on_clicked(on_storm_click)

    # --- Generate Interactive Diagnostics Exporter Button ---
    ax_export_btn = plt.axes([0.56, 0.02, 0.17, 0.04])
    export_button = Button(ax_export_btn, 'Export Diagnostics', color='#334155', hovercolor='#475569')
    export_button.label.set_color('#6ee7b7')  # Cool neon mint text color
    export_button.label.set_fontweight('bold')
    
    def on_export_click(event):
        csv_filename = "workspace_saves.csv"
        file_existed = os.path.isfile(csv_filename)
        
        with open(csv_filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_existed:
                # Build custom research headers dynamically
                writer.writerow([
                    "Raker Height (mm)", "Flow Velocity (mm/s)", "Debris Particle Count", 
                    "Hydro-Regime Mode", "Channel Intake Flux (L/min)", "Bottom Filtrate Flow (L/min)", 
                    "Filtrate Purity Index (%)", "Pollutant Leaks Caught"
                ])
            writer.writerow([
                f"{slider_height.val:.2f}",
                f"{slider_speed.val:.1f}",
                int(slider_particles.val),
                "STORM SURGE" if app_state["storm_mode"] else "LAMINAR STABLE",
                f"{app_state['q_intake']:.2f}",
                f"{app_state['q_filtrate']:.2f}",
                f"{app_state['current_yield']:.1f}",
                app_state["escaped_count"]
            ])
            
        export_button.color = '#065f46'  # Shift button color to deep success green
        export_button.label.set_text('Saved Row! [X]')
        print(f"[SUCCESS] Appended runtime snapshot coordinates to local file: '{csv_filename}'")
        fig.canvas.draw_idle()
        
    export_button.on_clicked(on_export_click)

    # Compile layout parameters
    ax.set_xlim(-5, channel_length + 5)
    ax.set_ylim(-5, channel_height + 5)
    ax.set_xlabel('Filter Channel Length (mm)', color='#cbd5e0', fontsize=11, fontweight='bold')
    ax.set_ylabel('Filter Channel Height (mm)', color='#cbd5e0', fontsize=11, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.15)
    
    for key, poly in polymer_profiles.items():
        ax.plot([], [], color=poly["color"], linewidth=2, label=poly["name"])
    ax.fill([], [], color='#475569', label="Bio-Inspired Gill Rakers")
    ax.legend(loc='upper right', fontsize=8, facecolor='#0f172a', edgecolor='#334155')

    compute_and_render_physics(init_height, init_speed, init_particles)
    plt.show()

if __name__ == "__main__":
    run_interactive_app()