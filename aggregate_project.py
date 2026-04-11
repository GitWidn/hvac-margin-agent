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
df=df.drop(['scheduled_value_x', 'budgeted_labor_x',
'budgeted_material_x', 'total_budget_x', 'actual_labor_cost_x','actual_material_cost_x', 'total_actual_cost_x','realized_margin_pct', 'labor_variance_pct', 'material_variance_pct',
'total_billed_x'],axis=1)

print(df.columns)


df.to_csv("/Users/ghy/Downloads/output.csv",index=False)
    
