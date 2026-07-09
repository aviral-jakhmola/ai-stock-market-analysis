import { useState } from "react";

function SearchBar({ onSearch }) {
    const [ticker, setTicker] = useState("");

    const handleSubmit = () => {
        if (!ticker.trim()) return;
        onSearch(ticker);
    };

    return (
        <div style={{ marginTop: "20px" }}>
            <input
                type="text"
                placeholder="Enter Stock Symbol"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
            />

            <button onClick={handleSubmit}>
                Search
            </button>
        </div>
    );
}

export default SearchBar;