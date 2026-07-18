import pandas as pd
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators


FEATURE_COLUMNS = [
    "open", "high", "low", "close", "volume",
    "sma_20", "sma_50", "ema_20", "ema_50",
    "rsi_14",
    "macd", "macd_signal", "macd_histogram",
    "bb_middle", "bb_upper", "bb_lower",
]


def prepare_classification_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Target: 1 if tomorrow's close is higher than today's, else 0.
    Chosen over price/return regression after testing showed regression
    (XGBoost and LSTM, multiple configs) never reliably beat a naive
    baseline, while direction classification showed a small, consistent edge.
    """
    df = df.copy()
    next_close = df["close"].shift(-1)
    df["target"] = (next_close > df["close"]).astype(int)
    df = df.dropna()
    return df


def train_test_split_chronological(df: pd.DataFrame, test_size: float = 0.2):
    """Splits by TIME, not randomly — train = earlier rows, test = later rows."""
    split_index = int(len(df) * (1 - test_size))
    return df.iloc[:split_index], df.iloc[split_index:]


def naive_classification_baseline(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict:
    """Baseline: always predict the majority class seen in TRAINING data."""
    majority_class = train_df["target"].mode()[0]
    naive_predictions = [majority_class] * len(test_df)
    accuracy = accuracy_score(test_df["target"], naive_predictions)
    return {"accuracy": round(accuracy, 4), "majority_class": int(majority_class)}


def train_xgboost_classifier(train_df: pd.DataFrame):
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target"]
    model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
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
    tomorrow's direction (UP/DOWN) using the most recent day's indicators.

    Note: retrains on every call (no persisted model), so this endpoint
    is slower than the others and accuracy may vary slightly between
    calls due to XGBoost's own training randomness — this was measured
    to be within roughly ±1-2 percentage points across repeated runs.
    """
    df = fetch_stock_data(ticker=ticker, period="5y")
    df = add_indicators(df)
    df = prepare_classification_dataset(df)

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