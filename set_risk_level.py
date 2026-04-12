#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 19:26:53 2026

@author: ghy
"""

import pandas as pd

df = pd.read_csv('/Users/ghy/Downloads/output.csv')


# 2. 你自己改这3个就行
col_name = "realized_margin_pct_y"    # 你要查的列名
threshold = 0      # 大于多少
symbol = ">="          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = df[col_name] >= threshold
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"Total line：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")

#w
col_name = "realized_margin_pct_y"    # 你要查的列名
threshold = -50     # 大于多少
symbol = ">="          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = (df[col_name] > threshold) & (df[col_name] < 0)
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"Total line ：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")

#2
col_name = "realized_margin_pct_y"    # 你要查的列名
threshold = -50      # 大于多少
symbol = "<"          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = df[col_name] < threshold
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"total line：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")





# 2. 你自己改这3个就行
col_name = "labor_variance_pct_y"    # 你要查的列名
threshold = -20    # 大于多少
symbol = "<="          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = df[col_name] <= threshold
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"total line：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")

#w
col_name = "labor_variance_pct_y"    # 你要查的列名
threshold =5     # 大于多少
symbol = ">="          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = (df[col_name] >= threshold) & (df[col_name] < 300)
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"total line：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")

#2
col_name = "labor_variance_pct_y"    # 你要查的列名
threshold = 250     # 大于多少
symbol = ">="          # 条件：>  >=  <  <=  ==

# 3. 自动统计
condition = df[col_name] >= threshold
count = condition.sum()
total = len(df)
percent= count * 100/total 

print(f"total line：{total}")
print(f"{col_name} {symbol} {threshold} count：{count}")
print(f"{col_name} {symbol} {threshold} percent：{percent}")



