import pandas as pd
from datetime import datetime, timedelta

class ExclusionRuleEngine:
    def __init__(self, df):
        self.df = df.copy()
        self.today = pd.Timestamp.today()
        self.cutoffs = {
            "dormant": timedelta(days=730),
            "at_risk_under_60": timedelta(days=547),
            "at_risk_60_plus": timedelta(days=730)
        }

    def apply_rules(self):
        # Preprocess
        self.df['TransactionDate'] = pd.to_datetime(self.df['TransactionDate'])
        self.df['Account_Opening_Date'] = pd.to_datetime(self.df['Account_Opening_Date'])

        # If Age is present and numeric
        if 'Age' not in self.df.columns:
            raise ValueError("Age column is required to apply age-based rules.")

        self.df['ExclusionStatus'] = self.df.groupby('AccountID').apply(self.evaluate_account).reset_index(level=0, drop=True)
        return self.df

    def evaluate_account(self, group):
        txn_dates = group['TransactionDate'].sort_values()
        opening_date = group['Account_Opening_Date'].iloc[0]
        age = group['Age'].iloc[0]

        # Rule 1: Dormant = only one transaction on opening date and 2+ years old
        if (
            len(group) == 1 and
            txn_dates.iloc[0] == opening_date and
            txn_dates.iloc[0] <= self.today - self.cutoffs["dormant"]
        ):
            return pd.Series(['Excluded'] * len(group))

        # Rule 2: AtRisk = last transaction 1.5 or 2+ years ago based on age
        last_txn = txn_dates.iloc[-1]
        at_risk_cutoff = self.cutoffs["at_risk_60_plus"] if age >= 60 else self.cutoffs["at_risk_under_60"]
        if last_txn <= self.today - at_risk_cutoff:
            return pd.Series(['AtRisk'] * len(group))

        # Else: Active
        return pd.Series(['Active'] * len(group))