import pandas as pd
import numpy as np

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Load, clean, and enrich transaction dataset."""
    df = pd.read_csv(file_path)

    # Force datetime conversion
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["invoice_no", "customer_id", "invoice_date", "quantity", "price"])

    # Ensure numeric types
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Keep only valid values
    df = df[(df["quantity"] > 0) & (df["price"] >= 0)]

    # Feature engineering
    df["revenue"] = df["quantity"] * df["price"]

    # Safely extract month
    if pd.api.types.is_datetime64_any_dtype(df["invoice_date"]):
        df["month"] = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    else:
        df["month"] = pd.NaT

    # Age groups
    if "age" in df.columns:
        bins = [0, 24, 34, 44, 54, 64, 120]
        labels = ["<=24", "25-34", "35-44", "45-54", "55-64", "65+"]
        df["age_group"] = pd.cut(
            df["age"].fillna(0).astype(int), bins=bins, labels=labels, include_lowest=True
        )
    else:
        df["age_group"] = "Unknown"

    return df
