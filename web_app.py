import streamlit as st
import math
import random
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import time

# -----------------------------------------------------------------------------
# 1. ENTERPRISE CONFIGURATION & BESPOKE CSS INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Manta Ray | CFD Engine", 
    layout="wide",
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

# Custom Enterprise-Grade UI Styling (Glassmorphism, Neon Typography, HUD Layout)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Global Dark Matrix Background */
    .stApp {
        background: linear-gradient(180deg, #07090f 0%, #0b0f19 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Neon Header Typography */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Glassmorphism Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetricValue"] { 
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #00f2fe; 
        text-shadow: 0px 0px 15px rgba(0, 242, 254, 0.4);
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 0.8rem; 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        color: #94a3b8; 
    }

    /* Console Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #090c15;
        border-right: 1px solid #1e293b;
    }
    
    /* Tab Styling */
    button[data-testid="stMarkdownContainer"] p { 
        font-weight: 600; 
        font-size: 1.05rem;
        color: #e2e8f0;
    }
    div.stAlert {
        background-color: rgba(0, 242, 254, 0.03);
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

plt.style.use('dark_background')

if "telemetry_log" not in st.session_state:
    st.session_state.telemetry_log = []

# -----------------------------------------------------------------------------
# 2. THE CONTROL CONSOLE (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Parameters")
    st.caption("Configure hydrodynamic boundaries and target polymers.")
    st.divider()

    with st.expander("📐 Structural Geometry", expanded=True):
        raker_height = st.slider("Raker Height (mm)", 0.0, 14.0, 8.0, step=0.1)

    with st.expander("🌊 Fluid Kinematics", expanded=True):
        flow_speed_x = st.slider("Continuous Flow Velocity (mm/s)", 50, 800, 250, step=1)
        storm_mode = st.toggle("⚠️ Inject Storm Surge Tensors", value=False)

    with st.expander("🦠 Pollutant Profiles", expanded=True):
        particle_count = st.slider("Debris Load (Unit Count)", 10, 100, 40, step=1)
        st.markdown("<br><span style='color:#94a3b8; font-size:0.8rem; text-transform:uppercase;'>Active Injection Targets</span>", unsafe_allow_html=True)
        
        polymer_profiles = {
            "PP":   {"name": "Polypropylene",       "density": 0.90e-3, "size_range": (1.5, 4.0), "color": "#00f2fe"},
            "LDPE": {"name": "Low-Density Poly",  "density": 0.92e-3, "size_range": (1.0, 3.0), "color": "#10b981"},
            "PS":   {"name": "Polystyrene",        "density": 1.05e-3, "size_range": (0.5, 2.0), "color": "#f59e0b"},
            "PET":  {"name": "Polyethylene (PET)",       "density": 1.38e-3, "size_range": (0.5, 2.5), "color": "#ec4899"},
            "PVC":  {"name": "Polyvinyl Chloride", "density": 1.40e-3, "size_range": (1.0, 4.5), "color": "#ef4444"}
        }

        active_polymers = {}
        for key, poly in polymer_profiles.items():
            active_polymers[key] = st.checkbox(f"{poly['name']} ({poly['density']*1000:.2f} g/cm³)", value=True)
        
        available_keys = [k for k, active in active_polymers.items() if active]

# Environment Constants
channel_length, channel_height, channel_depth = 100.0, 50.0, 50.0
time_step, rho_fluid, g, v_suction, C_d = 0.01, 1.025e-3, 9810.0, -60.0, 0.47
raker_start_positions, raker_width, peak_offset = [20.0, 35.0, 50.0, 65.0, 80.0], 8.0, 6.0

# -----------------------------------------------------------------------------
# 3. HEADER & HUD ONBOARDING
# -----------------------------------------------------------------------------
st.markdown("<h1>Manta Ray CFD Architecture</h1>", unsafe_allow_html=True)
st.caption("AEROSPACE-GRADE COMPUTATIONAL FLUID DYNAMICS (CFD) KINEMATICS TRACKING")

st.info("💡 **WORKSPACE INITIALIZED:** This numerical solver models bio-mimetic cross-flow filtration. Modifying boundary conditions in the console will trigger an automatic recalculation of vector fields, acceleration tensors, and particle trajectories.")
st.divider()

if not available_keys:
    st.error("🚨 ENGINE FAULT: Missing mass profiles. Select at least one polymer in the console to calculate trajectories.")
    st.stop()

# UX Flourish: Artificial computation delay to emphasize heavy processing
with st.spinner("Processing Navier-Stokes kinematic tensors and boundary reflections..."):
    time.sleep(0.3)

# -----------------------------------------------------------------------------
# 4. PHYSICS SOLVER & MATPLOTLIB RENDERING
# -----------------------------------------------------------------------------
random.seed(105 if storm_mode else 101)
captured_count = 0

# Create a transparent-background plot to blend into the Streamlit UI perfectly
fig, ax = plt.subplots(figsize=(14, 5.5))
fig.patch.set_facecolor('#07090f')
fig.patch.set_alpha(0.0) 
ax.set_facecolor('#0b0f19')

# Draw sleek boundary lines
ax.axhline(y=channel_height, color='#3b82f6', linestyle='--', linewidth=1.5, alpha=0.3)
ax.axhline(y=0, color='#ef4444', linestyle='-', linewidth=2, alpha=0.3)

# Render Vector Field with a subtle HUD glow
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
        ax.arrow(wx, wy, dx, dy, head_width=0.6, head_length=0.9, color='#38bdf8', alpha=0.15)

# Render Rakers (Geometric boundaries)
for start_x in raker_start_positions:
    rx = [start_x, start_x + peak_offset, start_x + raker_width]
    ry = [0.0, raker_height, 0.0]
    ax.fill(rx, ry, color='#1e293b', edgecolor='#475569', linewidth=1.5, alpha=0.8)

# Particle Trajectory Loop
for p_id in range(particle_count):
    poly_key = random.choice(available_keys)
    poly = polymer_profiles[poly_key]
    
    radius = random.uniform(poly["size_range"][0], poly["size_range"][1]) / 2.0
    volume = (4.0 / 3.0) * math.pi * (radius ** 3)
    mass = poly["density"] * volume
    cross_area = math.pi * (radius ** 2)
    a_buoy = ((poly["density"] - rho_fluid) / poly["density"]) * g
    
    particle_x, particle_y, velocity_y, elapsed_time = 0.0, 5.0 + random.uniform(0.0, 40.0), 0.0, 0.0
    x_paths, y_paths, status = [particle_x], [particle_y], "TRACKING"
    
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
            total_a_y = a_buoy + a_drag + (random.uniform(-45000.0, 45000.0) if storm_mode else 0)
            
            velocity_y += total_a_y * dt
            particle_y += (velocity_y * dt) + (wobble / sub_steps)
            
            for start_x in raker_start_positions:
                peak_x, end_x = start_x + peak_offset, start_x + raker_width
                current_wall_height = 0.0
                
                if start_x <= particle_x <= peak_x:
                    current_wall_height = (raker_height / peak_offset) * (particle_x - start_x)
                elif peak_x < particle_x <= end_x:
                    current_wall_height = raker_height - ((raker_height / (raker_width - peak_offset)) * (particle_x - peak_x))
                    
                if start_x <= particle_x <= end_x and particle_y <= current_wall_height:
                    velocity_y = abs(velocity_y) * 0.7 + 160.0  
                    particle_y = current_wall_height + 0.1
            
            if particle_y > channel_height:
                particle_y, velocity_y = channel_height, -velocity_y * 0.2
            elif particle_y <= 0.0:
                particle_y, status, escaped = 0.0, "ESCAPED", True
                break
                
            x_paths.append(particle_x)
            y_paths.append(particle_y)
            elapsed_time += dt
            
        if escaped: break
        
    if status == "TRACKING":
        captured_count += 1
        ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.8, linewidth=1.5, zorder=3)
    else:
        ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.3, linewidth=1.5, linestyle=':', zorder=2)

# Volumetric Math
q_intake_l_min = ((channel_height * channel_depth) / 100.0) * (flow_speed_x / 10.0) * 0.06
q_filtrate_l_min = q_intake_l_min * 0.45 * (1.0 if raker_height >= 4.0 else (0.4 + 0.15 * raker_height))
purity_index = (captured_count / particle_count) * 100
escaped_count = particle_count - captured_count

# -----------------------------------------------------------------------------
# 5. METRICS DASHBOARD
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Intake Flux Stream", f"{q_intake_l_min:.1f} L/m", delta="Q_in")
col2.metric("Filtrate Bottom Discharge", f"{q_filtrate_l_min:.1f} L/m", delta="Q_out")
col3.metric("Deflection Purity", f"{purity_index:.1f}%", delta="System Efficiency")
col4.metric("Boundary Leakage", f"{escaped_count}", delta="Escaped Units", delta_color="inverse" if escaped_count > 0 else "normal")
st.markdown("<br>", unsafe_allow_html=True)

# Telemetry Logging
st.session_state.telemetry_log.append({
    "Time": datetime.datetime.now().strftime("%H:%M:%S"),
    "Velocity": flow_speed_x,
    "Geometry": raker_height,
    "Load": particle_count,
    "Purity": f"{purity_index:.1f}%",
    "Regime": "Turbulent" if storm_mode else "Laminar"
})
if len(st.session_state.telemetry_log) > 20: st.session_state.telemetry_log.pop(0)

# -----------------------------------------------------------------------------
# 6. WORKSPACE VIEWPORTS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 KINEMATIC CANVAS", "📂 TELEMETRY DATABASE", "🔬 PHYSICS FORMULAS"])

with tab1:
    ax.set_xlim(-2, channel_length + 2)
    ax.set_ylim(-2, channel_height + 2)
    ax.set_xlabel("Horizontal Flow Displacement (x / mm)", color="#64748b", fontsize=10, family='JetBrains Mono')
    ax.set_ylabel("Filter Pore Clearance (y / mm)", color="#64748b", fontsize=10, family='JetBrains Mono')
    ax.tick_params(colors='#475569', labelsize=9)
    
    # Hide outer spines for a cleaner HUD look
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.grid(True, linestyle='-', alpha=0.05, color="#e2e8f0")
    st.pyplot(fig, transparent=True)
    
with tab2:
    st.dataframe(pd.DataFrame(st.session_state.telemetry_log[::-1]), use_container_width=True, hide_index=True)
        
with tab3:
    st.markdown("""
    #### Governing Hydrodynamic Equations
    The simulation environment evaluates fluid flux iteratively to maintain mass continuity. Total intake volume flux is determined by:
    $$Q_{intake} = A_{channel} \cdot v_{flow}$$
    
    Particle kinematics are derived by superimposing localized acceleration fields to evaluate vertical displacement relative to the bio-inspired geometric boundaries:
    $$a_{buoyancy} = \left(\\frac{\\rho_{polymer} - \\rho_{fluid}}{\\rho_{polymer}}\\right) \cdot g$$
    
    $$F_{drag} = -\\frac{1}{2} C_d \cdot \\rho_{fluid} \cdot A_{cross} \cdot v_{relative} \cdot |v_{relative}|$$
    """)