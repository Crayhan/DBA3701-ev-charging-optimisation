import pandas as pd
from gurobipy import Model, GRB, quicksum

def run_lambda_sensitivity(lambda_values):
    results = []

    for lam in lambda_values:

        # === Build model fresh each iteration ===
        m = Model("Lambda_Sensitivity")
        m.setParam("LogToConsole", 0)

        x = m.addVars(I, vtype=GRB.INTEGER, lb=0, name="x")
        y = m.addVars(valid_edges, vtype=GRB.INTEGER, lb=0, name="y")

        # Objective with λ as parameter
        m.setObjective(
            quicksum(ci[i] * x[i] for i in I)
            + lam * quicksum(dij[(i,j)] * y[i,j] for (i,j) in valid_edges),
            GRB.MINIMIZE
        )

        # Constraints (identical to baseline)
        for j in J:
            m.addConstr(
                quicksum(y[i, j] for (i, j2) in valid_edges if j2 == j) >= bj[j],
                f"demand_{j}"
            )

        for i in I:
            m.addConstr(
                quicksum(y[i, j] for (i2, j) in valid_edges if i2 == i)
                <= Si[i] * x[i],
                f"capacity_{i}"
            )

        m.addConstr(
            quicksum(ci[i] * x[i] for i in I) <= B,
            "budget"
        )

        for i in I:
            if install_flag[i] == 0:
                m.addConstr(x[i] == 0)

        for i in I:
            m.addConstr(
                P_exist[i] + charger_power[i] * x[i] >= P_min[i] * subject_to_rule[i]
            )

        for i in I:
            m.addConstr(
                P_exist[i] + charger_power[i] * x[i] <= P_max[i]
            )

        for i in I:
            m.addConstr(
                x[i] <= max_x[i]
            )

        # Solve
        m.optimize()

        # Record results
        install_cost = sum(ci[i] * x[i].X for i in I)
        dist_cost = lam * sum(dij[(i,j)] * y[i,j].X for (i,j) in valid_edges)
        num_chargers = sum(x[i].X for i in I)
        total_obj = m.ObjVal

        results.append({
            "lambda": lam,
            "New_Chargers": num_chargers,
            "Install_Cost": install_cost,
            "Distance_Cost": dist_cost,
            "Total_Objective": total_obj,
            "Budget_Used": install_cost
        })

    return pd.DataFrame(results)

# Run
lambda_values = [1500, 3000, 6000, 9000]
lambda_results = run_lambda_sensitivity(lambda_values)
print(lambda_results)
lambda_results.to_csv("lambda_sensitivity.csv", index=False)