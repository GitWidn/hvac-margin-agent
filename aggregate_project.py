#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 12:16:48 2026

@author: ghy
"""


# import anthropic
import pandas as pd

df = pd.read_csv('/Users/ghy/Downloads/sov_summary.csv')

df = pd.read_csv('/Users/ghy/Downloads/sov_summary.csv')

print(df.columns)
print(df.head())

top_projects = df.nsmallest(10, 'actual_labor_cost').to_string()  # worst margin first


# def agent(df):
    
# calculate the risk

# Labor Cost = (hours_st + hours_ot × 1.5) × hourly_rate × burden_multiplier
# Variance = Actual Cost - Budget
# Billing Gap = % Complete - % Billed
# Budget Coverage = Estimated Budget / Contract Value


sum_number = df.groupby('project_id', as_index=False)['actual_labor_cost'].sum()
df = df.merge(sum_number, on='project_id', how='left')
sum_number = df.groupby('project_id', as_index=False)['actual_material_cost'].sum()
df = df.merge(sum_number, on='project_id', how='left')

sum_number = df.groupby('project_id', as_index=False)['total_actual_cost'].sum()
df = df.merge(sum_number, on='project_id', how='left')


sum_number = df.groupby('project_id', as_index=False)['scheduled_value'].sum()
df = df.merge(sum_number, on='project_id', how='left')

sum_number = df.groupby('project_id', as_index=False)['total_budget'].sum()
df = df.merge(sum_number, on='project_id', how='left')

sum_number = df.groupby('project_id', as_index=False)['budgeted_material'].sum()
df = df.merge(sum_number, on='project_id', how='left')

sum_number = df.groupby('project_id', as_index=False)['budgeted_labor'].sum()
df = df.merge(sum_number, on='project_id', how='left')

sum_number = df.groupby('project_id', as_index=False)['total_billed'].sum()
df = df.merge(sum_number, on='project_id', how='left')


def compute_risk(df):
    df["LaborCost"] = df["actual_labor_cost_y"];
    df["Variance"]=df["total_actual_cost_y"] - df["total_budget_y"]
    # Billing Gap = % Complete - % Billed
    df["Budget Coverage"] = df["total_budget_y"] / df["scheduled_value_y"]
    df["realized_margin_pct_y"]=(df["scheduled_value_y"]-df["total_actual_cost_y"]) / (df["scheduled_value_y"] * 100)
    df["labor_variance_pct_y"]=(df["actual_labor_cost_y"]- df["budgeted_labor_y"]) /(df["budgeted_labor_y"] * 100)
    df["material_variance_pct_y"]=(df["actual_material_cost_y"] - df["budgeted_material_y"]) / (df["budgeted_material_y"] * 100)
    
compute_risk(df)



df.to_csv("/Users/ghy/Downloads/output.csv",index=False)
    
