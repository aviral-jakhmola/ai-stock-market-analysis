import { useState } from "react";

import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import StockData from "./components/StockData";

import api from "./services/api";

function App() {

    const [stockData, setStockData] = useState([]);

    const searchStock = async (ticker) => {

        try {

            const response = await api.get(
                `/api/stocks/${ticker}/history?timeframe=1Y`
            );

            setStockData(response.data);

        } catch (error) {

            console.error(error);

            alert("Unable to fetch stock data.");

        }

    };

    return (
        <>
            <Navbar />

            <div style={{ padding: "20px" }}>

                <SearchBar onSearch={searchStock} />

                <StockData data={stockData} />

            </div>
        </>
    );
}

export default App;