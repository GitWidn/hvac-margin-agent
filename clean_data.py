import pandas as pd

print("Loading labor logs...")
df = pd.read_csv('/Users/carltonking/Downloads/hvac-agent/labor_logs_all.csv')

print(f"Total rows before cleaning: {len(df)}")

role_map = {
    # Foreman
    'Fmn': 'Foreman',
    'Lead Foreman': 'Foreman',
    'General Foreman': 'Foreman',

    # Journeyman Pipefitter
    'J. Pipefitter': 'Journeyman Pipefitter',
    'JM Pipefitter': 'Journeyman Pipefitter',
    'Journeyman P.F.': 'Journeyman Pipefitter',
    'Pipefitter JM': 'Journeyman Pipefitter',

    # Journeyman Sheet Metal
    'J. Sheet Metal': 'Journeyman Sheet Metal',
    'JM Sheet Metal': 'Journeyman Sheet Metal',
    'Journeyman S.M.': 'Journeyman Sheet Metal',
    'Sheet Metal JM': 'Journeyman Sheet Metal',

    # Apprentice 2nd Year
    'App 2nd Year': 'Apprentice 2nd Year',
    'Apprentice - 2nd': 'Apprentice 2nd Year',
    'Apprentice 2nd Yr': 'Apprentice 2nd Year',

    # Apprentice 4th Year
    '4th Yr Apprentice': 'Apprentice 4th Year',
    'App 4th Year': 'Apprentice 4th Year',
    'Apprentice - 4th': 'Apprentice 4th Year',
    'Apprentice 4th Yr': 'Apprentice 4th Year',

    # Controls
    'Controls Tech': 'Controls Technician',
    'Ctrl Technician': 'Controls Technician',
    'DDC Tech': 'Controls Technician',
    'Controls Specialist': 'Controls Technician',

    # Helper
    'Helper/Laborer': 'Helper',
}

df['role_clean'] = df['role'].replace(role_map)

print("\nBefore vs After (role counts):")
before = df['role'].value_counts()
after = df['role_clean'].value_counts()
print(f"Unique roles before: {len(before)}")
print(f"Unique roles after:  {len(after)}")

print("\nChecking for missing values...")
print(df.isnull().sum())

print("\nChecking for negative hours or costs...")
neg_hours = df[df['hours_st'] < 0]
neg_ot = df[df['hours_ot'] < 0]
neg_rate = df[df['hourly_rate'] < 0]
print(f"Negative straight hours: {len(neg_hours)}")
print(f"Negative overtime hours: {len(neg_ot)}")
print(f"Negative hourly rates:   {len(neg_rate)}")

print("\nChecking for duplicate rows...")
dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")

df_clean = df.drop(columns=['role']).rename(columns={'role_clean': 'role'})
df_clean = df_clean.drop_duplicates()
print(f"Rows after removing duplicates: {len(df_clean)}")
df_clean.to_csv('/Users/carltonking/Downloads/hvac-agent/labor_logs_clean.csv', index=False)
print(f"\nDone! Clean file saved as labor_logs_clean.csv")