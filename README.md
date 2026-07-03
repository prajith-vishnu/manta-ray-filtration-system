# Manta Ray CFD Filtration Simulator

A computational fluid dynamics simulator modeling bio-inspired microplastic filtration — built as a computational extension of the FerroClean research project.

![Manta Ray CFD Dashboard](dashboard-preview.png)

## Background

FerroClean (2025-2026) proved ferrofluid magnetic separation achieves up to 100% microplastic removal efficiency from water, winning 3rd place at the NSF-affiliated UNT Physics Science Fair against college-level competitors.

That raised a follow-up question: could passive bio-inspired geometry achieve similar separation without chemical intervention? Manta rays use cross-flow filtration through gill rakers to separate particles from seawater without clogging. This simulator models that mechanism computationally.

## What It Does

Simulates microplastic particle transport through manta ray-inspired channel geometry using:

- Lagrangian particle tracking with real buoyancy and drag force equations
- Five real microplastic polymer types (PP, LDPE, PS, PET, PVC) with accurate bulk densities
- Configurable flow velocity and raker geometry
- Storm surge mode simulating turbulent conditions
- Session logging of deflection efficiency metrics

## Findings

Across a 32-run parameter sweep (raker heights 2–8 mm, flow velocities 150–600 mm/s, 200 particles per run — see `simulation_telemetry.csv`), deflection purity averaged 89.0% under laminar flow conditions. Under storm surge conditions this dropped to 85.6%, with the largest penalty at the reference geometry: at 8 mm rakers and 150 mm/s flow, purity fell from 91.0% (laminar) to 74.5% (turbulent). Purity dropped as low as 49.5% in the worst turbulent configuration.

Passive geometry reached 100% deflection only at high flow velocities under laminar conditions — it cannot guarantee complete separation across realistic conditions. These findings support continued development of active chemical methods like ferrofluid magnetic separation.

Negative results are valid scientific findings.

## Research Series

- **FerroClean v1 (2025-2026):** Physical experiments, 100% removal efficiency, UNT Science Fair winner
- **Manta Ray CFD (2026):** Computational modeling, passive geometry cannot guarantee full separation under turbulence (89.0% laminar vs. 85.6% turbulent average purity)
- **FerroClean v2 (planned):** Improved methodology targeting ISEF submission

## Live Demo

https://manta-ray-filtration-system-two.vercel.app

The demo is a static site (vanilla JavaScript + HTML5 Canvas) that runs the full particle
simulation client-side, so it loads instantly with no server wake-up delay. Hosted on Vercel.

## Tech Stack

- **Web demo:** Vanilla JavaScript + HTML5 Canvas (`index.html`), deployed on Vercel
- **Research code:** Python 3, Streamlit, Matplotlib, Pandas (parameter sweeps and the original dashboard)

## Run Locally

```bash
git clone https://github.com/prajith-vishnu/manta-ray-filtration-system
cd manta-ray-filtration-system

# Web demo — just open it in a browser
open index.html

# Python research dashboard
pip install -r requirements.txt
streamlit run web_app.py
```

## AI Usage

Claude (Anthropic) was used as a coding assistant to implement the Streamlit interface and optimize simulation loops. Physics formulation, research direction, and scientific interpretation by Prajith Vishnu Rajesh Kumar.

## License

MIT
