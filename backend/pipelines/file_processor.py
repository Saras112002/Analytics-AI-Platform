import pandas as pd
import os
from pathlib import Path

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def validate_file(filename: str, file_size: int) -> dict:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"File type '{extension}' not allowed. Use CSV, Excel, or JSON. Convert other formats first."
        }

    if file_size > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": "File too large. Maximum size is 50MB"
        }

    return {"valid": True, "error": None}


def read_file(filepath: str) -> pd.DataFrame:
    extension = Path(filepath).suffix.lower()

    if extension == ".csv":
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            raise ValueError("Could not read CSV with any known encoding")

    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)

    elif extension == ".json":
        df = pd.read_json(filepath)
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("JSON could not be read as a table")

    else:
        raise ValueError(
            f"Unsupported file type '{extension}'. Use CSV, Excel, or JSON."
        )

    return df


def extract_schema(df: pd.DataFrame) -> dict:
    schema = {}
    for column in df.columns:
        schema[column] = {
            "dtype": str(df[column].dtype),
            "null_count": int(df[column].isnull().sum()),
            "null_percentage": round(
                df[column].isnull().sum() / len(df) * 100, 2
            ),
            "unique_values": int(df[column].nunique()),
            "sample_values": df[column].dropna().head(3).tolist()
        }
    return schema


def generate_summary(df: pd.DataFrame, filename: str) -> dict:
    schema = extract_schema(df)
    summary = {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "schema": schema,
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
        "has_missing_values": bool(df.isnull().any().any()),
        "missing_value_count": int(df.isnull().sum().sum())
    }
    return summary