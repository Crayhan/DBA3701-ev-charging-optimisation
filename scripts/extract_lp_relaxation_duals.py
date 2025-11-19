# ============================================
# A.9.4 LP Relaxation Duals
# ============================================

m_lp = m.copy()
m_lp = m_lp.relax()
m_lp.Params.OutputFlag = 0
m_lp.optimize()

cons = m_lp.getConstrs()

dual_df = pd.DataFrame({
    "constraint": [c.ConstrName for c in cons],
    "pi": m_lp.getAttr("Pi", cons),
    "slack": m_lp.getAttr("Slack", cons)
})

dual_df["abs_pi"] = dual_df["pi"].abs()
dual_df = dual_df.sort_values("abs_pi", ascending=False)

dual_df.to_csv("lp_relaxation_duals.csv", index=False)
print("Saved lp_relaxation_duals.csv")
