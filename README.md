# DBA3701-ev-charging-optimisation
This repository contains the full optimisation model, data inputs, and solver outputs for our EV charging infrastructure deployment study in the East Region of Singapore.
The model is implemented using Python + Gurobi MILP, and supports reproducible experimentation, sensitivity analysis, and dual interpretation for policy insights.

## 📌 Project Overview

This work develops a mixed-integer linear programming (MILP) model to determine optimal installation of new EV chargers across 76 candidate sites near seven demand nodes in the East Region of Singapore.

It minimises:
- Installation cost, and
- User distance disutility

while satisfying:
- Charging demand,
- Electrical constraints,
- Regulatory minimum power requirements,
- Physical site capacity (max_i),
- Budget limitations.

The model generates:
- Optimal number of chargers per site
- Full demand–supply flow assignments (𝑦ᵢⱼ)
- Sensitivity analyses (budget, λ, maxᵢ, etc.)
- LP-relaxation dual shadow prices

All outputs are provided in easily downloadable .csv format.
