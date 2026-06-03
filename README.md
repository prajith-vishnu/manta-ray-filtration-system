# 🌌 Manta Ray Bio-Inspired Microplastic Filtration Platform
### *Real-Time Computational Fluid Dynamics (CFD) Simulation & Interactive Analytics Dashboard*

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A high-fidelity hydrodynamics simulation environment that models the non-clogging, vortical filtration mechanisms found in manta ray gill rakers. This platform evaluates microplastic particle kinematics across varying fluid regimes to isolate optimal architectural thresholds for marine conservation hardware.

---

## 📖 Executive Summary

Conventional microscopic filtering apparatuses rely on direct sieving, making them highly susceptible to particle accumulation, surface boundary clogging, and rapid structural fatigue. Manta rays bypass this limitation using solid, backward-facing, tooth-like structures (gill rakers) that manipulate fluid shear layers to induce local vortex fields. These vortexes dynamically deflect suspended solids away from filter pores while allowing clean water to pass smoothly through.

This project delivers a dual-layer interactive software suite (Native Desktop & Public Cloud Web Application) built to parameterize, test, and validate this bio-inspired mechanism against real-world environmental stressors.

---

## 🛠️ Key Engineering Features

* **Polymorphic Polymer Engine:** Tracks five discrete plastic classifications simultaneously based on localized material densities ($\text{g/mm}^3$): Polypropylene (PP), Low-Density Polyethylene (LDPE), Polystyrene (PS), Polyethylene (PET), and Polyvinyl Chloride (PVC).
* **Dual-Regime Kinematics:** Models baseline **Laminar Stable** flow profiles alongside chaotic, high-frequency **Storm Surge** regimes utilizing randomized vertical buffeting forces.
* **Continuous Fluid Flux Tracker:** Employs real-time hydro-volume processing arrays to calculate exact volumetric throughput constraints rather than simple batch metrics.
* **Rigorous Contamination Analytics:** Computes a live **Filtrate Purity Index** ($0\% - 100\%$) by evaluating particle boundary leaks directly against continuous bottom pore fluid discharge rates.
* **Diagnostic Data Exporter:** Includes a standalone recording architecture that automatically writes localized simulation parameter coordinates directly into a persistent CSV database for iterative research sweeps.

---

## 🔬 Mathematical Physics Framework

The system bypasses crude graphics behaviors by calculating physical forces using real fluid dynamics equations at every sub-stepping micro-interval $\Delta t$:

### 1. Continuous Volumetric Flux
The continuous inflow and filtration tracking are governed by the classical hydrodynamic continuity equation:

$$Q = A \cdot v$$

Where:
* $Q$ is the continuous volumetric flow rate ($\text{L/min}$).
* $A$ is the fixed cross-sectional intake area of the channel matrix ($25\text{ cm}^2$).
* $v$ is the active forward flow speed velocity vector ($\text{mm/s}$).

### 2. Kinematic Drag & Buoyancy Forces
Particle pathways are resolved by combining buoyant density vector offsets with fluid coupling drag force transformations:

$$F_d = -\frac{1}{2} C_d \cdot \rho_{\text{fluid}} \cdot A_p \cdot v_{\text{rel}} |v_{\text{rel}}|$$

$$a_{\text{buoy}} = \left(\frac{\rho_{\text{polymer}} - \rho_{\text{fluid}}}{\rho_{\text{polymer}}}\right) \cdot g$$

During **Storm Surge Mode**, high-frequency chaotic boundary layer stress is injected into the vertical axis via randomized fluid acceleration vectors ($a_{\text{turbulent}}$), directly testing the physical limits of the manta ray gill geometry.

---

## 📂 Repository Architecture

```text
├── README.md               # Production-grade technical documentation
├── requirements.txt         # Automated server environment initialization manifest
├── web_app.py              # Cloud-optimized Streamlit web application engine
├── interactive_app.py      # Multi-slider native desktop UI controller (Matplotlib API)
├── main.py                 # Core background simulation script
├── param_sweep.py          # Automated background parametric multi-variable testing utility
├── analytics.py            # Data parser and optimization curve chart generator
├── simulations/            # Low-level geometric validation modules
├── data_fetch/             # Sensor and empirical data gathering protocols
└── workspace_saves.csv     # Local storage database for exported diagnostic files
