# ================================
# Sensitivity Analysis for max_i
# ================================
import pandas as pd
from gurobipy import Model, GRB, quicksum


def solve_with_capacity_factor(cap_factor):

    # -------- scale max_x --------
    max_x_scaled = {i: int(max_x[i] * cap_factor) for i in I}

    # -------- build model --------
    m = Model(f"EV_Charging_CapFactor_{cap_factor}")
    m.Params.LogToConsole = 0

    x_s = m.addVars(I, vtype=GRB.INTEGER, lb=0, name="x")
    y_s = m.addVars(valid_edges, vtype=GRB.INTEGER, lb=0, name="y")

    # -------- objective --------
    m.setObjective(
        quicksum(ci[i] * x_s[i] for i in I)
        + lambda_dist * quicksum(dij[(i,j)] * y_s[i,j] for (i,j) in valid_edges),
        GRB.MINIMIZE
    )

    # -------- constraints --------

    # (1) demand satisfaction
    for j in J:
        m.addConstr(
            quicksum(y_s[i2, j] for (i2, j2) in valid_edges if j2 == j) >= bj[j],
            f"demand_{j}"
        )

    # (2) site session capacity
    for i in I:
        m.addConstr(
            quicksum(y_s[i, j2] for (i2, j2) in valid_edges if i2 == i)
            <= Si[i] * x_s[i],
            f"capacity_{i}"
        )

    # (3) budget
    m.addConstr(quicksum(ci[i] * x_s[i] for i in I) <= B, "budget")

    # (4) no-install flag
    for i in I:
        if install_flag[i] == 0:
            m.addConstr(x_s[i] == 0, f"no_install_{i}")

    # (5) minimum power rule
    for i in I:
        m.addConstr(
            P_exist[i] + charger_power[i] * x_s[i] >= P_min[i] * subject_to_rule[i],
            f"min_power_{i}"
        )

    # (6) max electrical capacity
    for i in I:
        m.addConstr(
            P_exist[i] + charger_power[i] * x_s[i] <= P_max[i],
            f"max_power_{i}"
        )

    # (7) max number of chargers
    for i in I:
        m.addConstr(
            x_s[i] <= max_x_scaled[i],
            f"max_chargers_{i}"
        )

    # -------- solve --------
    m.optimize()

    # -------- collect results --------
    install_cost = sum(ci[i] * x_s[i].X for i in I)
    dist_cost = sum(lambda_dist * dij[(i,j)] * y_s[i,j].X for (i,j) in valid_edges)
    total_new = sum(x_s[i].X for i in I)

    return {
        "Capacity_Factor": cap_factor,
        "New_Chargers": total_new,
        "Install_Cost": install_cost,
        "Distance_Cost": dist_cost,
        "Total_Objective": m.ObjVal,
        "Budget_Used": install_cost
    }



# ================================
# RUN SCENARIOS
# ================================
capacity_factors = [0.8, 1.0, 1.2, 1.5]

results = []
for cf in capacity_factors:
    r = solve_with_capacity_factor(cf)
    results.append(r)
    print(f"Finished scenario {cf}")

results_df = pd.DataFrame(results)
print("\n=== Sensitivity: max_x Scaling ===")
print(results_df)

results_df.to_csv("sensitivity_max_x.csv", index=False)
print("Saved: sensitivity_max_x.csv")