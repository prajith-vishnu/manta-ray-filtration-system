cat << 'EOF' > README.md
# 🌌 Manta Ray Bio-Inspired Microplastic Filtration Platform
### *High-Fidelity Computational Fluid Dynamics (CFD) Kinematics Tracking Engine & Interactive Data Workspace*

Development Engine | Build Integrity | Analytical Framework | License Matrix
:---: | :---: | :---: | :---:
[![Python Version](https://img.shields.io/badge/Python-3.14%2B-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/) | [![Framework](https://img.shields.io/badge/Core-Streamlit-FF4B4B?logo=streamlit&logoColor=white&style=flat-square)](https://streamlit.io/) | [![CFD Engine](https://img.shields.io/badge/CFD-Matplotlib%20Vector-005571?style=flat-square)]() | [![License](https://img.shields.io/badge/License-MIT-emerald?style=flat-square)](https://opensource.org/licenses/MIT)

---

## 📖 Scientific Abstract & Project Overview

Traditional mechanical microplastic filtration infrastructure relies heavily on direct-exclusion physical sieving. These systems are bound by a foundational engineering constraint: continuous particle accumulation induces boundary-layer blinding, flow restriction, rapid clogging, and high system-wide fatigue. 

This platform models a cutting-edge biomimetic alternative inspired by the non-clogging, vortical fluid separation mechanics discovered in **Manta Ray marine gill structures (*Mobulidae*)**. Rather than straining water directly through a filter wall, manta rays utilize backward-facing, high-aspect-ratio ridges called **gill rakers** to modify local shear layer profiles. This geometry forces the fluid to generate stabilized bound vortex cells inside the raker channels. 

The resulting hydrodynamic inertia drives suspended microplastic particles away from the active floor pores—ricocheting them safely into the central high-velocity wash current—while allowing purified fluid to cleanly exit through the porous bed.

This software suite delivers an interactive, high-fidelity computational sandbox designed to map particle trajectory kinematics across diverse hydrodynamic regimes, enabling rapid geometric optimization for industrial-grade ocean cleanup hardware.

---

## 🛠️ Core Engineering Architecture

* **Polymorphic Polymer Mass Spectrometer:** Simulates precise hydrodynamic transport pathways for five distinct classifications of ocean microplastics by computing accurate volumetric mass densities ($\text{g/mm}^3$):
  
  Polymer Matrix | Target Acronym | Volumetric Bulk Density ($\text{g/mm}^3$) | Target Particulate Diameter Range
  :--- | :---: | :---: | :---:
  **Polypropylene** | `PP` | $0.90 \times 10^{-3}$ | $1.5\text{ mm} - 4.0\text{ mm}$
  **Low-Density Polyethylene** | `LDPE` | $0.92 \times 10^{-3}$ | $1.0\text{ mm} - 3.0\text{ mm}$
  **Polystyrene** | `PS` | $1.05 \times 10^{-3}$ | $0.5\text{ mm} - 2.0\text{ mm}$
  **Polyethylene Terephthalate** | `PET` | $1.38 \times 10^{-3}$ | $0.5\text{ mm} - 2.5\text{ mm}$
  **Polyvinyl Chloride** | `PVC` | $1.40 \times 10^{-3}$ | $1.0\text{ mm} - 4.5\text{ mm}$

* **Dual-Regime Boundary Layer Kinematics:** Models baseline steady-state **Laminar Stable** flow profiles alongside chaotic, high-frequency **Storm Surge** profiles. The system maps vertical buffeting vectors to evaluate the limits of structural retention under severe turbulence.
* **Continuous Volumetric Flux Integration:** Runs an interactive real-time hydro-volume processing array to monitor instantaneous channel boundary constraints instead of simplified discrete particle metrics.
* **Rigorous Contamination Diagnostics:** Calculates an absolute **Filtrate Purity Index** ($0\% - 100\%$) by constantly auditing particle boundary leakage counts directly against the localized porous discharge rate.
* **Automated Data Logger & Exporter:** Includes an active runtime listener that captures slider coordinates, active material configurations, system purity scores, and absolute leak counts, instantly appending them to a persistent CSV database for automated parametric sweeps.

---

## 🔬 Mathematical Physics Framework

To maintain deep scientific validity, the kinematics engine bypasses cosmetic graphical estimation loops. It resolves discrete forces acting on each particulate coordinate at every micro-interval step ($\Delta t$):

### 1. Volumetric Fluid Flux & Continuity
The global fluid transport and baseline channel velocity matrices are governed by the classical hydrodynamic continuity expression:

$$Q = A \cdot v$$

Where:
* $Q$ is the continuous volumetric flow capacity ($\text{L/min}$).
* $A$ is the internal cross-sectional area of the fluid channel geometry ($25\text{ cm}^2$).
* $v$ is the primary forward horizontal flow speed velocity vector ($\text{mm/s}$).

### 2. Multi-Component Force Balance & Particulate Trajectories
The directional trajectory vector fields of suspended micro-particulates are computed by resolving the coupled interactions of hydrodynamic drag forces and buoyant density deltas:

$$\mathbf{F}_d = -\frac{1}{2} C_d \cdot \rho_{\text{fluid}} \cdot A_p \cdot (\mathbf{v}_p - \mathbf{v}_f) |\mathbf{v}_p - \mathbf{v}_f|$$

$$\mathbf{a}_{\text{buoy}} = \left(\frac{\rho_{\text{polymer}} - \rho_{\text{fluid}}}{\rho_{\text{polymer}}}\right) \cdot \mathbf{g}$$

Where:
* $C_d$ represents the standard spherical particulate drag coefficient ($0.47$).
* $\rho_{\text{fluid}}$ represents the fluid medium baseline density (Seawater: $1.025 \times 10^{-3}\text{ g/mm}^3$).
* $A_p$ represents the cross-sectional surface area of the evaluated particulate item ($\pi r^2$).
* $\mathbf{v}_p - \mathbf{v}_f$ is the relative velocity vector existing between the solid matter and the localized fluid stream.
* $\mathbf{g}$ is the acceleration constant of gravity ($9810\text{ mm/s}^2$).

During the activation of **Storm Surge Mode**, a chaotic boundary layer stress tensor ($\mathbf{a}_{\text{turbulent}}$) is continuously injected across the vertical axis, testing the geometry's structural resilience against real-world mechanical disruption:

$$\mathbf{a}_{\text{total}} = \mathbf{a}_{\text{buoy}} + \mathbf{a}_{\text{drag}} + \mathbf{a}_{\text{turbulent}}$$

---

## 📂 Repository Architecture

```text
├── README.md               # Production-grade system documentation & scientific brief
├── requirements.txt         # Package dependency manifest for cloud container initialization
├── web_app.py              # Cloud-optimized responsive Streamlit server application
├── interactive_app.py      # Desktop GUI dashboard running matplotlib-native backend loops
├── main.py                 # Core tracking script and mathematical coordinate engine
├── param_sweep.py          # Parametric script for testing edge-case geometries
├── analytics.py            # Automated chart compiler and optimization curve processor
├── simulations/            # Low-level physical verification modules
├── data_fetch/             # Protocols for pulling experimental validation figures
└── workspace_saves.csv     # Persistent storage capturing local diagnostic CSV rows

##🚀 Workspace Initialization & Deployment
Environment Prerequisites
This framework requires a local or remote installation of Python 3.14+.
Automated Installation & Launch
Execute this unified terminal sequence to clone the code assets, handle structural dependency tracking, and execute either the desktop control suite or the cloud-native interface web application:

git clone [https://github.com/prajith-vishnu/manta-ray-filtration-system.git](https://github.com/prajith-vishnu/manta-ray-filtration-system.git)
cd manta-ray-filtration-system
pip install -r requirements.txt
streamlit run web_app.py
python3 interactive_app.py

##🗺️ Engineering Development Roadmap
[x] Refactor primitive coordinate algorithms into modular object-oriented parameters.
[x] Move background code threads into a unified, high-contrast dark console HUD.
[x] Integrate high-fidelity continuous fluid volume continuity processing.
[x] Convert visualization architecture to deploy natively to public web infrastructure.
[ ] Upgrade 2D particle boundary sweeps into an expansive 3D vector fluid matrix.
[ ] Export internal node mesh files into cross-compatible CAD structural assets for rapid prototyping.
##📜 License & Compliance
Distributed under the open-source MIT License. Check the parent LICENSE directory files for comprehensive legal validation terms.
EOF
git add README.md
git commit -m "Docs: Update README to enterprise research grade technical specification standard"
git push origin main
