import numpy as np
import pandas as pd
import torch
import torch.nn as nn  # <-- Fixes the NameError!
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators

# ==========================================
# CONFIGURATION & FEATURE COLUMNS
# ==========================================
FEATURE_COLUMNS = [
    "open", "high", "low", "close", "volume",
    "sma_20", "sma_50", "ema_20", "ema_50",
    "rsi_14",
    "macd", "macd_signal", "macd_histogram",
    "bb_middle", "bb_upper", "bb_lower",
]
WINDOW_SIZE = 20  # Lookback window (20 consecutive trading days)

# ==========================================
# STAGE 1: DATA PREPARATION & SEQUENCE RESHAPING
# ==========================================
def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Target = tomorrow's % return, not raw price.
    Also converts price-level features into % change so the model
    isn't fed non-stationary raw prices (MinMax scaling alone doesn't fix this).
    """
    df = df.copy()
    next_close = df["close"].shift(-1)
    df["target"] = (next_close - df["close"]) / df["close"]

    # Convert absolute price-level columns into % change from the previous day.
    # RSI, MACD, and MACD signal/histogram are already oscillator-style and
    # roughly stationary, so they're left as-is.
    price_level_cols = [
        "open", "high", "low", "close",
        "sma_20", "sma_50", "ema_20", "ema_50",
        "bb_middle", "bb_upper", "bb_lower",
    ]
    for col in price_level_cols:
        df[col] = df[col].pct_change()

    df = df.dropna()
    return df

def create_sequences(features: np.ndarray, targets: np.ndarray, window: int):
    """
    Slides a window across the matrix: 'last `window` days of features' 
    -> 'next day's target return'.
    """
    X, y = [], []
    for i in range(len(features) - window):
        X.append(features[i : i + window])
        y.append(targets[i + window])
    return np.array(X), np.array(y)

# ==========================================
# STAGE 2: THE LSTM PRICE PREDICTOR MODEL
# ==========================================
class LSTMPricePredictor(nn.Module):
    def __init__(self, num_features: int, hidden_size: int = 16):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=num_features,
            hidden_size=hidden_size,
            batch_first=True,  # Shape: (batch, sequence, features)
        )
        self.dropout = nn.Dropout(0.2)  # Fights overfitting on small data rows
        self.fc = nn.Linear(hidden_size, 1)  # Maps final day memory summary to 1 target return
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]  # Extract only the 20th day summary vector
        last_hidden = self.dropout(last_hidden)
        prediction = self.fc(last_hidden)
        return prediction

# ==========================================
# STAGE 3: TRAINING LOOP WITH VALIDATION & EARLY STOPPING
# ==========================================
def train_lstm(X_train, y_train, num_epochs: int = 60, batch_size: int = 32, lr: float = 0.001):
    """
    Trains the LSTM with chronological validation splits to detect overfitting.
    """
    # 90/10 Chronological Train/Val split to monitor real-time loss deviation
    val_split = int(len(X_train) * 0.9)
    X_tr, X_val = X_train[:val_split], X_train[val_split:]
    y_tr, y_val = y_train[:val_split], y_train[val_split:]
    
    # Convert arrays to PyTorch Float32 tensors
    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)
    X_val_t = torch.tensor(X_val, dtype=torch.float32)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)
    
    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    model = LSTMPricePredictor(num_features=X_train.shape[2], hidden_size=16)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    best_val_loss = float('inf')
    best_model_weights = None
    patience = 7
    patience_counter = 0
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        # Validation Evaluation Step
        model.eval()
        with torch.no_grad():
            val_predictions = model(X_val_t)
            val_loss = criterion(val_predictions, y_val_t).item()
            
        avg_train_loss = train_loss / len(loader)
        
        # Early Stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_weights = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            
        if (epoch + 1) % 5 == 0 or patience_counter == patience:
            print(f"Epoch {epoch + 1:02d} | Train MSE: {avg_train_loss:.6f} | Val MSE: {val_loss:.6f}")
            
        if patience_counter >= patience:
            print(f"🛑 Early stopping triggered at epoch {epoch + 1}. Restoring best weights.")
            break
            
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)
        
    return model

def evaluate_lstm(model, X_test, y_test) -> dict:
    """
    Evaluates the model against held-out test frames.
    """
    model.eval()
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    with torch.no_grad():
        predictions = model(X_test_t).squeeze().numpy()
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    return {"mae": round(mae, 5), "rmse": round(rmse, 5)}

# ==========================================
# EXECUTION INTERFACE
# ==========================================
if __name__ == "__main__":
    df = fetch_stock_data(ticker="RELIANCE.NS", period="5y")
    df = add_indicators(df)
    df = prepare_dataset(df)
    
    split_index = int(len(df) * 0.8)
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    
    # MinMaxScaler tracking to prevent data leakage
    scaler = MinMaxScaler()
    train_features_scaled = scaler.fit_transform(train_df[FEATURE_COLUMNS])
    test_features_scaled = scaler.transform(test_df[FEATURE_COLUMNS])
    
    X_train, y_train = create_sequences(train_features_scaled, train_df["target"].values, WINDOW_SIZE)
    X_test, y_test = create_sequences(test_features_scaled, test_df["target"].values, WINDOW_SIZE)
    
    print(f"Train sequences: {X_train.shape}")
    print(f"Test sequences:  {X_test.shape}")
    
    # Naive Honest Benchmark
    naive_mae = mean_absolute_error(y_test, [0] * len(y_test))
    naive_rmse = mean_squared_error(y_test, [0] * len(y_test)) ** 0.5
    print(f"\n📋 Naive Baseline (0% Return Guess): MAE={naive_mae:.5f}, RMSE={naive_rmse:.5f}")
    
    print("\n🚀 Training Validation-Aware LSTM...")
    model = train_lstm(X_train, y_train, num_epochs=60)
    result = evaluate_lstm(model, X_test, y_test)
    
    print(f"\n🎯 Optimized LSTM: MAE={result['mae']}, RMSE={result['rmse']}")
    improvement = ((naive_mae - result["mae"]) / naive_mae) * 100
    print(f"📊 MAE Improvement over Baseline: {improvement:.1f}%")