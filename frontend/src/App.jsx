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

const TIMEFRAMES = ["1M", "3M", "6M", "1Y", "5Y"];

const formatINR = (value) =>
    `₹${value.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;

function App() {
    const [stockData, setStockData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [ticker, setTicker] = useState(null);
    const [timeframe, setTimeframe] = useState("1Y");

    const fetchStock = async (symbol, tf) => {
        setLoading(true);
        try {
            const response = await api.get(
                `/api/stocks/${symbol}/history?timeframe=${tf}`
            );
            setStockData(response.data);
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

    // Grab the most recent record for the summary cards
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

                <SearchBar onSearch={searchStock} />

                {loading ? (
                    <LoadingSpinner />
                ) : (
                    <>
                        {/* Timeframe buttons */}
                        <div className="flex gap-2 mt-5 flex-wrap">
                            {TIMEFRAMES.map((tf) => (
                                <button
                                    key={tf}
                                    onClick={() => changeTimeframe(tf)}
                                    disabled={!ticker}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                                        disabled:opacity-40 disabled:cursor-not-allowed
                                        ${
                                            timeframe === tf
                                                ? "bg-blue-600 text-white"
                                                : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                                        }`}
                                >
                                    {tf}
                                </button>
                            ))}
                        </div>

                        {/* Dashboard cards */}
                        <div className="flex flex-wrap gap-4 mt-5">
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

                        <CandlestickChart data={stockData} />
                        <VolumeChart data={stockData} />
                        <RSIChart data={stockData} />
                        <MACDChart data={stockData} />
                        <StockData data={stockData} />
                    </>
                )}
            </div>
        </div>
    );
}

export default App;