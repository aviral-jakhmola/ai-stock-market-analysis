import { useState } from "react";
import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import DashboardCard from "./components/DashboardCard";
import CandlestickChart from "./components/CandlestickChart";
import VolumeChart from "./components/VolumeChart";
import LoadingSpinner from "./components/LoadingSpinner";
import StockData from "./components/StockData";
import api from "./services/api";
import RSIChart from "./components/RSIChart";
import MACDChart from "./components/MACDChart";
import RecommendationCard from "./components/RecommendationCard";
import CompanyOverview from "./components/CompanyOverview";
import SentimentCard from "./components/SentimentCard";
import PredictionCard from "./components/PredictionCard";

const TIMEFRAMES = ["1M", "3M", "6M", "1Y", "5Y"];

const formatINR = (value) =>
    `₹${value.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;

function App() {
    const [stockData, setStockData] = useState([]);
    const [recommendation, setRecommendation] = useState(null);
    const [loading, setLoading] = useState(false);
    const [ticker, setTicker] = useState(null);
    const [timeframe, setTimeframe] = useState("1Y");
    const [companyData, setCompanyData] = useState(null);
    const [sentiment, setSentiment] = useState(null);
    const [prediction, setPrediction] = useState(null);

    const fetchStock = async (symbol, tf) => {
        setLoading(true);
        try {
            const [historyRes, recRes, companyRes, sentimentRes, predictionRes] = await Promise.all([
                api.get(`/api/stocks/${symbol}/history?timeframe=${tf}`),
                api.get(`/api/stocks/${symbol}/recommendation?timeframe=${tf}`),
                api.get(`/api/stocks/company/${symbol}`),
                api.get(`/api/stocks/${symbol}/sentiment`),
                api.get(`/api/stocks/${symbol}/predict`),
            ]);
            setStockData(historyRes.data);
            setRecommendation(recRes.data);
            setCompanyData(companyRes.data);
            setSentiment(sentimentRes.data);
            setPrediction(predictionRes.data);
        } catch (error) {
            console.error(error);
            alert("Unable to fetch stock data.");
        } finally {
            setLoading(false);
        }
    };

    const searchStock = (symbol) => {
        setTicker(symbol);
        fetchStock(symbol, timeframe);
    };

    const changeTimeframe = (tf) => {
        setTimeframe(tf);
        if (ticker) fetchStock(ticker, tf);
    };

    const latest = stockData.length > 0
        ? stockData[stockData.length - 1]
        : null;

    const previous = stockData.length > 1
        ? stockData[stockData.length - 2]
        : null;

    const trend = latest && previous
        ? latest.close > previous.close
            ? "up"
            : latest.close < previous.close
            ? "down"
            : "neutral"
        : "neutral";

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
            <Navbar />

            <div className="px-4 sm:px-6 lg:px-8 py-5 max-w-7xl mx-auto">
                
                {/* Unified Query & Scope Controls Section */}
                <div className="flex flex-col lg:flex-row gap-6 items-start mb-6">
                    
                    {/* Left Stack: Search Field Container + Bold Timeframe Selectors */}
                    <div className="flex flex-col gap-3 w-full lg:w-96 shrink-0">
                        <SearchBar onSearch={searchStock} />
                        
                        {/* Upsized & expanded Segmented Tab Bar strip */}
                        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-xl border border-gray-200 dark:border-gray-700 w-full">
                            {TIMEFRAMES.map((tf) => (
                                <button
                                    key={tf}
                                    onClick={() => changeTimeframe(tf)}
                                    disabled={!ticker || loading}
                                    className={`flex-1 text-center px-4 py-2 rounded-lg text-sm font-semibold transition-all
                                        disabled:opacity-40 disabled:cursor-not-allowed
                                        ${
                                            timeframe === tf
                                                ? "bg-blue-600 text-white shadow-md shadow-blue-500/10"
                                                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700/50"
                                        }`}
                                >
                                    {tf}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Right Stack: ML Direction Prediction Module */}
                    <div className="flex-1 w-full">
                        <PredictionCard data={prediction} />
                    </div>
                </div>

                {/* Main Dynamic Workspace Section */}
                {loading ? (
                    <div className="py-20">
                        <LoadingSpinner />
                    </div>
                ) : (
                    <>
                        {/* Auto-Responsive 4-Column Statistics Grid Matrix */}
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mt-5">
                            <DashboardCard
                                title="Current Price"
                                value={latest ? formatINR(latest.close) : "--"}
                                trend={trend}
                            />
                            <DashboardCard
                                title="High"
                                value={latest ? formatINR(latest.high) : "--"}
                                trend={trend}
                            />
                            <DashboardCard
                                title="Low"
                                value={latest ? formatINR(latest.low) : "--"}
                                trend={trend}
                            />
                            <DashboardCard
                                title="Volume"
                                value={latest ? latest.volume.toLocaleString() : "--"}
                            />
                        </div>

                        {/* Analysis Insight Deliverables */}
                        <RecommendationCard recommendation={recommendation} />
                        <CompanyOverview data={companyData} />
                        <SentimentCard data={sentiment} />

                        {/* Interactive Visualizations Block */}
                        <div className="flex flex-col gap-6 mt-6">
                            <CandlestickChart data={stockData} />
                            <VolumeChart data={stockData} />
                            <RSIChart data={stockData} />
                            <MACDChart data={stockData} />
                            <StockData data={stockData} />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default App;