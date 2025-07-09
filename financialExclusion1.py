import pandas as pd
import numpy as np
import random

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

# Sample name lists
female_names = [
    'Aaradhya Pandey', 'Anjali Kumar', 'Kavya Nanda', 'Meera Sevak', 'Priya Deb', 'Riya Sonami', 'Saanvi Shukla', 'Isha Tiwari', 'Tanvi Das', 'Divya Guha',
    'Neha Kamble', 'Lakshmi Singh', 'Jyoti Saxena', 'Pooja Sharma', 'Sneha Rathod', 'Nandini Panja', 'Aditi Rao', 'Radha Krishnan', 'Simran Singh', 'Trisha Sharma'
]

male_names = [
    'Aarav', 'Rohan', 'Aditya', 'Vihaan', 'Raj', 'Dev', 'Kabir', 'Arjun', 'Siddharth', 'Ravi',
    'Amit', 'Kunal', 'Manoj', 'Suresh', 'Nikhil', 'Vikram', 'Yash', 'Rishi', 'Sameer', 'Uday'
]

# Assign names based on gender
df['AccountHolderName'] = [
    random.choice(female_names) if gender == 'Female' else random.choice(male_names)
    for gender in df['Gender']
]


# Simulate Account Opening Dates (before first transaction)
df['Account_Opening_Date'] = df.groupby('AccountID')['TransactionDate'].transform('min') - pd.to_timedelta(np.random.randint(30, 365, size=len(df)), unit='D')

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
villages = ['Rampur, Jharkhand', 'Dantewada, Chhattisgarh', 'Banspal, Odisha', 'Barmer, Rajasthan', 'Dhemaji, Assam']
df['Location'] = random.choices(villages, k=len(df))
dormant_rows['Location'] = random.choices(villages, k=len(dormant_rows))

# Merge Final Data
df = df[~df['AccountID'].isin(dormant_ids)]
final_df = pd.concat([df, dormant_rows], ignore_index=True)






# Save to CSV
final_df.to_csv('financial_exclusion_final.csv', index=False)