import { useState } from "react";

function SearchBar({ onSearch }) {
    const [ticker, setTicker] = useState("");

    const handleSubmit = () => {
        if (!ticker.trim()) return;
        onSearch(ticker);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") handleSubmit();
    };

    return (
        <div className="mt-5 flex gap-3">
            <input
                type="text"
                placeholder="Enter Stock Symbol"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-1 max-w-xs px-4 py-2 rounded-lg border border-gray-300
                           text-gray-900 placeholder-gray-400
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:placeholder-gray-500"
            />

            <button
                onClick={handleSubmit}
                className="px-5 py-2 rounded-lg bg-blue-600 text-white font-medium
                           hover:bg-blue-700 active:bg-blue-800
                           dark:bg-blue-500 dark:hover:bg-blue-600"
            >
                Search
            </button>
        </div>
    );
}

export default SearchBar;