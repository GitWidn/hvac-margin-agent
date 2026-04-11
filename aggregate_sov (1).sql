-- =============================================================================
-- Project-Level Aggregation
-- Rolls up all SOV lines, labor, materials, billing, and change orders
-- to one row per project — sized for Claude's context window (~405 rows).
--
-- Compatible with: PostgreSQL (Neon / Supabase) and DuckDB
--
-- Assumed source tables:
--   contracts       (project_id, project_name, ...)
--   sov             (project_id, sov_line_id, scheduled_value, ...)
--   sov_budget      (project_id, sov_line_id, estimated_labor_cost,
--                    estimated_material_cost, estimated_equipment_cost,
--                    estimated_sub_cost, ...)
--   labor           (project_id, sov_line_id, hours_st, hours_ot,
--                    hourly_rate, burden_multiplier, ...)
--   materials       (project_id, sov_line_id, total_cost, ...)
--   billing_lines   (project_id, sov_line_id, total_billed, pct_complete, ...)
--   change_orders   (project_id, amount, status, ...)
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Step 1: Labor cost rolled up to project level
-- Overtime weighted at 1.5x before applying rate and burden
-- -----------------------------------------------------------------------------
WITH labor_summary AS (
    SELECT
        project_id,
        SUM((hours_st + hours_ot * 1.5) * hourly_rate * burden_multiplier) AS actual_labor_cost,
        SUM(hours_st + hours_ot)                                            AS actual_hours
    FROM labor
    GROUP BY project_id
),

-- -----------------------------------------------------------------------------
-- Step 2: Material cost rolled up to project level
-- -----------------------------------------------------------------------------
material_summary AS (
    SELECT
        project_id,
        SUM(total_cost) AS actual_material_cost
    FROM materials
    GROUP BY project_id
),

-- -----------------------------------------------------------------------------
-- Step 3: SOV totals rolled up to project level
-- scheduled_value is summed across all SOV lines per project
-- -----------------------------------------------------------------------------
sov_summary AS (
    SELECT
        project_id,
        SUM(scheduled_value) AS total_scheduled_value
    FROM sov
    GROUP BY project_id
),

-- -----------------------------------------------------------------------------
-- Step 4: Budget totals rolled up to project level
-- -----------------------------------------------------------------------------
budget_summary AS (
    SELECT
        project_id,
        SUM(estimated_labor_cost)     AS budgeted_labor,
        SUM(estimated_material_cost)  AS budgeted_material,
        SUM(
            estimated_labor_cost
            + estimated_material_cost
            + estimated_equipment_cost
            + estimated_sub_cost
        )                             AS total_budget
    FROM sov_budget
    GROUP BY project_id
),

-- -----------------------------------------------------------------------------
-- Step 5: Billing rolled up to project level
-- Sums the latest total_billed per SOV line, then sums across lines
-- -----------------------------------------------------------------------------
billing_summary AS (
    SELECT
        project_id,
        SUM(total_billed) AS total_billed,
        -- Weighted average completion across SOV lines by scheduled value
        SUM(total_billed * pct_complete) / NULLIF(SUM(total_billed), 0) AS avg_pct_complete
    FROM (
        SELECT
            project_id,
            sov_line_id,
            MAX(total_billed)  AS total_billed,
            MAX(pct_complete)  AS pct_complete
        FROM billing_lines
        GROUP BY project_id, sov_line_id
    ) latest_billing
    GROUP BY project_id
),

-- -----------------------------------------------------------------------------
-- Step 6: Change orders rolled up to project level
-- Note: CO status in the data is 'Approved' or 'Rejected' (no 'Pending' rows)
-- pending_cos will always be 0 with current data — retained for forward compat
-- -----------------------------------------------------------------------------
co_summary AS (
    SELECT
        project_id,
        SUM(CASE WHEN status = 'Approved' THEN amount ELSE 0 END) AS approved_co_value,
        COUNT(CASE WHEN status = 'Pending' THEN 1     END)         AS pending_cos
    FROM change_orders
    GROUP BY project_id
)

-- -----------------------------------------------------------------------------
-- Step 7: Final project-level summary
-- One row per project_id — 405 rows total, fits comfortably within Claude's
-- context window for cross-project analysis and insight generation
-- Ordered by worst realized margin first
-- -----------------------------------------------------------------------------
SELECT
    -- Identity
    c.project_id,
    c.project_name,

    -- SOV & Budget
    sv.total_scheduled_value,
    b.budgeted_labor,
    b.budgeted_material,
    b.total_budget,

    -- Actuals
    COALESCE(l.actual_labor_cost,    0)                   AS actual_labor_cost,
    COALESCE(l.actual_hours,         0)                   AS actual_hours,
    COALESCE(m.actual_material_cost, 0)                   AS actual_material_cost,
    COALESCE(l.actual_labor_cost,    0)
        + COALESCE(m.actual_material_cost, 0)             AS total_actual_cost,

    -- Billing
    COALESCE(bl.total_billed,      0)                     AS total_billed,
    COALESCE(bl.avg_pct_complete,  0)                     AS avg_pct_complete,

    -- Change Orders
    COALESCE(co.approved_co_value, 0)                     AS approved_co_value,
    COALESCE(co.pending_cos,       0)                     AS pending_cos,

    -- KPIs
    ROUND(
        (sv.total_scheduled_value
            - (COALESCE(l.actual_labor_cost, 0) + COALESCE(m.actual_material_cost, 0)))
        / NULLIF(sv.total_scheduled_value, 0) * 100,
    2) AS realized_margin_pct,

    ROUND(
        (COALESCE(l.actual_labor_cost, 0) - b.budgeted_labor)
        / NULLIF(b.budgeted_labor, 0) * 100,
    2) AS labor_variance_pct,

    ROUND(
        (COALESCE(m.actual_material_cost, 0) - b.budgeted_material)
        / NULLIF(b.budgeted_material, 0) * 100,
    2) AS material_variance_pct

FROM contracts c
LEFT JOIN sov_summary     sv ON c.project_id = sv.project_id
LEFT JOIN budget_summary  b  ON c.project_id = b.project_id
LEFT JOIN labor_summary   l  ON c.project_id = l.project_id
LEFT JOIN material_summary m  ON c.project_id = m.project_id
LEFT JOIN billing_summary bl  ON c.project_id = bl.project_id
LEFT JOIN co_summary      co  ON c.project_id = co.project_id

ORDER BY realized_margin_pct ASC;
