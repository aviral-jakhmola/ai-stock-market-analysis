import { useState } from "react";

import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";

import DashboardCard from "./components/DashboardCard";
import CandlestickChart from "./components/CandlestickChart";
import VolumeChart from "./components/VolumeChart";
import LoadingSpinner from "./components/LoadingSpinner";

import StockData from "./components/StockData";

import api from "./services/api";

function App() {

    const [stockData, setStockData] = useState([]);
    const [loading, setLoading] = useState(false);

    const searchStock = async (ticker) => {

        setLoading(true);

        try {

            const response = await api.get(
                `/api/stocks/${ticker}/history?timeframe=1Y`
            );

            setStockData(response.data);

        } catch (error) {

            console.error(error);

            alert("Unable to fetch stock data.");

        } finally {

            setLoading(false);

        }

    };

    // Grab the most recent record for the summary cards
    const latest = stockData.length > 0
        ? stockData[stockData.length - 1]
        : null;

    return (
        <>
            <Navbar />

            <div style={{ padding: "20px" }}>

                <SearchBar onSearch={searchStock} />

                {loading ? (
                    <LoadingSpinner />
                ) : (
                    <>
                        <div
                            style={{
                                display: "flex",
                                gap: "20px",
                                flexWrap: "wrap",
                                marginTop: "20px",
                            }}
                        >
                            <DashboardCard
    title="Current Price"
    value={latest ? latest.close.toFixed(2) : "--"}
/>
<DashboardCard
    title="High"
    value={latest ? latest.high.toFixed(2) : "--"}
/>
<DashboardCard
    title="Low"
    value={latest ? latest.low.toFixed(2) : "--"}
/>
<DashboardCard
    title="Volume"
    value={latest ? latest.volume.toLocaleString() : "--"}
/>
                        </div>

                        <CandlestickChart data={stockData} />

                        <VolumeChart data={stockData} />

                        <StockData data={stockData} />
                    </>
                )}

            </div>
        </>
    );
}

export default App;