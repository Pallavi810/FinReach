import pandas as pd
from datetime import datetime, timedelta

# Load the dataset
df = pd.read_csv('financial_exclusion_final.csv')

# Convert dates to datetime
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
df['Account_Opening_Date'] = pd.to_datetime(df['Account_Opening_Date'])

# Define the cutoff date (2 years ago from today)
cutoff_date = pd.Timestamp.today() - pd.DateOffset(years=2)

# Group by AccountID and check the condition
dormant_accounts = df.groupby('AccountID').filter(
    lambda group: (
            len(group) == 1 and
            group['TransactionDate'].iloc[0] == group['Account_Opening_Date'].iloc[0] and
            group['TransactionDate'].iloc[0] <= cutoff_date
    )
)

# Identify dormant account IDs
dormant_ids = df.groupby('AccountID').filter(is_dormant)['AccountID'].unique()

# Create Status column and mark dormant ones
df['Status'] = df['AccountID'].apply(lambda x: 'Dormant' if x in dormant_ids else '')

# Display the IDs
print("Dormant Accounts:")
print(dormant_accounts['AccountID'].unique())

num_dormant = dormant_accounts['AccountID'].nunique()
print(f"Number of dormant accounts: {num_dormant}")
