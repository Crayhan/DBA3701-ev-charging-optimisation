# ================================
# 1. Import Libraries
# ================================
import pandas as pd
from gurobipy import Model, GRB, quicksum

# ================================
# 2. Load Data
# ================================
def load_data():
    sites = pd.read_csv("candidate_sites.csv")
    demand = pd.read_csv("demand_nodes.csv")
    dist = pd.read_csv("distance_matrix.csv")
    budget = float(pd.read_csv("budget.csv").iloc[0,0])
    return sites, demand, dist, budget

sites, demand, dist, B = load_data()

# ================================
# 3. Prepare Sets & Parameters
# ================================
I = sites["site_id"].tolist()
J = demand["demand_id"].tolist()

Ei = sites.set_index("site_id")["Ei"].to_dict()
Si = sites.set_index("site_id")["Si"].to_dict()
ci = sites.set_index("site_id")["ci"].to_dict()
install_flag = sites.set_index("site_id")["install_flag"].to_dict()

charger_power   = sites.set_index("site_id")["charger_power"].to_dict()
P_exist         = sites.set_index("site_id")["P_exist_kW"].to_dict()
P_min           = sites.set_index("site_id")["P_min_kW"].to_dict()
P_max           = sites.set_index("site_id")["P_max_kW"].to_dict()
subject_to_rule = sites.set_index("site_id")["subject_to_rule"].to_dict()

max_x           = sites.set_index("site_id")["max_x"].to_dict()

bj = demand.set_index("demand_id")["b_j_inc"].to_dict()
dij = {(row.site_id, row.demand_id): row.dij for _, row in dist.iterrows()}

lambda_dist = 3000

# ================================
# 4. Filter Valid Edges
# ================================
VERY_LARGE = 1e8
valid_edges = [(row.site_id, row.demand_id)
               for _, row in dist.iterrows()
               if row.dij < VERY_LARGE]

# ================================
# 5. Build Model
# ================================
m = Model("EV_Charging_Optimisation")

x = m.addVars(I, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(valid_edges, vtype=GRB.INTEGER, lb=0, name="y")

# ================================
# 6. Objective
# ================================
m.setObjective(
    quicksum(ci[i] * x[i] for i in I)
    + lambda_dist * quicksum(dij[(i,j)] * y[i,j] for (i,j) in valid_edges),
    GRB.MINIMIZE
)

# ================================
# 7. Constraints
# ================================

# (1) Demand satisfaction
for j in J:
    m.addConstr(
        quicksum(y[i, j] for (i, j2) in valid_edges if j2 == j) >= bj[j],
        f"demand_{j}"
    )

# (2) Site session capacity
for i in I:
    m.addConstr(
        quicksum(y[i, j] for (i2, j) in valid_edges if i2 == i)
        <= Si[i] * x[i],
        f"capacity_{i}"
    )

# (3) Budget
m.addConstr(
    quicksum(ci[i] * x[i] for i in I) <= B,
    "budget"
)

# (4) Install flag
for i in I:
    if install_flag[i] == 0:
        m.addConstr(x[i] == 0, f"no_install_{i}")

# (5) Minimum required EV power (only for sites subject to rule)
for i in I:
    m.addConstr(
        P_exist[i] + charger_power[i] * x[i] >= P_min[i] * subject_to_rule[i],
        f"min_power_{i}"
    )

# (6) Maximum electrical capacity
for i in I:
    m.addConstr(
        P_exist[i] + charger_power[i] * x[i] <= P_max[i],
        f"max_power_{i}"
    )

# (7) Maximum number of chargers limited by site physical capacity
for i in I:
    m.addConstr(
        x[i] <= max_x[i],
        f"max_chargers_{i}"
    )

# ================================
# 8. Solve
# ================================
m.optimize()
print("\nStatus:", m.Status)
print(f"Optimal Objective Value = {m.ObjVal:.2f}")

solution_x = pd.DataFrame({
    "site_id": I,
    "x_new_chargers": [x[i].X for i in I]
})

solution_y = pd.DataFrame([
    {"site_id": i, "demand_id": j, "sessions": y[i, j].X}
    for (i, j) in valid_edges if y[i, j].X > 1e-6
])

print(solution_x)
print(solution_y)

solution_x.to_csv("solution_x.csv", index=False)
solution_y.to_csv("solution_y.csv", index=False)