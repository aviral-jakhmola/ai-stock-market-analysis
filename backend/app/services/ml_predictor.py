import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators


FEATURE_COLUMNS = [
    "open", "high", "low", "close", "volume",
    "sma_20", "sma_50", "ema_20", "ema_50",
    "rsi_14", "macd", "macd_signal", "macd_histogram",
    "bb_middle", "bb_upper", "bb_lower",
    "return_1d", "intraday_return", "high_low_range", "volume_change",
    "sma_20_distance", "sma_50_distance",
    "ema_20_distance", "ema_50_distance",
    "bb_position",
]


def add_relative_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["return_1d"] = df["close"].pct_change()
    df["intraday_return"] = (df["close"] - df["open"]) / df["open"]
    df["high_low_range"] = (df["high"] - df["low"]) / df["close"]
    df["volume_change"] = df["volume"].pct_change()
    df["sma_20_distance"] = (df["close"] - df["sma_20"]) / df["sma_20"]
    df["sma_50_distance"] = (df["close"] - df["sma_50"]) / df["sma_50"]
    df["ema_20_distance"] = (df["close"] - df["ema_20"]) / df["ema_20"]
    df["ema_50_distance"] = (df["close"] - df["ema_50"]) / df["ema_50"]

    band_width = df["bb_upper"] - df["bb_lower"]
    df["bb_position"] = (df["close"] - df["bb_lower"]) / band_width.replace(0, np.nan)

    return df


def prepare_classification_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Target: 1 if tomorrow's close is higher than today's, else 0.

    next_close is stored as a real column (not just a local variable) and
    included in dropna(), so the final row -- where next_close is NaN --
    is correctly dropped instead of silently becoming a mislabeled
    target=0 (NaN > x evaluates to False, not NaN, so a plain dropna()
    on target alone won't catch it).
    """
    df = df.copy()

    df["next_close"] = df["close"].shift(-1)
    df["target"] = (df["next_close"] > df["close"]).astype(int)

    # Only clean feature columns actually present, so this also works
    # on partial/synthetic frames used in unit tests.
    present_features = [c for c in FEATURE_COLUMNS if c in df.columns]

    for column in present_features:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if present_features:
        df[present_features] = df[present_features].replace([np.inf, -np.inf], np.nan)

    df.dropna(subset=present_features + ["next_close", "target"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def train_test_split_chronological(df: pd.DataFrame, test_size: float = 0.2):
    """Splits by TIME, not randomly — train = earlier rows, test = later rows."""
    split_index = int(len(df) * (1 - test_size))
    return df.iloc[:split_index].copy(), df.iloc[split_index:].copy()


def naive_classification_baseline(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """Baseline: always predict the majority class seen in TRAINING data."""
    majority_class = train_df["target"].mode()[0]
    naive_predictions = [majority_class] * len(test_df)
    accuracy = accuracy_score(test_df["target"], naive_predictions)
    return {"accuracy": round(accuracy, 4), "majority_class": int(majority_class)}


def train_xgboost_classifier(train_df: pd.DataFrame):
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target"]

    model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.03,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def evaluate_classifier(model, test_df: pd.DataFrame) -> dict:
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target"]
    predictions = model.predict(X_test)
    return {"accuracy": round(accuracy_score(y_test, predictions), 4)}


def predict_direction(ticker: str) -> dict:
    """
    Trains the classifier fresh on a ticker's history and predicts
    tomorrow's direction (UP/DOWN) using the most recent day's features.

    Note: retrains on every call (no persisted model), so this endpoint
    is slower than the others and accuracy may vary slightly between
    calls due to XGBoost's own training randomness.
    """
    df = fetch_stock_data(ticker=ticker, period="5y")

    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    df = add_indicators(df)
    df = add_relative_features(df)
    df = prepare_classification_dataset(df)

    if len(df) < 100:
        raise ValueError(
            f"Insufficient data for '{ticker}' after preprocessing: "
            f"{len(df)} usable rows"
        )

    train_df, test_df = train_test_split_chronological(df)
    model = train_xgboost_classifier(train_df)
    eval_result = evaluate_classifier(model, test_df)

    latest_features = df[FEATURE_COLUMNS].iloc[[-1]]
    prediction = model.predict(latest_features)[0]
    probabilities = model.predict_proba(latest_features)[0]

    return {
        "ticker": ticker,
        "direction": "UP" if prediction == 1 else "DOWN",
        "probability_up": round(float(probabilities[1]), 4),
        "probability_down": round(float(probabilities[0]), 4),
        "model_accuracy_on_test_set": eval_result["accuracy"],
    }


if __name__ == "__main__":
    result = predict_direction("RELIANCE.NS")
    print(result)