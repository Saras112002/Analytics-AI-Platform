# backend/ml/anomaly_detector.py
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df: pd.DataFrame, top_k: int = 5, contamination="auto") -> dict:
    """Real outlier detection on numeric columns. Returns evidence the
    AnomalyAgent will EXPLAIN instead of inventing. contamination='auto'
    over-flags (~10%); pass a float like 0.02 once you know the real rate."""
    numeric = df.select_dtypes(include=[np.number]).dropna(axis=1, how="all").copy()
    if numeric.shape[1] == 0:
        return {"method": "isolation_forest", "status": "no_numeric_columns",
                "rows_scanned": int(len(df)), "anomalies_found": 0,
                "anomaly_rate_pct": 0.0, "per_column_outliers": {}, "most_anomalous_rows": []}

    X = numeric.fillna(numeric.median(numeric_only=True))
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    labels = model.fit_predict(X)        # -1 = anomaly
    scores = model.score_samples(X)      # lower = more anomalous
    n_anom = int((labels == -1).sum())

    per_col = {}
    for col in X.columns:
        q1, q3 = X[col].quantile(0.25), X[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        cnt = int(((X[col] < lo) | (X[col] > hi)).sum())
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