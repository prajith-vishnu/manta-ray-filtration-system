import streamlit as st
import math
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & BESPOKE CSS INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Manta Ray | CFD Simulator",
    layout="wide",
    page_icon="🌊",
    initial_sidebar_state="expanded"
)

# Ocean Bioluminescence design system:
# bg #000a0e | cyan #00e5ff | green #00ff9d | orange #ff6b35 | muted #4a6fa5
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@500;700&display=swap');

    /* Deep ocean background */
    .stApp {
        background: #000a0e;
        font-family: 'Inter', sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #ffffff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000a0e;
        border-right: 1px solid rgba(0, 229, 255, 0.15);
    }
    [data-testid="stSidebar"] details {
        background: rgba(0, 20, 30, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 4px;
    }

    /* Tabs — monospace sensor-readout labels */
    button[data-baseweb="tab"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        letter-spacing: 2px;
        color: #4a6fa5;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #00e5ff;
    }
    [data-baseweb="tab-highlight"] {
        background-color: #00e5ff;
    }

    /* Alerts */
    div.stAlert {
        background-color: rgba(0, 20, 30, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 4px;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    </style>
""", unsafe_allow_html=True)


def render_metric(label, value, sublabel, color="#00e5ff"):
    st.markdown(f"""
    <div style='
        background: rgba(0, 20, 30, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-left: 3px solid {color};
        border-radius: 4px;
        padding: 1.25rem;
        margin: 0.25rem 0;
    '>
        <div style='
            font-family: JetBrains Mono;
            font-size: 0.65rem;
            color: #4a6fa5;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        '>{label}</div>
        <div style='
            font-family: JetBrains Mono;
            font-size: 1.8rem;
            font-weight: 700;
            color: {color};
            text-shadow: 0 0 20px {color}40;
        '>{value}</div>
        <div style='
            font-family: Inter;
            font-size: 0.75rem;
            color: #4a6fa5;
            margin-top: 0.25rem;
        '>{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)

plt.style.use('dark_background')

if "telemetry_log" not in st.session_state:
    st.session_state.telemetry_log = []
if "run_counter" not in st.session_state:
    st.session_state.run_counter = 0

# -----------------------------------------------------------------------------
# 2. THE CONTROL CONSOLE (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='
        font-family: JetBrains Mono;
        font-size: 0.7rem;
        color: #00e5ff;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(0,229,255,0.1);
        margin-bottom: 1rem;
    '>⬡ SIMULATION PARAMETERS</div>
    """, unsafe_allow_html=True)

    with st.expander("📐 Structural Geometry", expanded=True):
        raker_height = st.slider("Raker Height (mm)", 0.0, 14.0, 8.0, step=0.1)

    with st.expander("🌊 Fluid Kinematics", expanded=True):
        flow_speed_x = st.slider("Continuous Flow Velocity (mm/s)", 50, 800, 250, step=1)
        storm_mode = st.toggle("⚠️ Inject Storm Surge Tensors", value=False)

    with st.expander("🦠 Pollutant Profiles", expanded=True):
        particle_count = st.slider("Debris Load (Unit Count)", 10, 100, 40, step=1)
        st.markdown("<br><span style='color:#4a6fa5; font-size:0.8rem; letter-spacing:2px; text-transform:uppercase; font-family:JetBrains Mono;'>Active Injection Targets</span>", unsafe_allow_html=True)
        
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

    # Sidebar AI Declaration Anchor for Stardance Compliance
    st.divider()
    st.markdown("### 🤖 AI Declaration")
    st.caption(
        "Claude (Anthropic) was used as a coding assistant to implement the UI and optimize "
        "the simulation loops. Physics formulation and research direction by "
        "Prajith Vishnu Rajesh Kumar."
    )

# Environment Constants
channel_length, channel_height, channel_depth = 100.0, 50.0, 50.0
time_step, rho_fluid, g, v_suction, C_d = 0.01, 1.025e-3, 9810.0, -60.0, 0.47
raker_start_positions, raker_width, peak_offset = [20.0, 35.0, 50.0, 65.0, 80.0], 8.0, 6.0

# -----------------------------------------------------------------------------
# 3. HEADER & RESEARCH CONTEXT
# -----------------------------------------------------------------------------
st.markdown("""
<div style='padding: 2rem 0 1rem 0;'>
  <div style='font-family: JetBrains Mono;
              font-size: 0.75rem;
              color: #00e5ff;
              letter-spacing: 4px;
              text-transform: uppercase;
              margin-bottom: 0.5rem;'>
    FERROCLEAN RESEARCH SERIES — COMPUTATIONAL MODULE
  </div>
  <div style='font-family: Space Grotesk;
              font-size: 2.5rem;
              font-weight: 700;
              color: #ffffff;
              line-height: 1.1;'>
    Manta Ray<br>
    <span style='color: #00e5ff;'>CFD Simulator</span>
  </div>
  <div style='font-family: Inter;
              font-size: 0.9rem;
              color: #4a6fa5;
              margin-top: 0.75rem;
              max-width: 600px;'>
    Computational extension of the FerroClean
    microplastics research project. Modeling
    bio-inspired gill raker filtration geometry
    against real polymer bulk densities.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='
    background: rgba(0, 229, 255, 0.03);
    border: 1px solid rgba(0, 229, 255, 0.12);
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    font-family: Inter;
    font-size: 0.85rem;
    color: #4a6fa5;
    line-height: 1.6;
'>
    <span style='color: #00e5ff; font-family: JetBrains Mono;
                 font-size: 0.7rem; letter-spacing: 2px;'>
        RESEARCH CONTEXT
    </span><br><br>
    This simulator extends the
    <span style='color: #00ff9d;'>FerroClean</span>
    research project — which achieved up to
    <span style='color: #00ff9d;'>100% microplastic
    removal efficiency</span> via ferrofluid magnetic
    separation (UNT Science Fair, 2026, 3rd Place).
    While FerroClean uses chemical intervention,
    this model asks whether passive bio-inspired
    geometry alone can achieve comparable separation.
</div>
""", unsafe_allow_html=True)

st.info(
    "💡 Configure fluid parameters in the sidebar to simulate microplastic particle "
    "behavior through bio-inspired gill raker geometry."
)
st.divider()

if not available_keys:
    st.error("🚨 ENGINE FAULT: Missing mass profiles. Select at least one polymer in the console to calculate trajectories.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. PHYSICS SOLVER & MATPLOTLIB RENDERING
# -----------------------------------------------------------------------------
random.seed(105 if storm_mode else 101)
captured_count = 0

# Create a transparent-background plot to blend into the Streamlit UI perfectly
fig, ax = plt.subplots(figsize=(14, 5.5))
fig.patch.set_facecolor('#000a0e')
fig.patch.set_alpha(0.0)
ax.set_facecolor('#000a0e')

# Water depth gradient — darker at the bottom, slightly lighter near the surface
depth_cmap = mcolors.LinearSegmentedColormap.from_list("ocean_depth", ["#000a0e", "#00141e"])
depth_gradient = [[step] for step in range(64)]
ax.imshow(
    depth_gradient,
    extent=(-2, channel_length + 2, -2, channel_height + 2),
    aspect='auto', origin='lower', cmap=depth_cmap, zorder=0
)

# Draw sleek boundary lines
ax.axhline(y=channel_height, color='#00e5ff', linestyle='--', linewidth=1.5, alpha=0.3)
ax.axhline(y=0, color='#ff6b35', linestyle='-', linewidth=2, alpha=0.35)

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
        ax.arrow(wx, wy, dx, dy, head_width=0.6, head_length=0.9, color='#00e5ff', alpha=0.2)

# Render Rakers (Geometric boundaries)
for start_x in raker_start_positions:
    rx = [start_x, start_x + peak_offset, start_x + raker_width]
    ry = [0.0, raker_height, 0.0]
    ax.fill(rx, ry, color='#001a24', edgecolor='#004d66', linewidth=1.5, zorder=1)

# Particle Trajectory Loop
with st.spinner("Processing particle trajectories and boundary reflections..."):
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
                        # Elastic bounce with coefficient of restitution 0.65
                        # (plastic particle on a smooth surface)
                        velocity_y = -velocity_y * 0.65
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
            ax.plot(x_paths, y_paths, color=poly["color"], alpha=0.9, linewidth=1.5, zorder=3)
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
with col1:
    render_metric("Intake Flux Stream", f"{q_intake_l_min:.1f} L/m", "Q_in — volumetric intake")
with col2:
    render_metric("Filtrate Discharge", f"{q_filtrate_l_min:.1f} L/m", "Q_out — bottom filtrate")
with col3:
    render_metric(
        "Deflection Purity", f"{purity_index:.1f}%",
        "FerroClean achieved 100% via magnetic removal",
        color="#00ff9d"
    )
with col4:
    render_metric(
        "Boundary Leakage", f"{escaped_count}", "Escaped units",
        color="#ff6b35" if escaped_count > 0 else "#00e5ff"
    )
st.markdown("<br>", unsafe_allow_html=True)

# Session Logging
st.session_state.run_counter += 1
st.session_state.telemetry_log.append({
    "Run #": st.session_state.run_counter,
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
tab1, tab2, tab3 = st.tabs(["PARTICLE TRAJECTORIES", "TELEMETRY LOG", "GOVERNING EQUATIONS"])

with tab1:
    ax.set_xlim(-2, channel_length + 2)
    ax.set_ylim(-2, channel_height + 2)
    ax.set_xlabel("Horizontal Flow Displacement (x / mm)", color="#4a6fa5", fontsize=10, family='monospace')
    ax.set_ylabel("Filter Pore Clearance (y / mm)", color="#4a6fa5", fontsize=10, family='monospace')
    ax.tick_params(colors='#4a6fa5', labelsize=9)

    # Hide outer spines for a cleaner HUD look
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(True, linestyle='-', alpha=0.05, color="#00e5ff")
    st.pyplot(fig, transparent=True)
    
with tab2:
    st.dataframe(pd.DataFrame(st.session_state.telemetry_log[::-1]), width="stretch", hide_index=True)
        
with tab3:
    st.markdown(r"""
    #### Governing Hydrodynamic Equations
    The simulation environment evaluates fluid flux iteratively to maintain mass continuity. Total intake volume flux is determined by:
    $$Q_{intake} = A_{channel} \cdot v_{flow}$$

    Particle kinematics are derived by superimposing localized acceleration fields to evaluate vertical displacement relative to the bio-inspired geometric boundaries:
    $$a_{buoyancy} = \left(\frac{\rho_{polymer} - \rho_{fluid}}{\rho_{polymer}}\right) \cdot g$$

    $$F_{drag} = -\frac{1}{2} C_d \cdot \rho_{fluid} \cdot A_{cross} \cdot v_{relative} \cdot |v_{relative}|$$
    """)

# -----------------------------------------------------------------------------
# 7. FOOTER
# -----------------------------------------------------------------------------
st.divider()
st.caption(
    "Claude (Anthropic) assisted with code implementation. "
    "All physics, research direction, and scientific interpretation by the author."
)
st.caption(
    "Built for Hack Club Stardance 2026 | "
    "Computational extension of the FerroClean "
    "microplastics research project | MIT License"
)