"""
Data Intake Module

Load CSV or Excel files and produce the dataset_overview section of the report.
"""
import os
import pandas as pd
from typing import Optional


def load_dataset(path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Load a CSV or Excel file. Returns a pandas DataFrame.
    Raises ValueError if the file type is not supported.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .csv or .xlsx")

    if sample_rows and len(df) > sample_rows:
        df = df.sample(sample_rows, random_state=42)
    return df


def profile(df: pd.DataFrame, file_name: str = "") -> dict:
    """
    Profile a DataFrame and return the dataset_overview dict.
    """
    rows, cols = df.shape
    field_types = {col: str(df[col].dtype) for col in df.columns}

    # Missing values
    missing_counts = df.isnull().sum()
    missing_summary = []
    for col in df.columns:
        if missing_counts[col] > 0:
            missing_summary.append({
                "field": col,
                "missing_count": int(missing_counts[col]),
                "missing_pct": round(float(missing_counts[col] / rows * 100), 2),
            })

    # Time range from datetime columns
    time_range = ""
    for col in df.columns:
        if df[col].dtype in ("datetime64[ns]", "datetime64[ns, UTC]"):
            try:
                min_d = df[col].min()
                max_d = df[col].max()
                time_range = f"{min_d.date()} ~ {max_d.date()}"
                break
            except Exception:
                pass

    # Duplicate rows
    dup_rows = int(df.duplicated().sum())

    return {
        "file_name": os.path.basename(file_name) if file_name else "",
        "rows": rows,
        "columns": cols,
        "fields": list(df.columns),
        "field_types": field_types,
        "has_missing": bool(df.isnull().any().any()),
        "missing_summary": missing_summary,
        "duplicate_rows": dup_rows,
        "time_range": time_range,
    }


def detect_numeric_fields(df: pd.DataFrame) -> list:
    """Return names of numeric columns."""
    return list(df.select_dtypes(include=["number"]).columns)


def detect_categorical_fields(df: pd.DataFrame) -> list:
    """Return names of categorical/low-cardinality columns."""
    cats = []
    for col in df.columns:
        if df[col].dtype == "object":
            n_unique = df[col].nunique()
            if 1 < n_unique <= 50:  # reasonable category size
                cats.append(col)
        elif df[col].dtype.name == "category":
            cats.append(col)
    return cats


def detect_date_fields(df: pd.DataFrame) -> list:
    """Return names of datetime columns."""
    return list(df.select_dtypes(include=["datetime64"]).columns)
