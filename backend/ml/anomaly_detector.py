# backend/ml/anomaly_detector.py
import numpy as np
import pandas as pd


def detect_anomalies(df: pd.DataFrame, top_k: int = 5, contamination=0.03,
                    exclude_cols=None) -> dict:
    from sklearn.ensemble import IsolationForest    
    """Real outlier detection on numeric columns. Excludes ID-like columns
    (Row ID, Postal Code) that are numeric but not quantities."""
    if len(df) < 20:
        return {"method": "IsolationForest + IQR", "status": "too_few_rows",
                "rows_scanned": int(len(df)), "anomalies_found": 0,
                "anomaly_rate_pct": 0.0, "per_column_outliers": {}, "most_anomalous_rows": []}
    
    numeric = df.select_dtypes(include=[np.number]).dropna(axis=1, how="all").copy()

    # Drop identifier columns — numeric but meaningless for outlier detection
    drop = set(exclude_cols or [])
    for col in numeric.columns:
        name = col.lower()
        if any(k in name for k in ("id", "code", "zip", "postal", "phone", "index")):
            drop.add(col)
    numeric = numeric.drop(columns=[c for c in drop if c in numeric.columns])

    if numeric.shape[1] == 0:
        return {"method": "isolation_forest", "status": "no_numeric_columns",
                "rows_scanned": int(len(df)), "anomalies_found": 0,
                "anomaly_rate_pct": 0.0, "per_column_outliers": {}, "most_anomalous_rows": []}

    X = numeric.fillna(numeric.median(numeric_only=True))
    # everything below this line stays exactly as it already is
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    labels = model.fit_predict(X)        # -1 = anomaly
    scores = model.score_samples(X)      # lower = more anomalous
    n_anom = int((labels == -1).sum())

    flagged = X[labels == -1]          # the 300 rows IF called anomalous
    per_col = {}
    for col in X.columns:
        q1, q3 = X[col].quantile(0.25), X[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        lo = max(lo, float(X[col].min()))
        hi = min(hi, float(X[col].max()))
        cnt = int(((flagged[col] < lo) | (flagged[col] > hi)).sum())   # count within flagged only
        if cnt:
            per_col[col] = {"outlier_count": cnt,
                            "normal_range": [round(float(lo), 2), round(float(hi), 2)]}
    rows = []
    for i in np.argsort(scores)[:top_k]:
        rec = {c: (round(float(v), 3) if isinstance(v, (int, float, np.floating, np.integer)) else v)
            for c, v in numeric.iloc[i].items()}
        rec["_anomaly_score"] = round(float(scores[i]), 4)
        rows.append(rec)

    return {
        "method": "IsolationForest + IQR",
        "rows_scanned": int(len(df)),
        "columns_used": list(X.columns),
        "anomalies_found": n_anom,
        "anomaly_rate_pct": round(100 * n_anom / len(df), 2),
        "per_column_outliers": per_col,
        "most_anomalous_rows": rows,
    }