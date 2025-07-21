import pandas as pd
import numpy as np
import random
from datetime import datetime


def occupation_rule(row):
    if row['CustomerAge'] > 60:
        return 'Retired'
    else:
        return random.choice(['Farmer', 'Labour'])

# Map MerchantType based on CustomerOccupation
def merchant_type_rule(row):
    if row['CustomerOccupation'] == 'Farmer':
        return 'Crop/Seed seller'
    elif row['CustomerOccupation'] == 'Labour':
        return 'Migration Help'
    elif row['CustomerOccupation'] == 'Retired':
        return 'Kirana'
    else:
        return 'Unknown'

# Define age group weights (more 60+)
age_groups = {
    '60+': (60, 85),
    '50-60': (50, 59),
    '40-50': (40, 49),
    '30-40': (30, 39),
    '18-30': (18, 29)
}
weights = [0.4, 0.2, 0.15, 0.15, 0.1]  # Skewed toward 60+
today = datetime.today()

def generate_dob():
    group = random.choices(list(age_groups.keys()), weights=weights, k=1)[0]
    min_age, max_age = age_groups[group]
    age = random.randint(min_age, max_age)
    year = today.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe for all months
    return datetime(year, month, day)


# Load your dataset
df = pd.read_csv('financial_exclusion_dataset.csv')

# Convert TransactionDate to datetime
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])

# Assign gender
num_rows = len(df)
num_females = int(num_rows * 0.6)
num_males = num_rows - num_females

genders = ['Female'] * num_females + ['Male'] * num_males
random.shuffle(genders)
df['Gender'] = genders

# 👩 Female Names
female_prefixes = ['Su', 'Ra', 'Ka', 'Vi', 'Me', 'Ba', 'La', 'Mo', 'Di', 'An']
female_suffixes = ['mita', 'lata', 'shree', 'kshi', 'nita', 'priya', 'esha', 'vani', 'ika', 'angi']
female_names = [p + s for p in female_prefixes for s in female_suffixes]

# 👨 Male Names
male_prefixes = ['Ro', 'Ma', 'Vi', 'Ra', 'Ad', 'Sa', 'Sh', 'De', 'La', 'Mo']
male_suffixes = ['nath', 'esh', 'raj', 'deep', 'jit', 'kar', 'veer', 'ram', 'pal', 'an']
male_names = [p + s for p in male_prefixes for s in male_suffixes]

# 🧾 Optional: Deduplicate and shuffle
female_names = list(set(female_names))
male_names = list(set(male_names))
random.shuffle(female_names)
random.shuffle(male_names)

ages = [65, 80, 40, 55, 32]
weightsAge = [0.4, 0.3, 0.1, 0.1, 0.1]  # Heavier bias toward 65 and 80

# Assign names based on gender
df['AccountHolderName'] = [
    random.choice(female_names) if gender == 'Female' else random.choice(male_names)
    for gender in df['Gender']
]


# Simulate Account Opening Dates (before first transaction)
df['Account_Opening_Date'] = df.groupby('AccountID')['TransactionDate'].transform('min') - pd.to_timedelta(np.random.randint(30, 365, size=len(df)), unit='D')
df['Account_Opening_Date'] = pd.to_datetime(df['Account_Opening_Date'], format='%Y-%m-%d')
# 1️⃣ Add 2–3 Year Gaps to Simulate Exclusion
gap_ids = df['AccountID'].drop_duplicates().sample(frac=0.1, random_state=1)
gap_data = []

for acc_id in gap_ids:
    user_txns = df[df['AccountID'] == acc_id].sort_values('TransactionDate')
    first_txn = user_txns.iloc[0].copy()
    second_txn = first_txn.copy()
    second_txn['TransactionDate'] += pd.DateOffset(years=random.choice([2, 3]))
    gap_data.extend([first_txn, second_txn])

df = df[~df['AccountID'].isin(gap_ids)]
df = pd.concat([df, pd.DataFrame(gap_data)], ignore_index=True)

# 2️⃣ Create Dormant Accounts
dormant_ids = df['AccountID'].drop_duplicates().sample(frac=0.05, random_state=2)
dormant_rows = df[df['AccountID'].isin(dormant_ids)].groupby('AccountID').first().reset_index()
dormant_rows['Status'] = 'Dormant'
dormant_rows['TransactionDate'] = dormant_rows['Account_Opening_Date']

# 3️⃣ Update Locations to Remote Villages
villages = [ 'Gadchiroli , Maharashtra', 'Nandurbar , Maharashtra', 'Dhule , Maharashtra', 'Yavatmal, Maharashtra', 'Washim , Maharashtra',
    'Hingoli , Maharashtra', 'Parbhani , Maharashtra', 'Wardha , Maharashtra', 'Buldhana , Maharashtra', 'Melghat , Maharashtra']
df['Location'] = random.choices(villages, k=len(df))
dormant_rows['Location'] = random.choices(villages, k=len(dormant_rows))
dormant_rows['Age'] = [random.choices(ages, weights=weightsAge)[0] for _ in range(len(dormant_rows))]

# Merge Final Data
df = df[~df['AccountID'].isin(dormant_ids)]
# Apply to your dataset
df['DOB'] = [generate_dob().date() for _ in range(len(df))]

# Calculate Age
df['Age'] = df['DOB'].apply(lambda dob: today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)) if pd.notnull(dob) else '65')
df['DOB'] = pd.to_datetime(df['DOB'], errors='coerce', infer_datetime_format=True)

# Format as YYYY-MM-DD
df['DOB'] = df['DOB'].dt.strftime('%Y-%m-%d')

#df = df.rename(columns={'TransactionDate': 'TransactionDates'})
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], format='%Y-%m-%d')  # if day comes first

# Count transactions per AccountID
txn_counts = df.groupby('AccountID').size().reset_index(name='TransactionCount')

# Merge back into original dataset
df = df.merge(txn_counts, on='AccountID', how='left')

# Optional: Set TransactionCount to NaN or blank for non-excluded accounts
df['TransactionCount'] = df.apply(
    lambda row: row['TransactionCount'] if row.get('Status') == 'Excluded' else '',
    axis=1
)


final_df = pd.concat([df, dormant_rows], ignore_index=True)

final_df['CustomerOccupation'] = final_df.apply(occupation_rule, axis=1)

final_df['MerchantType'] = final_df.apply(merchant_type_rule, axis=1)
final_df = final_df.drop(columns=['MerchantID'])

# Save to CSV
final_df.to_csv('financial_exclusion_final.csv', index=False)