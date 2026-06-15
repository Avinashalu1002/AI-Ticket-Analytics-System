import pandas as pd

def load_data():
    df = pd.read_csv("data/support_tickets.csv")

    df.columns = df.columns.str.strip()

    df["created_at"] = pd.to_datetime(df["created_at"])

    return df