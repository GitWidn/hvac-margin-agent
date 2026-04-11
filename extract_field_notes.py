import pandas as pd

print("Loading field notes...")
df = pd.read_csv('/Users/carltonking/Downloads/hvac-agent/field_notes_all.csv', low_memory=False)
print(f"Total field note rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

worst_projects = [
    'PRJ-2021-260',
    'PRJ-2019-113',
    'PRJ-2022-322',
    'PRJ-2020-203',
    'PRJ-2019-152',
    'PRJ-2018-052',
    'PRJ-2021-318',
    'PRJ-2021-315',
    'PRJ-2021-243',
    'PRJ-2022-325'
]

filtered = df[df['project_id'].isin(worst_projects)]
print(f"\nField notes for worst 10 projects: {len(filtered)} rows")
print(filtered['project_id'].value_counts())

filtered.to_csv('/Users/carltonking/Downloads/hvac-agent/field_notes_critical.csv', index=False)
print("\nDone! Saved as field_notes_critical.csv")