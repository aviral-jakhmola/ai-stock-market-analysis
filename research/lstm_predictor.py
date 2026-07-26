import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.services.data_fetcher import fetch_stock_data
from app.services.indicators import add_indicators

# ==========================================
# CONFIGURATION & FEATURES
# ==========================================
FEATURE_COLUMNS = [
    "close_return",       # Asset's own return momentum
    "volume",
    "rsi_14",
    "macd_histogram",
    "lag_1_return",
    "lag_2_return",
    "volatility_10",      # Asset rolling volatility
    "market_return",      # NIFTY 50 Index Return (Macro Anchor 1)
    "market_vol_10"       # NIFTY 50 Volatility Context (Macro Anchor 2)
]

WINDOW_SIZE = 20
HORIZON = 1

# ==========================================
# DATA PREPARATION (EXPERIMENTS 1 & 2 SECURED)
# ==========================================
def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preserves Experiment 1 (NIFTY Context) and Experiment 2 (EWMA Smooth Target)
    to establish a consistent baseline for our architectural upgrade.
    """
    df = df.copy()
    
    # 1. Base Feature Engineering (Asset stats)
    df["close_return"] = df["close"].pct_change()
    df["lag_1_return"] = df["close_return"].shift(1)
    df["lag_2_return"] = df["close_return"].shift(2)
    df["volatility_10"] = df["close_return"].rolling(window=10).std()
    
    # 2. Fetch and merge Macro Benchmark (NIFTY 50) data cleanly
    print("🌐 Fetching NIFTY 50 Index Context for Market Anchor...")
    market_df = fetch_stock_data(ticker="^NSEI", period="5y")
    market_df = market_df[["close"]].copy().rename(columns={"close": "market_close"})
    
    # Align via date indexes
    df = df.join(market_df, how="inner")
    
    # 3. Engine Macro features
    df["market_return"] = df["market_close"].pct_change()
    df["market_vol_10"] = df["market_return"].rolling(window=10).std()
    
    # 4. EXPERIMENT 2 TARGET MATH: 3-day forward EWMA return smoothing
    df["fwd_return_1"] = df["close_return"].shift(-1)
    df["fwd_return_2"] = df["close_return"].shift(-2)
    df["fwd_return_3"] = df["close_return"].shift(-3)
    
    df["target"] = (df["fwd_return_1"] * 0.50) + (df["fwd_return_2"] * 0.33) + (df["fwd_return_3"] * 0.17)
    
    df = df.drop(columns=["fwd_return_1", "fwd_return_2", "fwd_return_3"])
    df = df.dropna()
    return df

def create_sequences(features: np.ndarray, targets: np.ndarray, window: int):
    X, y = [], []
    for i in range(len(features) - window):
        X.append(features[i : i + window])
        y.append(targets[i + window])
    return np.array(X), np.array(y)

# ==========================================
# RE-ENGINEERED BI-DIRECTIONAL LSTM MODEL (EXP 3)
# ==========================================
class LSTMPricePredictor(nn.Module):
    def __init__(self, num_features: int, hidden_size: int = 16):
        super().__init__()
        # Set hidden size and activate bidirectional logic
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(
            input_size=num_features,
            hidden_size=hidden_size,
            batch_first=True,
            num_layers=1,
            bidirectional=True  # <-- ACTIVATES EXPERIMENT 3 parallel time channels
        )
        self.dropout = nn.Dropout(0.3) # Increased dropout to control expanded capacity
        
        # CRITICAL CHANGE: Because it's bidirectional, the output tensor width 
        # from the hidden layers is doubled (hidden_size * 2).
        self.fc = nn.Linear(hidden_size * 2, 1)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        
        # Gather the final chronological step for the forward pass 
        # and the first step for the backward pass automatically via slicing.
        last_hidden = lstm_out[:, -1, :]  
        
        last_hidden = self.dropout(last_hidden)
        prediction = self.fc(last_hidden)
        return prediction

# ==========================================
# TRAINING IMPLEMENTATION WITH PLATEAU SCHEDULER
# ==========================================
def train_lstm(X_train, y_train, num_epochs: int = 80, batch_size: int = 32, lr: float = 0.002):
    val_split = int(len(X_train) * 0.9)
    X_tr, X_val = X_train[:val_split], X_train[val_split:]
    y_tr, y_val = y_train[:val_split], y_train[val_split:]
    
    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)
    X_val_t = torch.tensor(X_val, dtype=torch.float32)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)
    
    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # hidden_size scaled down slightly to 16 since Bi-LSTM naturally doubles layer variables
    model = LSTMPricePredictor(num_features=X_train.shape[2], hidden_size=16)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=4)
    
    best_val_loss = float('inf')
    best_model_weights = None
    patience = 12  
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
            
        model.eval()
        with torch.no_grad():
            val_predictions = model(X_val_t)
            val_loss = criterion(val_predictions, y_val_t).item()
            
        avg_train_loss = train_loss / len(loader)
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_weights = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            
        if (epoch + 1) % 5 == 0 or patience_counter == patience:
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Epoch {epoch + 1:02d} | Train MSE: {avg_train_loss:.6f} | Val MSE: {val_loss:.6f} | LR: {current_lr:.5f}")
            
        if patience_counter >= patience:
            print(f"🛑 Early stopping triggered at epoch {epoch + 1}. Restoring best weights.")
            break
            
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)
        
    return model

def evaluate_lstm(model, X_test, y_test) -> dict:
    model.eval()
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    with torch.no_grad():
        predictions = model(X_test_t).squeeze().numpy()
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    return {"mae": round(mae, 5), "rmse": round(rmse, 5)}

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    df = fetch_stock_data(ticker="RELIANCE.NS", period="5y")
    df = add_indicators(df)
    df = prepare_dataset(df)
    
    split_index = int(len(df) * 0.8)
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    
    scaler = MinMaxScaler()
    train_features_scaled = scaler.fit_transform(train_df[FEATURE_COLUMNS])
    test_features_scaled = scaler.transform(test_df[FEATURE_COLUMNS])
    
    X_train, y_train = create_sequences(train_features_scaled, train_df["target"].values, WINDOW_SIZE)
    X_test, y_test = create_sequences(test_features_scaled, test_df["target"].values, WINDOW_SIZE)
    
    print(f"\nTrain sequences (Bi-LSTM structural inputs): {X_train.shape}")
    print(f"Test sequences:  {X_test.shape}")
    
    # Baseline configuration preserved
    naive_mae = mean_absolute_error(y_test, [0] * len(y_test))
    naive_rmse = mean_squared_error(y_test, [0] * len(y_test)) ** 0.5
    print(f"📋 Naive Baseline (0% Return Guess): MAE={naive_mae:.5f}, RMSE={naive_rmse:.5f}")
    
    print("\n🚀 Training Full Bi-Directional Macro-Anchored LSTM...")
    model = train_lstm(X_train, y_train, num_epochs=80)
    result = evaluate_lstm(model, X_test, y_test)
    
    print(f"\n🎯 Bi-LSTM Final Results: MAE={result['mae']}, RMSE={result['rmse']}")
    improvement = ((naive_mae - result["mae"]) / naive_mae) * 100
    print(f"📊 MAE Improvement over Baseline: {improvement:.1f}%")