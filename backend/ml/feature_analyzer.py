import warnings
warnings.filterwarnings("ignore", message=".*mismatched devices.*")
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
from xgboost import XGBRegressor, XGBClassifier

MIN_ROWS = 20
ID_KEYWORDS = ("id", "code", "zip", "postal", "phone", "index")


def _pick_target(df, target):
    if target and target in df.columns:
        return target
    nums = df.select_dtypes(include=[np.number]).columns.tolist()
    nums = [c for c in nums if not any(k in c.lower() for k in ID_KEYWORDS)]
    return nums[-1] if nums else None


def _is_classification(y):
    if y.dtype == object or str(y.dtype) == "category":
        return True
    return y.nunique() <= 10


def _fit_detect(model_cls, params, X_tr, y_tr):
    try:
        model = model_cls(**{**params, "device": "cuda"})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(X_tr, y_tr)
        fell_back = any("GPU" in str(w.message) for w in caught)
        return model, ("cpu" if fell_back else "cuda")
    except Exception:
        model = model_cls(**{**params, "device": "cpu"})
        model.fit(X_tr, y_tr)
        return model, "cpu"


def _quality_note(metric, score):
    if metric == "r2":
        return ("strong predictive signal" if score > 0.7 else
                "moderate signal" if score > 0.4 else
                "weak signal" if score > 0 else
                "no usable signal (worse than predicting the mean)")
    return ("strong classifier" if score > 0.85 else
            "moderate classifier" if score > 0.65 else "weak classifier")


def analyze_drivers(df: pd.DataFrame, target: str = None, top_k: int = 8) -> dict:
    if len(df) < MIN_ROWS:
        return {"method": "xgboost", "status": f"too_few_rows (<{MIN_ROWS})", "target": None, "drivers": []}

    target_col = _pick_target(df, target)
    if target_col is None:
        return {"method": "xgboost", "status": "no_numeric_target", "target": None, "drivers": []}

    auto = not (target and target in df.columns)
    target_not_found = bool(target) and target not in df.columns
    y = df[target_col]
    X = df.drop(columns=[target_col]).copy()

    # drop ID-like columns from features
    id_cols = [c for c in X.columns if any(k in c.lower() for k in ID_KEYWORDS)]
    X = X.drop(columns=id_cols)

    # drop high-cardinality text/date columns (names, dates) — they're labels, not drivers
    high_card = []
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]) and X[c].nunique() > 50:
            high_card.append(c)
    X = X.drop(columns=high_card)

    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype("category")   # robust: handles object, string, StringDtype
    if X.shape[1] == 0:
        return {"method": "xgboost", "status": "no_feature_columns", "target": target_col, "drivers": []}

    classification = _is_classification(y)
    if classification and (y.dtype == object or str(y.dtype) == "category"):
        y = y.astype("category").cat.codes

    base = dict(n_estimators=300, max_depth=5, learning_rate=0.1,
                tree_method="hist", enable_categorical=True, random_state=42)
    strat = y if classification and y.nunique() > 1 else None
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=strat)

    if classification:
        model, device = _fit_detect(XGBClassifier, base, X_tr, y_tr)
        score = round(float(accuracy_score(y_te, model.predict(X_te))), 3)
        metric = "accuracy"
    else:
        model, device = _fit_detect(XGBRegressor, base, X_tr, y_tr)
        score = round(float(r2_score(y_te, model.predict(X_te))), 3)
        metric = "r2"

    pairs = sorted(zip(X.columns, model.feature_importances_), key=lambda p: p[1], reverse=True)[:top_k]
    drivers = [{"feature": f, "importance": round(float(i), 4)} for f, i in pairs]

    return {
        "method": "XGBoost",
        "compute_device": device,
        "target": target_col,
        "target_auto_selected": auto,
        "target_requested_but_missing": target_not_found,
        "problem_type": "classification" if classification else "regression",
        "model_quality": {metric: score, "interpretation": _quality_note(metric, score)},
        "excluded_id_columns": id_cols,
        "drivers": drivers,
    }