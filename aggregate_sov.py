import duckdb
import pandas as pd

con = duckdb.connect()
data = "/Users/carltonking/Downloads/hvac-agent"

print("Loading files...")
con.execute(f"CREATE TABLE contracts AS SELECT * FROM read_csv_auto('{data}/contracts_all.csv')")
con.execute(f"CREATE TABLE sov AS SELECT * FROM read_csv_auto('{data}/sov_all.csv')")
con.execute(f"CREATE TABLE sov_budget AS SELECT * FROM read_csv_auto('{data}/sov_budget_all.csv')")
con.execute(f"CREATE TABLE labor AS SELECT * FROM read_csv_auto('{data}/labor_logs_clean.csv')")
con.execute(f"CREATE TABLE materials AS SELECT * FROM read_csv_auto('{data}/material_deliveries_all.csv')")
con.execute(f"CREATE TABLE billing_lines AS SELECT * FROM read_csv_auto('{data}/billing_line_items_all.csv')")
con.execute(f"CREATE TABLE change_orders AS SELECT * FROM read_csv_auto('{data}/change_orders_all.csv')")

print("Computing labor costs per SOV line...")
con.execute("""
CREATE TABLE labor_summary AS
SELECT sov_line_id,
       SUM((hours_st + hours_ot * 1.5) * hourly_rate * burden_multiplier) AS actual_labor_cost,
       SUM(hours_st + hours_ot) AS total_hours
FROM labor
GROUP BY sov_line_id
""")

print("Computing material costs per SOV line...")
con.execute("""
CREATE TABLE material_summary AS
SELECT sov_line_id,
       SUM(total_cost) AS actual_material_cost
FROM materials
GROUP BY sov_line_id
""")

print("Computing billing per SOV line...")
con.execute("""
CREATE TABLE billing_summary AS
SELECT sov_line_id,
       MAX(total_billed) AS total_billed,
       MAX(pct_complete) AS pct_complete
FROM billing_lines
GROUP BY sov_line_id
""")

print("Computing change orders per project...")
con.execute("""
CREATE TABLE co_summary AS
SELECT project_id,
       SUM(CASE WHEN status = 'Approved' THEN amount ELSE 0 END) AS approved_co_value,
       COUNT(CASE WHEN status = 'Pending' THEN 1 END) AS pending_cos
FROM change_orders
GROUP BY project_id
""")

print("Building SOV line summary...")
summary = con.execute("""
SELECT
    s.sov_line_id,
    s.project_id,
    c.project_name,
    s.line_number,
    s.description,
    s.scheduled_value,
    b.estimated_labor_cost AS budgeted_labor,
    b.estimated_material_cost AS budgeted_material,
    b.estimated_labor_cost + b.estimated_material_cost + b.estimated_equipment_cost + b.estimated_sub_cost AS total_budget,
    COALESCE(l.actual_labor_cost, 0) AS actual_labor_cost,
    COALESCE(l.total_hours, 0) AS actual_hours,
    COALESCE(m.actual_material_cost, 0) AS actual_material_cost,
    COALESCE(l.actual_labor_cost, 0) + COALESCE(m.actual_material_cost, 0) AS total_actual_cost,
    COALESCE(bl.total_billed, 0) AS total_billed,
    COALESCE(bl.pct_complete, 0) AS pct_complete,
    COALESCE(co.approved_co_value, 0) AS approved_co_value,
    COALESCE(co.pending_cos, 0) AS pending_cos,
    ROUND(
        (s.scheduled_value - (COALESCE(l.actual_labor_cost, 0) + COALESCE(m.actual_material_cost, 0)))
        / NULLIF(s.scheduled_value, 0) * 100, 2
    ) AS realized_margin_pct,
    ROUND(
        (COALESCE(l.actual_labor_cost, 0) - b.estimated_labor_cost)
        / NULLIF(b.estimated_labor_cost, 0) * 100, 2
    ) AS labor_variance_pct,
    ROUND(
        (COALESCE(m.actual_material_cost, 0) - b.estimated_material_cost)
        / NULLIF(b.estimated_material_cost, 0) * 100, 2
    ) AS material_variance_pct
FROM sov s
LEFT JOIN contracts c ON s.project_id = c.project_id
LEFT JOIN sov_budget b ON s.sov_line_id = b.sov_line_id
LEFT JOIN labor_summary l ON s.sov_line_id = l.sov_line_id
LEFT JOIN material_summary m ON s.sov_line_id = m.sov_line_id
LEFT JOIN billing_summary bl ON s.sov_line_id = bl.sov_line_id
LEFT JOIN co_summary co ON s.project_id = co.project_id
ORDER BY realized_margin_pct ASC
""").df()

summary.to_csv(f'{data}/sov_summary.csv', index=False)
print(f"Done! {len(summary)} SOV lines saved to sov_summary.csv")
print("\nTop 10 worst margin SOV lines:")
print(summary[['sov_line_id', 'project_id', 'description', 'scheduled_value', 'total_actual_cost', 'realized_margin_pct', 'labor_variance_pct']].head(10).to_string())