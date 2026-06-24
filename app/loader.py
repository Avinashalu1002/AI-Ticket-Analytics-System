import pandas as pd
from pathlib import Path
from functools import lru_cache

CSV_PATH = Path(__file__).parent.parent / "data" / "support_tickets.csv"

@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    
    for col in ["response_time_hrs", "resolution_time_hrs", "customer_rating"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df