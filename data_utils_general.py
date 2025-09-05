import pandas as pd

def load_and_process_data(file_path: str) -> dict:
    """
    Load a CSV and auto-detect column types.
    Returns a dictionary with DataFrame, numeric, categorical, and datetime columns.
    """
    df = pd.read_csv(file_path)

    # Attempt to parse datetime columns automatically
    datetime_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        else:
            # Try to parse object columns as datetime
            try:
                parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                if parsed.notna().sum() > 0:
                    df[col] = parsed
                    datetime_cols.append(col)
            except:
                continue

    # Numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Categorical columns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    # Remove any datetime accidentally included
    categorical_cols = [c for c in categorical_cols if c not in datetime_cols]

    # Return all info
    return {
        "df": df,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols
    }
