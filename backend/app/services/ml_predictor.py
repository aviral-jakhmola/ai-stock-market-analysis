import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators


FEATURE_COLUMNS = [
    "open", "high", "low", "close", "volume",
    "sma_20", "sma_50", "ema_20", "ema_50",
    "rsi_14",
    "macd", "macd_signal", "macd_histogram",
    "bb_middle", "bb_upper", "bb_lower",
]


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the target as tomorrow's PERCENTAGE RETURN, not the raw price.
    Tree models can't extrapolate beyond prices seen in training, but
    daily % returns stay in a roughly consistent range over time,
    which is a much fairer target for this kind of model.
    """
    df = df.copy()

    # tomorrow's close, same shift trick as before
    next_close = df["close"].shift(-1)

    # convert to a percentage return: (tomorrow - today) / today
    df["target"] = (next_close - df["close"]) / df["close"]

    df = df.dropna()

    return df


def train_test_split_chronological(df: pd.DataFrame, test_size: float = 0.2):
    """
    Splits data by TIME, not randomly. Train = earlier rows, Test = later rows.
    This matters: a random shuffle would let the model 'see' future data
    during training, which is impossible in real trading and would make
    our evaluation dishonest.
    """
    split_index = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    return train_df, test_df


def naive_baseline_error(test_df: pd.DataFrame) -> dict:
    """
    Naive baseline is now: guess 0% change (tomorrow = today), in return terms.
    """
    naive_predictions = pd.Series(0, index=test_df.index)  # predicting "no change"
    actual = test_df["target"]

    mae = mean_absolute_error(actual, naive_predictions)
    rmse = mean_squared_error(actual, naive_predictions) ** 0.5

    return {"mae": round(mae, 5), "rmse": round(rmse, 5)}


def evaluate_model(model, test_df: pd.DataFrame) -> dict:
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target"]

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    return {"mae": round(mae, 5), "rmse": round(rmse, 5)}

from xgboost import XGBRegressor


def train_xgboost_model(train_df: pd.DataFrame):
    """
    Trains an XGBoost regressor on the training set.
    """
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target"]

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
    )
    model.fit(X_train, y_train)

    return model


def evaluate_model(model, test_df: pd.DataFrame) -> dict:
    """
    Predicts on the held-out test set and computes error metrics,
    same way we scored the naive baseline, so they're directly comparable.
    """
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target"]

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    return {"mae": round(mae, 2), "rmse": round(rmse, 2)}


if __name__ == "__main__":
    df = fetch_stock_data(ticker="RELIANCE.NS", period="5y")
    df = add_indicators(df)
    df = prepare_dataset(df)

    print(f"Total usable rows: {len(df)}")

    train_df, test_df = train_test_split_chronological(df)
    print(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")

    baseline = naive_baseline_error(test_df)
    print("\nNaive baseline (guess tomorrow = today):")
    print(f"  MAE:  ₹{baseline['mae']}")
    print(f"  RMSE: ₹{baseline['rmse']}")

    model = train_xgboost_model(train_df)
    xgb_result = evaluate_model(model, test_df)
    print("\nXGBoost model:")
    print(f"  MAE:  ₹{xgb_result['mae']}")
    print(f"  RMSE: ₹{xgb_result['rmse']}")

    improvement = ((baseline["mae"] - xgb_result["mae"]) / baseline["mae"]) * 100
    print(f"\nMAE improvement over baseline: {improvement:.1f}%")