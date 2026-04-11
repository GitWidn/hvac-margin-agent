import duckdb
import pandas as pd

con = duckdb.connect()
data = "/Users/carltonking/Downloads/hvac-agent"

print("Loading files...")
con.execute(f"CREATE TABLE contracts AS SELECT * FROM read_csv_auto('{data}/contracts_all.csv')")
con.execute(f"CREATE TABLE labor AS SELECT * FROM read_csv_auto('{data}/labor_logs_clean.csv')")
con.execute(f"CREATE TABLE sov_budget AS SELECT * FROM read_csv_auto('{data}/sov_budget_all.csv')")
con.execute(f"CREATE TABLE materials AS SELECT * FROM read_csv_auto('{data}/material_deliveries_all.csv')")
con.execute(f"CREATE TABLE billing AS SELECT * FROM read_csv_auto('{data}/billing_history_all.csv')")
con.execute(f"CREATE TABLE change_orders AS SELECT * FROM read_csv_auto('{data}/change_orders_all.csv')")

print("Computing labor costs...")
con.execute("""
CREATE TABLE labor_summary AS
SELECT project_id,
       SUM((hours_st + hours_ot * 1.5) * hourly_rate * burden_multiplier) AS actual_labor_cost
FROM labor
GROUP BY project_id
""")

print("Computing material costs...")
con.execute("""
CREATE TABLE material_summary AS
SELECT project_id,
       SUM(total_cost) AS actual_material_cost
FROM materials
GROUP BY project_id
""")

print("Computing budgets...")
con.execute("""
CREATE TABLE budget_summary AS
SELECT project_id,
       SUM(estimated_labor_cost) AS budgeted_labor,
       SUM(estimated_material_cost) AS budgeted_material,
       SUM(estimated_labor_cost + estimated_material_cost + estimated_equipment_cost + estimated_sub_cost) AS total_budget
FROM sov_budget
GROUP BY project_id
""")

print("Computing billing...")
con.execute("""
CREATE TABLE billing_summary AS
SELECT project_id,
       MAX(cumulative_billed) AS total_billed,
       SUM(retention_held) AS total_retention_held
FROM billing
GROUP BY project_id
""")

print("Computing approved change orders...")
con.execute("""
CREATE TABLE co_summary AS
SELECT project_id,
       SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) AS approved_co_value,
       COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending_cos
FROM change_orders
GROUP BY project_id
""")

print("Building final project summary...")
summary = con.execute("""
SELECT
    c.project_id,
    c.project_name,
    c.original_contract_value,
    COALESCE(co.approved_co_value, 0) AS approved_co_value,
    c.original_contract_value + COALESCE(co.approved_co_value, 0) AS adjusted_contract_value,
    COALESCE(b.total_budget, 0) AS total_budget,
    COALESCE(l.actual_labor_cost, 0) AS actual_labor_cost,
    COALESCE(m.actual_material_cost, 0) AS actual_material_cost,
    COALESCE(l.actual_labor_cost, 0) + COALESCE(m.actual_material_cost, 0) AS total_actual_cost,
    COALESCE(bl.total_billed, 0) AS total_billed,
    COALESCE(bl.total_retention_held, 0) AS total_retention_held,
    COALESCE(co.pending_cos, 0) AS pending_cos,
    ROUND(
        (c.original_contract_value - (COALESCE(l.actual_labor_cost, 0) + COALESCE(m.actual_material_cost, 0)))
        / NULLIF(c.original_contract_value, 0) * 100, 2
    ) AS realized_margin_pct
FROM contracts c
LEFT JOIN labor_summary l ON c.project_id = l.project_id
LEFT JOIN material_summary m ON c.project_id = m.project_id
LEFT JOIN budget_summary b ON c.project_id = b.project_id
LEFT JOIN billing_summary bl ON c.project_id = bl.project_id
LEFT JOIN co_summary co ON c.project_id = co.project_id
ORDER BY realized_margin_pct ASC
""").df()

summary.to_csv(f'{data}/project_summary.csv', index=False)
print(f"Done! {len(summary)} projects saved to project_summary.csv")
print("\nTop 10 worst margin projects:")
print(summary[['project_id','project_name','original_contract_value','total_actual_cost','realized_margin_pct']].head(10).to_string())