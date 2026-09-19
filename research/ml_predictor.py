import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators


# ============================================================
# FEATURE COLUMNS
# ============================================================

FEATURE_COLUMNS = [

    # Original price features
    "open",
    "high",
    "low",
    "close",
    "volume",

    # Technical indicators
    "sma_20",
    "sma_50",
    "ema_20",
    "ema_50",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_histogram",
    "bb_middle",
    "bb_upper",
    "bb_lower",

    # Relative / derived features
    "return_1d",
    "intraday_return",
    "high_low_range",
    "volume_change",
    "sma_20_distance",
    "sma_50_distance",
    "ema_20_distance",
    "ema_50_distance",
    "bb_position",
]


# ============================================================
# ADD RELATIVE FEATURES
# ============================================================

def add_relative_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # --------------------------------------------------------
    # 1. One-day return
    # --------------------------------------------------------

    df["return_1d"] = (
        df["close"].pct_change()
    )

    # --------------------------------------------------------
    # 2. Intraday return
    # --------------------------------------------------------

    df["intraday_return"] = (
        (df["close"] - df["open"])
        / df["open"]
    )

    # --------------------------------------------------------
    # 3. High-Low range
    # --------------------------------------------------------

    df["high_low_range"] = (
        (df["high"] - df["low"])
        / df["close"]
    )

    # --------------------------------------------------------
    # 4. Volume change
    # --------------------------------------------------------

    df["volume_change"] = (
        df["volume"].pct_change()
    )

    # --------------------------------------------------------
    # 5. Distance from SMA 20
    # --------------------------------------------------------

    df["sma_20_distance"] = (
        (df["close"] - df["sma_20"])
        / df["sma_20"]
    )

    # --------------------------------------------------------
    # 6. Distance from SMA 50
    # --------------------------------------------------------

    df["sma_50_distance"] = (
        (df["close"] - df["sma_50"])
        / df["sma_50"]
    )

    # --------------------------------------------------------
    # 7. Distance from EMA 20
    # --------------------------------------------------------

    df["ema_20_distance"] = (
        (df["close"] - df["ema_20"])
        / df["ema_20"]
    )

    # --------------------------------------------------------
    # 8. Distance from EMA 50
    # --------------------------------------------------------

    df["ema_50_distance"] = (
        (df["close"] - df["ema_50"])
        / df["ema_50"]
    )

    # --------------------------------------------------------
    # 9. Bollinger Band position
    # --------------------------------------------------------

    # Avoid division by zero when upper and lower
    # Bollinger Bands are equal.

    band_width = (
        df["bb_upper"] - df["bb_lower"]
    )

    df["bb_position"] = (
        (df["close"] - df["bb_lower"])
        / band_width.replace(0, np.nan)
    )

    return df


# ============================================================
# CREATE TARGET
# ============================================================

def prepare_classification_dataset(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    # ========================================================
    # CREATE TARGET
    # ========================================================

    # Tomorrow's closing price
    df["next_close"] = (
        df["close"].shift(-1)
    )

    # 1 = price goes UP tomorrow
    # 0 = price goes DOWN or stays same
    df["target"] = (
        df["next_close"] > df["close"]
    ).astype(int)

    # ========================================================
    # CLEAN NUMERIC FEATURES
    # ========================================================

    # Convert feature columns to numeric
    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ========================================================
    # REMOVE INFINITE VALUES
    # ========================================================

    # Convert +inf and -inf to NaN
    df[FEATURE_COLUMNS] = (
        df[FEATURE_COLUMNS]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

    # ========================================================
    # REMOVE MISSING VALUES
    # ========================================================

    df.dropna(
        subset=FEATURE_COLUMNS + [
            "next_close",
            "target"
        ],
        inplace=True
    )

    # ========================================================
    # RESET INDEX
    # ========================================================

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df


# ============================================================
# CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

def train_test_split_chronological(
    df: pd.DataFrame,
    train_ratio: float = 0.80
):

    split_index = int(
        len(df) * train_ratio
    )

    train_df = (
        df.iloc[:split_index]
        .copy()
    )

    test_df = (
        df.iloc[split_index:]
        .copy()
    )

    return train_df, test_df


# ============================================================
# NAIVE BASELINE
# ============================================================

def naive_classification_baseline(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
):

    # Find majority class in training data

    majority_class = (
        train_df["target"]
        .mode()[0]
    )

    # Always predict majority class

    predictions = [
        majority_class
    ] * len(test_df)

    accuracy = accuracy_score(
        test_df["target"],
        predictions
    )

    return {
        "accuracy": round(
            accuracy,
            4
        ),
        "majority_class": int(
            majority_class
        ),
    }


# ============================================================
# TRAIN XGBOOST
# ============================================================

def train_classifier(
    train_df: pd.DataFrame
):

    X_train = (
        train_df[FEATURE_COLUMNS]
    )

    y_train = (
        train_df["target"]
    )

    # Regularized XGBoost

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

    model.fit(
        X_train,
        y_train
    )

    return model


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_classifier(
    model,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
):

    # --------------------------------------------------------
    # Training data
    # --------------------------------------------------------

    X_train = (
        train_df[FEATURE_COLUMNS]
    )

    y_train = (
        train_df["target"]
    )

    # --------------------------------------------------------
    # Testing data
    # --------------------------------------------------------

    X_test = (
        test_df[FEATURE_COLUMNS]
    )

    y_test = (
        test_df["target"]
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    train_predictions = (
        model.predict(X_train)
    )

    test_predictions = (
        model.predict(X_test)
    )

    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    test_probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    train_accuracy = accuracy_score(
        y_train,
        train_predictions
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions
    )

    precision = precision_score(
        y_test,
        test_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        test_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        test_predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        test_probabilities
    )

    matrix = confusion_matrix(
        y_test,
        test_predictions
    )

    return {

        "train_accuracy": round(
            train_accuracy,
            4
        ),

        "test_accuracy": round(
            test_accuracy,
            4
        ),

        "precision": round(
            precision,
            4
        ),

        "recall": round(
            recall,
            4
        ),

        "f1": round(
            f1,
            4
        ),

        "roc_auc": round(
            roc_auc,
            4
        ),

        "confusion_matrix":
            matrix.tolist(),
    }


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def print_feature_importance(
    model
):

    importance = pd.Series(
        model.feature_importances_,
        index=FEATURE_COLUMNS
    ).sort_values(
        ascending=False
    )

    print("\n" + "-" * 60)
    print("FEATURE IMPORTANCE")
    print("-" * 60)

    print(importance)


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

def print_target_distributions(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
):

    # --------------------------------------------------------
    # Training distribution
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("TRAINING TARGET DISTRIBUTION")
    print("-" * 60)

    print("\nCounts:")

    print(
        train_df["target"]
        .value_counts()
    )

    print("\nPercentages:")

    train_distribution = (
        train_df["target"]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )

    print(
        train_distribution
    )

    # --------------------------------------------------------
    # Testing distribution
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("TESTING TARGET DISTRIBUTION")
    print("-" * 60)

    print("\nCounts:")

    print(
        test_df["target"]
        .value_counts()
    )

    print("\nPercentages:")

    test_distribution = (
        test_df["target"]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )

    print(
        test_distribution
    )


# ============================================================
# CHECK INFINITE VALUES
# ============================================================

def check_infinite_values(
    df: pd.DataFrame
):

    print("\n" + "-" * 60)
    print("INFINITE VALUE CHECK")
    print("-" * 60)

    inf_counts = (
        df[FEATURE_COLUMNS]
        .isin([
            float("inf"),
            float("-inf")
        ])
        .sum()
    )

    if inf_counts.sum() == 0:

        print(
            "\nNo infinite values found."
        )

    else:

        print(
            "\nInfinite values found:"
        )

        print(
            inf_counts[
                inf_counts > 0
            ]
        )


# ============================================================
# COMPARE XGBOOST CONFIGURATIONS
# ============================================================

def compare_xgboost_configs(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
):

    configs = {

        "A_current": dict(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
        ),

        "B_shallower": dict(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.03,
            random_state=42,
        ),

        "C_regularized": dict(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.03,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
        ),

        "D_very_conservative": dict(
            n_estimators=400,
            max_depth=2,
            learning_rate=0.02,
            min_child_weight=10,
            subsample=0.7,
            colsample_bytree=0.7,
            reg_alpha=0.5,
            reg_lambda=2.0,
            random_state=42,
        ),
    }

    print("\n" + "=" * 60)
    print("XGBOOST CONFIG COMPARISON")
    print("=" * 60)

    results = {}

    for name, params in configs.items():

        model = XGBClassifier(
            **params
        )

        model.fit(
            train_df[FEATURE_COLUMNS],
            train_df["target"]
        )

        eval_result = (
            evaluate_classifier(
                model,
                train_df,
                test_df
            )
        )

        results[name] = (
            eval_result
        )

        gap = (
            eval_result[
                "train_accuracy"
            ]
            -
            eval_result[
                "test_accuracy"
            ]
        )

        print(
            f"\n--- {name} ---"
        )

        print(
            f"Params: {params}"
        )

        print(
            f"Train Accuracy : "
            f"{eval_result['train_accuracy']:.2%}"
        )

        print(
            f"Test Accuracy  : "
            f"{eval_result['test_accuracy']:.2%}"
        )

        print(
            f"Train-Test Gap : "
            f"{gap:+.2%}"
        )

        print(
            f"ROC-AUC        : "
            f"{eval_result['roc_auc']:.4f}"
        )

        print(
            f"F1 Score       : "
            f"{eval_result['f1']:.4f}"
        )

    # --------------------------------------------------------
    # Summary table
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("SUMMARY TABLE")
    print("-" * 60)

    print(
        f"\n{'Config':<22}"
        f"{'Train':>8}"
        f"{'Test':>8}"
        f"{'Gap':>8}"
        f"{'ROC-AUC':>10}"
    )

    for name, result in results.items():

        gap = (
            result["train_accuracy"]
            -
            result["test_accuracy"]
        )

        print(
            f"{name:<22}"
            f"{result['train_accuracy']:>8.2%}"
            f"{result['test_accuracy']:>8.2%}"
            f"{gap:>8.2%}"
            f"{result['roc_auc']:>10.4f}"
        )

    return results


# ============================================================
# WALK-FORWARD VALIDATION
# ============================================================

def walk_forward_validation(
    df: pd.DataFrame,
    n_splits: int = 5,
    min_train_ratio: float = 0.5
):

    total_rows = len(df)

    # --------------------------------------------------------
    # Determine minimum training size and fold test size
    # --------------------------------------------------------

    min_train_size = int(
        total_rows * min_train_ratio
    )

    remaining_rows = (
        total_rows - min_train_size
    )

    test_size = (
        remaining_rows // n_splits
    )

    print("\n" + "=" * 60)
    print("WALK-FORWARD VALIDATION")
    print("=" * 60)

    print(
        f"\nTotal rows        : {total_rows}"
    )

    print(
        f"Min train size    : {min_train_size}"
    )

    print(
        f"Rows per test fold: {test_size}"
    )

    print(
        f"Number of folds   : {n_splits}"
    )

    if test_size < 20:

        print(
            "\nWARNING: test fold size is very small. "
            "Results may be noisy."
        )

    fold_results = []

    # --------------------------------------------------------
    # Loop through expanding-window folds
    # --------------------------------------------------------

    for fold_index in range(n_splits):

        train_end = (
            min_train_size
            + fold_index * test_size
        )

        # Last fold absorbs any remainder rows
        if fold_index == n_splits - 1:
            test_end = total_rows
        else:
            test_end = train_end + test_size

        train_df = df.iloc[:train_end].copy()
        test_df = df.iloc[train_end:test_end].copy()

        if len(test_df) == 0:
            continue

        # ----------------------------------------------------
        # Train and evaluate this fold
        # ----------------------------------------------------

        model = train_classifier(train_df)

        eval_result = evaluate_classifier(
            model,
            train_df,
            test_df
        )

        baseline = naive_classification_baseline(
            train_df,
            test_df
        )

        fold_summary = {
            "fold": fold_index + 1,
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "train_start": train_df["date"].min(),
            "train_end": train_df["date"].max(),
            "test_start": test_df["date"].min(),
            "test_end": test_df["date"].max(),
            "baseline_accuracy": baseline["accuracy"],
            "test_accuracy": eval_result["test_accuracy"],
            "roc_auc": eval_result["roc_auc"],
            "f1": eval_result["f1"],
        }

        fold_results.append(fold_summary)

        print(
            f"\n--- Fold {fold_index + 1} ---"
        )

        print(
            f"Train: {fold_summary['train_start']} "
            f"→ {fold_summary['train_end']} "
            f"({fold_summary['train_rows']} rows)"
        )

        print(
            f"Test:  {fold_summary['test_start']} "
            f"→ {fold_summary['test_end']} "
            f"({fold_summary['test_rows']} rows)"
        )

        print(
            f"Baseline Accuracy : "
            f"{fold_summary['baseline_accuracy']:.2%}"
        )

        print(
            f"Test Accuracy     : "
            f"{fold_summary['test_accuracy']:.2%}"
        )

        print(
            f"ROC-AUC           : "
            f"{fold_summary['roc_auc']:.4f}"
        )

        print(
            f"F1 Score          : "
            f"{fold_summary['f1']:.4f}"
        )

    # --------------------------------------------------------
    # Aggregate across folds
    # --------------------------------------------------------

    accuracies = [
        f["test_accuracy"] for f in fold_results
    ]

    baseline_accuracies = [
        f["baseline_accuracy"] for f in fold_results
    ]

    roc_aucs = [
        f["roc_auc"] for f in fold_results
    ]

    print("\n" + "-" * 60)
    print("WALK-FORWARD SUMMARY")
    print("-" * 60)

    print(
        f"\n{'Fold':<6}"
        f"{'Test Period':<26}"
        f"{'Baseline':>10}"
        f"{'Test Acc':>10}"
        f"{'ROC-AUC':>10}"
    )

    for f in fold_results:

        period = (
            f"{f['test_start'].date()} "
            f"to {f['test_end'].date()}"
        )

        print(
            f"{f['fold']:<6}"
            f"{period:<26}"
            f"{f['baseline_accuracy']:>10.2%}"
            f"{f['test_accuracy']:>10.2%}"
            f"{f['roc_auc']:>10.4f}"
        )

    print(
        f"\nMean Test Accuracy     : "
        f"{np.mean(accuracies):.2%}"
    )

    print(
        f"Std Dev Test Accuracy  : "
        f"{np.std(accuracies):.2%}"
    )

    print(
        f"Mean Baseline Accuracy : "
        f"{np.mean(baseline_accuracies):.2%}"
    )

    print(
        f"Mean ROC-AUC           : "
        f"{np.mean(roc_aucs):.4f}"
    )

    mean_difference = (
        np.mean(accuracies)
        - np.mean(baseline_accuracies)
    )

    print(
        f"\nMean Difference "
        f"(XGBoost - Baseline): "
        f"{mean_difference:+.2%}"
    )

    return fold_results


# ============================================================
# MAIN PREDICTION / DIAGNOSTIC FUNCTION
# ============================================================

def predict_direction(
    ticker: str
):

    print("\n" + "=" * 60)

    print(
        f"AI FDSS MODEL DIAGNOSTIC: "
        f"{ticker}"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # 1. FETCH DATA
    # --------------------------------------------------------

    df = fetch_stock_data(
        ticker=ticker,
        period="5y",
        interval="1d"
    )

    print("\nRaw data:")

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Start: {df['date'].min()}"
    )

    print(
        f"End:   {df['date'].max()}"
    )

    # --------------------------------------------------------
    # 2. ADD TECHNICAL INDICATORS
    # --------------------------------------------------------

    df = add_indicators(
        df
    )

    # --------------------------------------------------------
    # 3. ADD RELATIVE FEATURES
    # --------------------------------------------------------

    df = add_relative_features(
        df
    )

    # --------------------------------------------------------
    # 4. CHECK INFINITE VALUES
    # --------------------------------------------------------

    check_infinite_values(
        df
    )

    # --------------------------------------------------------
    # 5. CREATE TARGET
    # --------------------------------------------------------

    df = prepare_classification_dataset(
        df
    )

    # --------------------------------------------------------
    # 6. TARGET DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("TARGET DISTRIBUTION")
    print("-" * 60)

    print("\nCounts:")

    print(
        df["target"]
        .value_counts()
    )

    print("\nPercentages:")

    target_percentages = (
        df["target"]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .round(2)
    )

    print(
        target_percentages
    )

    # --------------------------------------------------------
    # 7. CHRONOLOGICAL TRAIN / TEST SPLIT
    # --------------------------------------------------------

    train_df, test_df = (
        train_test_split_chronological(
            df,
            train_ratio=0.80
        )
    )

    print("\n" + "-" * 60)
    print("TRAIN / TEST SPLIT")
    print("-" * 60)

    print(
        f"\nTraining rows: "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows:  "
        f"{len(test_df)}"
    )

    print("\nTraining period:")

    print(
        train_df["date"].min(),
        "→",
        train_df["date"].max()
    )

    print("\nTesting period:")

    print(
        test_df["date"].min(),
        "→",
        test_df["date"].max()
    )

    # --------------------------------------------------------
    # 8. TRAIN / TEST TARGET DISTRIBUTIONS
    # --------------------------------------------------------

    print_target_distributions(
        train_df,
        test_df
    )

    # --------------------------------------------------------
    # 9. NAIVE BASELINE
    # --------------------------------------------------------

    baseline = (
        naive_classification_baseline(
            train_df,
            test_df
        )
    )

    print("\n" + "-" * 60)
    print("NAIVE BASELINE")
    print("-" * 60)

    print(
        f"\nAlways predict class "
        f"{baseline['majority_class']}"
    )

    print(
        f"Naive baseline accuracy: "
        f"{baseline['accuracy']:.2%}"
    )

    # --------------------------------------------------------
    # 10. TRAIN XGBOOST
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("TRAINING XGBOOST")
    print("-" * 60)

    model = train_classifier(
        train_df
    )

    print(
        "\nXGBoost training completed."
    )

    # --------------------------------------------------------
    # 11. EVALUATE MODEL
    # --------------------------------------------------------

    results = evaluate_classifier(
        model,
        train_df,
        test_df
    )

    print("\n" + "-" * 60)
    print("XGBOOST RESULTS")
    print("-" * 60)

    print(
        f"\nTrain Accuracy : "
        f"{results['train_accuracy']:.2%}"
    )

    print(
        f"Test Accuracy  : "
        f"{results['test_accuracy']:.2%}"
    )

    print(
        f"Precision      : "
        f"{results['precision']:.4f}"
    )

    print(
        f"Recall         : "
        f"{results['recall']:.4f}"
    )

    print(
        f"F1 Score       : "
        f"{results['f1']:.4f}"
    )

    print(
        f"ROC-AUC        : "
        f"{results['roc_auc']:.4f}"
    )

    print("\nConfusion Matrix:")

    print(
        results["confusion_matrix"]
    )

    # --------------------------------------------------------
    # 12. FEATURE IMPORTANCE
    # --------------------------------------------------------

    print_feature_importance(
        model
    )

    # --------------------------------------------------------
    # 13. BASELINE VS XGBOOST
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("BASELINE VS XGBOOST")
    print("-" * 60)

    print(
        f"\nNaive baseline : "
        f"{baseline['accuracy']:.2%}"
    )

    print(
        f"XGBoost        : "
        f"{results['test_accuracy']:.2%}"
    )

    difference = (
        results["test_accuracy"]
        -
        baseline["accuracy"]
    )

    print(
        f"Difference     : "
        f"{difference:+.2%}"
    )

    # --------------------------------------------------------
    # 14. CONFIGURATION COMPARISON
    # --------------------------------------------------------

    config_results = (
        compare_xgboost_configs(
            train_df,
            test_df
        )
    )

    # --------------------------------------------------------
    # 15. WALK-FORWARD VALIDATION
    # --------------------------------------------------------

    walk_forward_results = (
        walk_forward_validation(
            df,
            n_splits=5,
            min_train_ratio=0.5
        )
    )

    # --------------------------------------------------------
    # 16. LATEST PREDICTION
    # --------------------------------------------------------

    latest_features = (
        df[
            FEATURE_COLUMNS
        ].iloc[[-1]]
    )

    prediction = model.predict(
        latest_features
    )[0]

    probability = model.predict_proba(
        latest_features
    )[0]

    direction = (
        "UP"
        if prediction == 1
        else "DOWN"
    )

    print("\n" + "-" * 60)
    print("LATEST PREDICTION")
    print("-" * 60)

    print(
        f"\nPrediction: "
        f"{direction}"
    )

    print(
        f"DOWN probability: "
        f"{probability[0]:.2%}"
    )

    print(
        f"UP probability:   "
        f"{probability[1]:.2%}"
    )

    print("\n" + "=" * 60)

    return {

        "ticker": ticker,

        "baseline": baseline,

        "model_results": results,

        "prediction": direction,

        "probability_up": round(
            float(probability[1]),
            4
        ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    predict_direction(
        "RELIANCE.NS"
    )