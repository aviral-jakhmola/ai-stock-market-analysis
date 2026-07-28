# AI Stock Market Decision Support System (AI FDSS)

[![Backend Tests](https://github.com/aviral-jakhmola/ai-stock-market-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/aviral-jakhmola/ai-stock-market-analysis/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Frontend Deployed](https://img.shields.io/badge/Frontend-Vercel-success)](https://ai-stock-market-analysis-nine.vercel.app/)
[![Backend Deployed](https://img.shields.io/badge/Backend-Railway-blue)](https://ai-stock-market-analysis-production.up.railway.app/)

An intelligent, full-stack stock analysis platform combining technical indicators, machine learning direction classification, and financial news sentiment analysis (NLP) into a unified, explainable decision-support dashboard.

---

## 📈 Project Overview

AI FDSS is an AI-powered stock market decision support system that combines:

- Technical indicators
- Company fundamentals
- Financial news sentiment analysis using FinBERT via the Hugging Face Inference API
- XGBoost trend prediction
- Explainable recommendation engine

Instead of predicting exact prices, the system predicts market direction and combines multiple independent signals into an explainable BUY/HOLD/SELL recommendation.

---

## 🚀 Features

- 📈 Interactive stock dashboard with candlestick and volume charts
- 📊 Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- 🤖 XGBoost-based market direction prediction
- 📰 Financial news sentiment analysis using FinBERT via the Hugging Face Inference API
- 🧠 Explainable weighted BUY / HOLD / SELL recommendation engine
- 🔐 JWT authentication with protected routes
- ⭐ Personalized watchlist and search history
- 🐳 Dockerized deployment with CI/CD

---

## 🔗 Demo
- **Live Application Link**: [https://ai-stock-market-analysis-nine.vercel.app](https://ai-stock-market-analysis-nine.vercel.app/)
- **Frontend SPA Hosting**: Deployed on Vercel [https://ai-stock-market-analysis-nine.vercel.app](https://ai-stock-market-analysis-nine.vercel.app/)
- **Backend API Hosting**: Deployed via Docker on Railway [https://ai-stock-market-analysis-production.up.railway.app](https://ai-stock-market-analysis-production.up.railway.app/)
- **Video Walkthrough**: https://youtu.be/awsn62pvgnk

---

## 📸 Screenshots

### Dashboard Overview
<p align="center">
  <img src="docs/screenshots/dashboard_overview.png" width="90%">
</p>

### Market Analysis
<p align="center">
  <img src="docs/screenshots/candlestick_chart.png" width="90%">
</p>

### AI Recommendation
<p align="center">
  <img src="docs/screenshots/final_recommendation.png" width="90%">
</p>

### Explainable AI

#### Technical Recommendation

<p align="center">
<img src="docs/screenshots/technical_recommendation.png" width="85%">
</p>

#### ML Prediction

<p align="center">
<img src="docs/screenshots/ml_prediction.png" width="70%">
</p>

#### News Sentiment

<p align="center">
<img src="docs/screenshots/news_sentiment.png" width="85%">
</p>

## 🛠 Tech Stack

| Category | Technology Used |
| :--- | :--- |
| **Frontend** | React, Vite, Tailwind CSS, ApexCharts, Lucide Icons  |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy ORM  |
| **Machine Learning** | XGBoost (Classifier), PyTorch (CPU-optimized), Hugging Face Transformers (FinBERT), Scikit-Learn, Pandas, NumPy  |
| **Database** | MySQL (Production), In-memory SQLite with StaticPool (Testing)  |
| **Authentication** | JWT (python-jose), bcrypt (passlib)  |
| **DevOps & CI/CD**| Docker, Docker Compose, GitHub Actions  |
| **Testing** | Pytest (Backend), Vitest (Frontend)  |
| **Deployment** | Railway (Backend & MySQL database), Vercel (Frontend)  |

---

## 📐 System Architecture


````mermaid
graph TD
    User[User / Client Browser]
    
    subgraph Vercel_Frontend ["Vite + React SPA (Vercel)"]
        UI[Dashboard / UI Components]
        AxiosClient[Axios Service API layer]
        AuthContext[React AuthContext & Route Guards]
    end

    subgraph Railway_Backend ["FastAPI Server (Railway)"]
        API[FastAPI Endpoints / APIRouter]
        CORS[CORS Middleware]
        Dependency[get_current_user Token Dependency]
        
        subgraph Services [Business Logic Services]
            Fetcher[yfinance Stock Data Fetcher]
            Overview[Fundamental Overview Service]
            Indicators[Pandas Technical Indicators Engine]
            MLPredictor[XGBoost Directional Classifier]
            NLP[FinBERT Sentiment Scraper & Pipeline]
            Ensemble[Weighted Ensemble Decision Engine]
        end
    end

    subgraph Database_Layer ["MySQL Instance (Railway)"]
        UsersDB[(MySQL users table)]
        WatchDB[(MySQL watchlist table)]
        HistoryDB[(MySQL search_history table)]
    end

    subgraph External_APIs [Third-Party Data Sources]
        YahooFinance[Yahoo Finance Public Endpoints]
        HF[Hugging Face Hub Model Weights]
    end

    User <-->|HTTP / JWT / HTTPS| UI
    UI <--> AxiosClient
    AxiosClient <-->|Axios Requests / JSON| API
    API --> CORS
    API --> Dependency
    Dependency -->|Verify JWT| Database_Layer
    API --> Services
    
    Fetcher -->|Historical Price Candles| YahooFinance
    Overview -->|Company Metadata| YahooFinance
    NLP -->|Recent News Scrapes| YahooFinance
    NLP -->|Model Weights Cached| HF
    
    MLPredictor -->|Train XGBoost on OHLCV| Indicators
    Ensemble -->|Aggregate Signals| Indicators
    Ensemble -->|Aggregate Signals| MLPredictor
    Ensemble -->|Aggregate Signals| NLP
    
    API <-->|Query / Persist User Data| Database_Layer
````

---

## 📁 Project Structure

```text
ai-stock-market-analysis/
├──research/
|   └── lstm_predictor.py  # Initial LSTM experiment (kept for reference)
├── .github/workflows/    # CI/CD Workflows (ci.yml)
├── backend/
│   ├── app/
│   │   ├── auth/         # JWT & Password Security (dependencies.py, security.py)
│   │   ├── models/       # SQLAlchemy Database Models (user.py, watchlist.py, search_history.py)
│   │   ├── routers/      # REST Endpoints (auth.py, stocks.py, watchlist.py, search_history.py)
│   │   ├── schemas/      # Pydantic Schemas (user.py, stock.py, watchlist.py, search_history.py)
│   │   ├── services/     # Core Logic (ensemble.py, sentiment.py, indicators.py, ml_predictor.py)
│   │   └── main.py       # FastAPI App Entry & Startup DB Initialization
│   ├── tests/            # Pytest Suite (conftest.py, test_conftest_sanity.py)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI (FinalRecommendationCard, SentimentCard, WatchlistButton)
│   │   ├── context/      # React Context State (AuthContext.jsx)
│   │   ├── pages/        # Route Views (Dashboard.jsx, Login.jsx, Register.jsx, Profile.jsx)
│   │   └── services/     # Axios API Integrations (api.js)
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml    # Multi-container orchestration (MySQL + Backend + Frontend)
```

---

## 📥 Installation & Setup

### Prerequisite Checklist
Ensure your local host machine has the following tools installed:
- [Git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/downloads/)
- [Node.js (v18+)](https://nodejs.org/)
- [MySQL Server](https://dev.mysql.com/downloads/installer/) (or Docker)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/aviral-jakhmola/ai-stock-market-analysis.git
cd ai-stock-market-analysis
```

---

### Step 2: Backend Setup
1. **Initialize Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=mysql+pymysql://root:yourpassword@127.0.0.1:3306/ai_fdss
   SECRET_KEY=your_generated_jwt_secret_signing_key_here
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
4. **Database Initialization**:
   Create the target database in your local MySQL Server:
   ```sql
   CREATE DATABASE ai_fdss;
   ```
   *Note: On backend startup, the FastAPI server will automatically call `init_db()` and instantiate the SQL schemas (users, watchlist, search_history) with no manual SQL scripts required.*

5. **Run the Backend locally**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Verify the API server is active by opening your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI).

---

### Step 3: Frontend Setup
1. **Navigate to directory**:
   ```bash
   cd ../frontend
   ```
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```
4. **Run the Frontend locally**:
   ```bash
   npm run dev
   ```
   Open your browser to [http://localhost:5173](http://localhost:5173).

---

### Step 4: Docker Compose Orchestration (Alternative Local Run)
To fire up the entire multi-service stack (Database, Backend, Frontend) with a single command:
1. Ensure Docker is running.
2. In the project root, create a `.env` file:
   ```env
   MYSQL_ROOT_PASSWORD=aviraljak
   MYSQL_DATABASE=ai_fdss
   SECRET_KEY=your_production_jwt_signing_key
   ```
3. Boot the environment:
   ```bash
   docker compose up --build
   ```
   The local services will map as follows:
   - React Frontend SPA: [http://localhost:5173](http://localhost:5173)
   - FastAPI Backend Server: [http://localhost:8000](http://localhost:8000)
   - MySQL Instance: `localhost:3307` (mapped internally to standard MySQL port `3306`)

---




## 🤖 AI Pipeline

The predictive backbone of AI FDSS is built on a split quantitative design, combining tree classification (XGBoost), deep NLP sentiment (FinBERT), and traditional rule-based algorithms.

```
+--------------------+
| 5-Year Equity Data |
+----------+---------+
           |
           v
+----------+---------+
| Pandas Calc Engine | ---> SMA, EMA, RSI, MACD, Bollinger Bands
+----------+---------+
           |
           v
+----------+---------+
| Feature Engineering| ---> 16 tabular features
+----------+---------+
           |
           +----------------------------------------+
           |                                        |
           v (Chronological Split)                  v (Financial News)
+----------+---------+              +---------------+---------------+  
|  Train / Test Sets |              |      FinBERT Sentiment        |    
+----------+---------+              |  (Hugging Face Inference API) |
           |                        +---------------+---------------+
           v (XGBoost Trainer)                      |
+----------+---------+                              |
| Model Evaluation   |                              |
| (Accuracy ~51%)    |                              |
+----------+---------+                              |
           |                                        |
           v                                        v
+----------+----------------------------------+--------+
|                    XGBoost Classifier                |
+------------------------------+-----------------------+
                               |
                               v (Outputs Up/Down Probability)
                         [ UP: 51.5% ]
```


## 🛡️ API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/auth/register` | Creates a new user account (min 8-char password check)  | No |
| **POST** | `/api/auth/login` | Form-encoded login verifying credentials and issuing JWT  | No |
| **GET** | `/api/auth/me` | Returns the profile details of the current logged-in user  | Yes (Bearer Token) |
| **GET** | `/api/stocks/company/{symbol}` | Fetches company sector, market cap, and trading bounds  | No |
| **GET** | `/api/stocks/{ticker}/history` | Exposes historical OHLCV data for charts  | No |
| **GET** | `/api/stocks/{ticker}/sentiment` | Running inference via FinBERT to analyze news headlines  | No |
| **GET** | `/api/stocks/{ticker}/predict` | Feeds indicators into XGBoost to output direction trend  | No |
| **GET** | `/api/stocks/{ticker}/final-recommendation` | Computes the unified final weighted investment rating  | No |
| **GET** | `/api/watchlist` | Lists all tickers saved to the user's watchlist  | Yes (Bearer Token) |
| **POST** | `/api/watchlist` | Adds a new ticker symbol to the user's profile  | Yes (Bearer Token) |
| **DELETE** | `/api/watchlist/{item_id}` | Removes a ticker symbol from the active watchlist  | Yes (Bearer Token) |
| **GET** | `/api/search-history` | Retrieves logged search history entries (max 10)  | Yes (Bearer Token) |

---

## 🔐 Authentication & Security Flow

- JWT-based authentication
- bcrypt password hashing
- Protected API routes
- Automatic logout on expired tokens

---

## 🧪 Testing Suite

The project includes automated testing for both the backend and frontend to ensure reliability and prevent regressions.

### Backend
- **Framework:** Pytest
- Tests API endpoints, authentication, watchlist, search history, and recommendation logic.
- Uses an isolated in-memory SQLite database for fast and independent test execution.

Run backend tests:

```bash
cd backend
pytest
```

### Frontend
- **Framework:** Vitest + React Testing Library
- Tests component rendering, authentication flow, protected routes, and user interactions.

Run frontend tests:

```bash
cd frontend
npm run test
```

### Test Coverage
- ✅ 133 automated unit and integration tests
- ✅ Backend and frontend tests run automatically through **GitHub Actions** on every push and pull request.

---

## 🚀 DevOps, CI/CD, and Cloud Deployments

- Backend containerized using Docker and deployed on Railway
- Frontend deployed on Vercel
- CI/CD automated using GitHub Actions
- Automatic database initialization during backend startup
- Environment variables securely managed through Railway, Vercel, and GitHub Secrets
- FinBERT inference performed through the Hugging Face Inference API to minimize backend memory usage

---

## 🛠 Challenges & Design Decisions

### 1. LSTM → XGBoost
- **Challenge:** LSTM price prediction produced low error but failed to outperform a simple baseline due to the difficulty of forecasting exact prices.
- **Solution:** Switched to an **XGBoost classifier** that predicts market direction (UP/DOWN), providing probability-based and more interpretable results.

### 2. Production Memory Constraints

- **Challenge:** Hosting the FinBERT transformer locally exceeded Railway's 1 GB memory limit, making production deployment unreliable.
- **Solution:** Redesigned the sentiment analysis pipeline to use the Hugging Face Inference API instead of loading the transformer model inside the backend.

### 3. Asynchronous AI Pipeline

- **Challenge:** Migrating the sentiment analysis service from local inference to an external API required asynchronous network requests, which initially caused runtime errors due to mixed synchronous and asynchronous code.
- **Solution:** Refactored the entire sentiment pipeline to use Python's async/await pattern consistently across the FastAPI routes, sentiment service, and ensemble recommendation engine.

### 4. Production Database Initialization
- **Challenge:** Missing database tables caused backend startup failures that appeared as CORS errors in the frontend.
- **Solution:** Added automatic `init_db()` execution on application startup to create tables when needed.

### 5. CI Testing
- **Challenge:** The startup database initialization interfered with automated tests by attempting to connect to the production database.
- **Solution:** Mocked `init_db()` during testing, allowing the test suite to run entirely against an in-memory SQLite database.

---

## 🔮 Future Improvements

1. **Websocket Real-Time Order-Book Tickers**: Shift from delayed REST polling to persistent WebSocket connections (such as Zerodha Kite Connect or broker APIs) to support real-time price updates.
2. **Macroeconomic Indicators Integration**: Integrate macroeconomic anchors (interest rates, CPI, inflation data, and USD/INR exchange rates) via Alpha Vantage to improve prediction accuracy on medium-term horizons.
3. **Advanced Portfolio Backtesting Simulator**: Create a "paper trading" simulation engine with historical backtesting to let users test strategy yields over different chronological market regimes.

---


## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ✍️ Author
**Aviral Jakhmola**
- GitHub: [@aviral-jakhmola](https://github.com/aviral-jakhmola)
- LinkedIn: https://www.linkedin.com/in/aviral-jakhmola-a23987333/