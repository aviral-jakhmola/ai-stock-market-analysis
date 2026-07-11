import pandas as pd


def add_sma(df: pd.DataFrame, period: int, column: str = "close") -> pd.DataFrame:
    """
    Adds a Simple Moving Average column to the DataFrame.
    e.g. add_sma(df, 20) -> adds a column named 'sma_20'
    """
    df[f"sma_{period}"] = df[column].rolling(window=period).mean()
    return df


def add_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.DataFrame:
    """
    Adds an Exponential Moving Average column to the DataFrame.
    e.g. add_ema(df, 50) -> adds a column named 'ema_50'
    """
    df[f"ema_{period}"] = df[column].ewm(span=period, adjust=False).mean()
    return df


def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the standard set of moving averages used for trend analysis.
    """
    df = add_sma(df, 20)
    df = add_sma(df, 50)
    df = add_ema(df, 20)
    df = add_ema(df, 50)
    return df

def add_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.DataFrame:
    """
    Adds a Relative Strength Index column to the DataFrame.
    Values range from 0-100. Common thresholds: >70 overbought, <30 oversold.
    """
    delta = df[column].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Wilder's smoothing method (a specific form of EMA)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df[f"rsi_{period}"] = rsi
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the full set of technical indicators used across the app.
    """
    df = add_sma(df, 20)
    df = add_sma(df, 50)
    df = add_ema(df, 20)
    df = add_ema(df, 50)
    df = add_rsi(df, 14)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    return df

def add_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.DataFrame:
    """
    Adds MACD line, signal line, and histogram columns.
    """
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_histogram"] = histogram
    return df


def add_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    num_std: int = 2,
    column: str = "close",
) -> pd.DataFrame:
    """
    Adds Bollinger Bands: upper, middle (SMA), and lower.
    """
    middle = df[column].rolling(window=period).mean()
    std = df[column].rolling(window=period).std()

    df["bb_middle"] = middle
    df["bb_upper"] = middle + (num_std * std)
    df["bb_lower"] = middle - (num_std * std)
    return df