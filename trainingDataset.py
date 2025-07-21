import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
num_accounts = 400  # ~400 unique accounts will create 1000 rows
today = datetime.today()
villages = ['Gadchiroli , Maharashtra', 'Nandurbar , Maharashtra', 'Dhule , Maharashtra', 'Yavatmal, Maharashtra', 'Washim , Maharashtra',
    'Hingoli , Maharashtra', 'Parbhani , Maharashtra', 'Wardha , Maharashtra', 'Buldhana , Maharashtra', 'Melghat , Maharashtra']
female_names = ['Anjali', 'Kavya', 'Meera', 'Priya', 'Saanvi', 'Isha', 'Trisha', 'Sneha', 'Neha', 'Divya']
male_names = ['Aarav', 'Rohan', 'Kabir', 'Raj', 'Aditya', 'Arjun', 'Ravi', 'Vikram', 'Manoj', 'Siddharth']

# Age group weights skewed toward 60+
age_groups = {
    '60+': (60, 85),
    '50-60': (50, 59),
    '40-50': (40, 49),
    '30-40': (30, 39),
    '18-30': (18, 29)
}
age_weights = [0.4, 0.2, 0.15, 0.15, 0.1]

rows = []


def generate_dob():
    group = random.choices(list(age_groups.keys()), weights=age_weights)[0]
    min_age, max_age = age_groups[group]
    age = random.randint(min_age, max_age)
    year = today.year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day), age






for i in range(num_accounts):
    account_id = f"A{i + 1:04d}"
    gender = random.choices(['Female', 'Male'], weights=[0.6, 0.4])[0]
    name = random.choice(female_names) if gender == 'Female' else random.choice(male_names)
    location = random.choice(villages)
    dob, age = generate_dob()
    opening_date = today - timedelta(days=random.randint(800, 3000))

    # Assign exclusion status
    status = random.choices(['Excluded', 'AtRisk', 'Active'], weights=[0.3, 0.3, 0.4])[0]

    if status == 'Excluded':
        transaction_dates = [opening_date]
    elif status == 'AtRisk':
        cutoff = timedelta(days=730) if age >= 60 else timedelta(days=547)
        last_txn = today - cutoff
        transaction_dates = [opening_date + timedelta(days=30), last_txn]
    else:
        txn1 = opening_date + timedelta(days=random.randint(30, 180))
        txn2 = txn1 + timedelta(days=random.randint(90, 180))
        txn3 = txn2 + timedelta(days=random.randint(90, 180))
        transaction_dates = [txn1, txn2, txn3]

    for txn_date in transaction_dates:
        is_dormant = (
                status == 'Excluded' and
                len(transaction_dates) == 1 and
                txn_date == opening_date.date() and
                opening_date.date() <= (today - timedelta(days=730)).date()
        )

    for txn_date in transaction_dates:
        row = {
            'AccountID': account_id,
            'AccountHolderName': name,
            'Gender': gender,
            'Location': location,
            'DOB': dob.date(),
            'Age': age,
            'Account_Opening_Date': opening_date.date(),
            'TransactionDate': txn_date.date(),
            'ExclusionStatus': status,
            'IsDormant': is_dormant

        }
        rows.append(row)

    for i in range(5):  # Create guaranteed dormant accounts
        account_id = f"D{i + 1:04d}"
        opening_date = today - timedelta(days=1000)
        txn_date = opening_date
        age = random.randint(60, 85)
        dob = datetime(today.year - age, random.randint(1, 12), random.randint(1, 28))
        row = {
            'AccountID': account_id,
            'AccountHolderName': 'DormantUser',
            'Gender': 'Female',
            'Location': random.choice(villages),
            'DOB': dob.date(),
            'Age': age,
            'Account_Opening_Date': opening_date.date(),
            'TransactionDate': txn_date.date(),
            'ExclusionStatus': 'Excluded',
            'IsDormant': True
        }
        rows.append(row)


# Create DataFrame
df = pd.DataFrame(rows)

# Limit to 1000 rows
df = df.sample(n=1000, random_state=42,replace=True).reset_index(drop=True)

# Save dataset
df.to_csv('training_exclusion_flat.csv', index=False)

dormant_df = df[df['IsDormant'] == False]
print("Dormant ", dormant_df)
