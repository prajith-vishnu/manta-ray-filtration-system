import streamlit as st
import math
import random
import matplotlib.pyplot as plt

# Enforce dark theme environment parameters for Web Canvas rendering
plt.style.use('dark_background')

st.set_page_config(page_title="Manta CFD Web Workspace", layout="wide")

st.title("🌌 Manta Advanced CFD Real-Time Analytics Dashboard")
st.markdown("Automated Bio-Inspired Microplastic Filtration Fluid Dynamics Workspace")

# --- Environment Baselines ---
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
    "PP":   {"name": "Polypropylene (PP)",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#63b3ed"},
    "LDPE": {"name": "Low-Density Poly (LDPE)",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#68d391"},
    "PS":   {"name": "Polystyrene (PS)",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#f6e05e"},
    "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#f687b3"},
    "PVC":  {"name": "Polyvinyl Chloride (PVC)", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#fc8181"}
}

# --- Sidebar Instrument Control Panel ---
st.sidebar.header("🎛️ Control Room Console")

raker_height = st.sidebar.slider("Raker Height (mm)", 0.0, 14.0, 8.0, step=0.1)
flow_speed_x = st.sidebar.slider("Flow Speed (mm/s)", 50, 800, 250, step=1)
particle_count = st.sidebar.slider("Debris Load (PPM)", 10, 100, 40, step=1)

st.sidebar.subheader("🌪️ Environmental Hazards")
storm_mode = st.sidebar.toggle("Activate Storm Surge Mode", value=False)

st.sidebar.subheader("🧬 Active Polymer Injection")
active_polymers = {}
for key, poly in polymer_profiles.items():
    active_polymers[key] = st.sidebar.checkbox(poly["name"].split(" (")[0], value=True)

available_keys = [k for k, active in active_polymers.items() if active]

if not available_keys:
    st.error("🚨 SYSTEM STATUS: PAUSED — Select at least one polymer from console to inject.")
else:
    # --- Kinematic Tracking Core ---
    random.seed(105 if storm_mode else 101)
    captured_count = 0
    
    fig, ax = plt.subplots(figsize=(11, 5), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')
    
    ceiling_line = ax.axhline(y=channel_height, color='#3182ce', linestyle='--', linewidth=2)
    floor_line = ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2)
    
    # 1. Background vector field arrows
    grid_res_x, grid_res_y = 24, 12
    x_space = [i * (channel_length / (grid_res_x - 1)) for i in range(grid_res_x)]
    y_space = [i * (channel_height / (grid_res_y - 1)) for i in range(grid_res_y)]
    
    for wx in x_space[::2]:  
        for wy in y_space[::2]:
            local_suction = v_suction * (1.0 - (wy / channel_height))
            dx = flow_speed_x * 0.024
            dy = local_suction * 0.05
            
            if storm_mode:
                dy += math.sin(wx * 0.15 + wy * 0.2) * 2.5
                dx += math.cos(wy * 0.4) * 1.0
                
            for start_x in raker_start_positions:
                if start_x <= wx <= start_x + raker_width and wy <= raker_height:
                    dy = raker_height * 0.5  
            ax.arrow(wx, wy, dx, dy, head_width=0.7, head_length=1.0, color='#93c5fd', alpha=0.25)

    # 2. Raker geometry patches
    for start_x in raker_start_positions:
        rx = [start_x, start_x + peak_offset, start_x + raker_width]
        ry = [0.0, raker_height, 0.0]
        ax.fill(rx, ry, color='#475569', edgecolor='#64748b', alpha=0.95)

    # 3. Particle resolution loop
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
                if storm_mode:
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
            ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5)
        else:
            ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.7, linewidth=1.5, linestyle=':')

    # 🌊 Volumetric Metric Calculations
    intake_area_cm2 = (channel_height * channel_depth) / 100.0
    speed_cm_s = flow_speed_x / 10.0
    q_intake_l_min = intake_area_cm2 * speed_cm_s * 0.06
    clogging_coefficient = 1.0 if raker_height >= 4.0 else (0.4 + 0.15 * raker_height)
    q_filtrate_l_min = q_intake_l_min * 0.45 * clogging_coefficient
    purity_index = (captured_count / particle_count) * 100
    escaped_count = particle_count - captured_count

    # Render Layout
    ax.set_xlim(-3, channel_length + 3)
    ax.set_ylim(-3, channel_height + 3)
    ax.grid(True, linestyle=':', alpha=0.1)
    
    # Render Streamlit Layout Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Intake Flux Stream", f"{q_intake_l_min:.1f} L/min")
    col2.metric("Filtrate Bottom Discharge", f"{q_filtrate_l_min:.1f} L/min")
    col3.metric("Filtrate Purity Index", f"{purity_index:.1f}%")
    col4.metric("Pollutants Escaped", f"{escaped_count} Units")
    
    # Blit the Matplotlib figure canvas right into the web layout container
    st.pyplot(fig)