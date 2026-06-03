import streamlit as st
import math
import random
import matplotlib.pyplot as plt
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# 1. GLOBAL WORKSPACE DESIGN & STYLING CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Manta CFD Web Workspace", 
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

# Enforce professional dark theme configurations for the canvas engine
plt.style.use('dark_background')

# Inject custom styling overrides to match premier dashboard UI standards
st.markdown("""
    <style>
    /* Styling adjustments for metric component readouts */
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #00f2fe; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.7px; color: #94a3b8; }
    div[data-testid="stMetricDelta"] { font-size: 0.85rem; }
    
    /* Clean adjustments for tab item headings */
    button[data-testid="stMarkdownContainer"] p { font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Initialize simulation telemetry data logger inside persistent session states
if "telemetry_log" not in st.session_state:
    st.session_state.telemetry_log = []

# -----------------------------------------------------------------------------
# 2. CONTROL ROOM PANEL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚙️ Simulation Control Panel")
st.sidebar.caption("Manipulate mechanical geometry, inflow dynamics, and pollutant configurations.")
st.sidebar.divider()

st.sidebar.markdown("**Structural Elements**")
raker_height = st.sidebar.slider("Raker Height (mm)", 0.0, 14.0, 8.0, step=0.1)

st.sidebar.markdown("**Fluid Dynamics**")
flow_speed_x = st.sidebar.slider("Flow Speed (mm/s)", 50, 800, 250, step=1)

st.sidebar.markdown("**Contamination Factors**")
particle_count = st.sidebar.slider("Debris Load (PPM / Count)", 10, 100, 40, step=1)

st.sidebar.divider()
st.sidebar.markdown("**Environmental Stress Testing**")
storm_mode = st.sidebar.toggle("Activate Storm Surge Mode", value=False, help="Injects dynamic chaotic velocity tensors across coordinate grids.")

st.sidebar.divider()
st.sidebar.markdown("**🧬 Active Polymer Injection Profiles**")
st.sidebar.caption("Toggle specific microplastic targets to run tracking array passes.")

# Environment Baselines
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

active_polymers = {}
for key, poly in polymer_profiles.items():
    active_polymers[key] = st.sidebar.checkbox(poly["name"].split(" (")[0], value=True)

available_keys = [k for k, active in active_polymers.items() if active]

# -----------------------------------------------------------------------------
# 3. HEADER & CORE ONBOARDING SYSTEM
# -----------------------------------------------------------------------------
st.title("🌌 Manta Ray Bio-Inspired Filtration Platform")
st.caption("High-Fidelity Computational Fluid Dynamics (CFD) Kinematics Tracking Workspace")

st.info(
    "💡 **Quick Start Workspace Guide:** This engine models non-clogging vortical separation "
    "mechanics derived from biological manta ray gill rakers. Alter configurations in the left control console to modify boundary layers, "
    "manipulate continuous flux properties, and track how different polymer masses react to shearing fluid currents."
)
st.divider()

# Verify operational requirements before executing simulation loop
if not available_keys:
    st.error("🚨 SYSTEM STATUS: PAUSED — Please check at least one polymer in the console sidebar to re-initialize injection fluid.")
else:
    # -----------------------------------------------------------------------------
    # 4. CORE KINEMATIC RESOLUTION LOOP (PHYSICS CALCULATION PROCESSING)
    # -----------------------------------------------------------------------------
    random.seed(105 if storm_mode else 101)
    captured_count = 0
    
    # Structural layout canvas setup matching parent dashboard color tone
    fig, ax = plt.subplots(figsize=(12, 5), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')
    
    ceiling_line = ax.axhline(y=channel_height, color='#3182ce', linestyle='--', linewidth=1.5, alpha=0.6, label="Upper Channel Boundary")
    floor_line = ax.axhline(y=0, color='#e53e3e', linestyle='-', linewidth=2, alpha=0.5, label="Active Pore Filter Bed")
    
    # Generate background velocity tracking vector indicators
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
            ax.arrow(wx, wy, dx, dy, head_width=0.7, head_length=1.0, color='#93c5fd', alpha=0.20)

    # Render solid geometry patches for physical rakers
    for start_x in raker_start_positions:
        rx = [start_x, start_x + peak_offset, start_x + raker_width]
        ry = [0.0, raker_height, 0.0]
        ax.fill(rx, ry, color='#475569', edgecolor='#64748b', alpha=0.95)

    # Process kinematic trajectories for individual debris loads
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
            ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.6, linewidth=1.2)
        else:
            ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.4, linewidth=1.2, linestyle=':')

    # Volumetric Performance Metrics
    intake_area_cm2 = (channel_height * channel_depth) / 100.0
    speed_cm_s = flow_speed_x / 10.0
    q_intake_l_min = intake_area_cm2 * speed_cm_s * 0.06
    clogging_coefficient = 1.0 if raker_height >= 4.0 else (0.4 + 0.15 * raker_height)
    q_filtrate_l_min = q_intake_l_min * 0.45 * clogging_coefficient
    purity_index = (captured_count / particle_count) * 100
    escaped_count = particle_count - captured_count

    # -----------------------------------------------------------------------------
    # 5. HIGH LEVEL KPI ANALYTIC DISPLAY CARDS
    # -----------------------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Intake Flux Stream", f"{q_intake_l_min:.1f} L/min", delta="Main Current")
    col2.metric("Filtrate Bottom Discharge", f"{q_filtrate_l_min:.1f} L/min", delta="Output Continuum")
    col3.metric("Filtrate Purity Index", f"{purity_index:.1f}%", delta="Separation Performance")
    col4.metric("Pollutants Escaped", f"{escaped_count} Units", delta="Boundary Leakage", delta_color="inverse" if escaped_count > 0 else "normal")
    st.divider()

    # Append current state calculation outputs directly to tracking session logs
    timestamp_string = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.telemetry_log.append({
        "Timestamp": timestamp_string,
        "Flow Speed (mm/s)": flow_speed_x,
        "Raker Geometry (mm)": raker_height,
        "Total Particles": particle_count,
        "Purity Index": f"{purity_index:.1f}%",
        "Regime": "Storm Critical" if storm_mode else "Steady State"
    })
    
    # Cap internal trace lengths to preserve system memory thresholds
    if len(st.session_state.telemetry_log) > 25:
        st.session_state.telemetry_log.pop(0)

    # -----------------------------------------------------------------------------
    # 6. WORKSPACE INTERACTIVE VIEWPORTS (TABS SYSTEM)
    # -----------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Live Fluid Kinematics Field", "📂 Parametric Telemetry Log", "🔬 Mathematical Physics Framework"])
    
    with tab1:
        st.subheader("Dynamic Boundary Layer Vector Displacement Map")
        st.caption("Visualizing particle shear vector reflections across bio-inspired geometries.")
        
        # Plot Canvas Design Styling Elements
        ax.set_xlim(-2, channel_length + 2)
        ax.set_ylim(-2, channel_height + 2)
        ax.set_xlabel("Horizontal Flow Displacement Axis (x - mm)", color="#94a3b8", fontsize=10)
        ax.set_ylabel("Filter Pore Clearance Axis (y - mm)", color="#94a3b8", fontsize=10)
        ax.tick_params(colors='#94a3b8', labelsize=9)
        ax.grid(True, linestyle=':', alpha=0.15, color="#cbd5e1")
        
        # Output matplotlib engine rendering layout inside tab
        st.pyplot(fig)
        
    with tab2:
        st.subheader("Persistent Simulation Logs")
        st.caption("Active monitoring system history documenting data outputs across past setting changes.")
        
        if st.session_state.telemetry_log:
            df_history = pd.DataFrame(st.session_state.telemetry_log[::-1])
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        else:
            st.info("Awaiting simulation initialization pass to trace runtime values.")
            
    with tab3:
        st.subheader("System Modeling Formulations")
        st.caption("Theoretical framework parameters used to resolve particle fluid kinematics arrays inside the workspace engine.")
        
        st.markdown(
            """
            This simulator utilizes discrete mathematical equations to monitor transport characteristics across continuous boundary limits. 
            The system volumetric flow parameters are computed through cross-sectional area and vector translations:
            
            $$Q_{intake} = A_{channel} \cdot v_{flow}$$
            
            Where:
            * $Q_{intake}$ is the Volume Flow Rate Profile ($L/min$).
            * $A_{channel}$ is the Transverse Area Vector Cross Section ($mm^2$).
            * $v_{flow}$ is the Input Velocity Vector Magnitude ($mm/s$).
            
            Individual particle trajectories are calculated at each sub-step through a balance of buoyancy and drag force profiles acting on localized masses:
            
            $$a_{buoyancy} = \left(\\frac{\\rho_{polymer} - \\rho_{fluid}}{\\rho_{polymer}}\\right) \cdot g$$
            
            $$F_{drag} = -\\frac{1}{2} C_d \cdot \\rho_{fluid} \cdot A_{cross} \cdot v_{relative} \cdot |v_{relative}|$$
            
            When particles encounter the geometric slopes representing the manta ray gill rakers, reflection algorithms invert vertical acceleration layers to simulate cross-flow shear interactions, creating non-clogging separation zones without physical entrapment.
            """
        )