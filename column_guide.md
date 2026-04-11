# SOV Summary Column Guide

## Identity Columns
These tell you WHAT and WHERE the row is.

**sov_line_id** — The unique ID for this specific line item. Like a fingerprint. Example: `PRJ-2021-260-SOV-09` means project 2021-260, line item 9.

**project_id** — Which project this line belongs to. Example: `PRJ-2021-260`.

**project_name** — The human readable name of the project. Example: "Nashville Mixed-Income Housing - Climate Control"

**line_number** — The number of this line item within the project. Each project has 15 lines numbered 1 through 15.

**description** — What type of work this line covers. Example: "Ductwork - Fabrication" or "Piping - Hydronic Systems"

---

## Money Columns
These tell you what was planned vs what was spent.

**scheduled_value** — The dollar value assigned to this line item in the original contract. This is the revenue for this piece of work.

**budgeted_labor** — How much labor was estimated to cost at bid time.

**budgeted_material** — How much material was estimated to cost at bid time.

**total_budget** — The total estimated cost for this line item at bid time. Includes labor + material + equipment + subcontractors.

**actual_labor_cost** — What labor actually cost in real life based on all the time cards logged.

**actual_hours** — Total hours actually worked on this line item.

**actual_material_cost** — What materials actually cost based on all delivery receipts.

**total_actual_cost** — actual_labor_cost + actual_material_cost combined. This is the real total spend on this line.

**total_billed** — How much the company has invoiced the client for this line item so far.

**pct_complete** — What percentage of this line item is done. Example: 85 means 85% complete.

**approved_co_value** — Dollar value of approved change orders for this project. Change orders are extra work the client agreed to pay for on top of the original contract.

**pending_cos** — Number of change orders submitted but not yet approved by the client. These are potential money the company might recover.

---

## The Last 4 Columns — The Most Important Ones

**realized_margin_pct** — This is the bottom line. It answers: after spending what we spent, how much profit did we actually make on this line item as a percentage of its value?

- Formula: `(scheduled_value - total_actual_cost) / scheduled_value × 100`
- Example: scheduled_value = $500,000, total_actual_cost = $600,000 → realized_margin_pct = -20%
- Positive means profitable. Negative means losing money.
- PRJ-2021-260-SOV-01 at -218% means they spent 3x the value of that line item. A catastrophic loss.

**labor_variance_pct** — How much did actual labor cost exceed the original labor budget, as a percentage?

- Formula: `(actual_labor_cost - budgeted_labor) / budgeted_labor × 100`
- Example: budgeted $100K, spent $200K → labor_variance_pct = 100%
- 0% means perfectly on budget. Positive means over budget. Negative means under budget.
- PRJ-2021-260-SOV-09 at 1,215% means labor cost 13x what was estimated on that line. That is the single biggest red flag in the entire dataset.

**material_variance_pct** — Same idea but for materials. How much did actual material cost exceed the material budget?

- Formula: `(actual_material_cost - budgeted_material) / budgeted_material × 100`
- Example: budgeted $50K for pipes, spent $80K → material_variance_pct = 60%
- High numbers here suggest material waste, price increases, rework, or scope creep.

**billing_gap** — Not yet in the output but important to add. Formula: `pct_complete - (total_billed / scheduled_value × 100)`. A positive number means the company has done more work than they have invoiced — they are leaving money on the table right now.

---

## How the AI Agent Uses These Columns

When the agent reads this data it looks for patterns like:

- realized_margin_pct below -20% → flag as CRITICAL
- labor_variance_pct above 100% → labor is bleeding
- material_variance_pct above 50% → material problem
- pending_cos greater than 0 → there may be money to recover through change orders
- pct_complete high but total_billed low → company did the work but has not invoiced for it yet
