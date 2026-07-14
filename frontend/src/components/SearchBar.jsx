import { useState, useEffect, useRef } from "react";
import api from "../services/api";

function SearchBar({ onSearch }) {
    const [ticker, setTicker] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const wrapperRef = useRef(null);

    // Fetch suggestions as the user types, debounced
    useEffect(() => {
        if (!ticker.trim()) {
            setSuggestions([]);
            return;
        }

        const timeoutId = setTimeout(async () => {
            try {
                const res = await api.get(`/api/stocks/search?q=${ticker}`);
                setSuggestions(res.data.results);
                setShowDropdown(true);
            } catch (error) {
                console.error(error);
            }
        }, 300); // wait 300ms after typing stops before firing the request

        return () => clearTimeout(timeoutId);
    }, [ticker]);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSubmit = () => {
        if (!ticker.trim()) return;
        onSearch(ticker);
        setShowDropdown(false);
    };

    const handleSelect = (symbol) => {
        setTicker(symbol);
        onSearch(symbol);
        setShowDropdown(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") handleSubmit();
        if (e.key === "Escape") setShowDropdown(false);
    };

    return (
        <div className="mt-5 flex gap-3 relative" ref={wrapperRef}>
            <div className="relative flex-1 max-w-xs">
                <input
                    type="text"
                    placeholder="Enter Stock Symbol"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300
                               text-gray-900 placeholder-gray-400
                               focus:outline-none focus:ring-2 focus:ring-blue-500
                               dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:placeholder-gray-500"
                />

                {showDropdown && suggestions.length > 0 && (
                    <ul className="absolute z-10 mt-1 w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg overflow-hidden">
                        {suggestions.map((symbol) => (
                            <li key={symbol}>
                                <button
                                    onClick={() => handleSelect(symbol)}
                                    className="w-full text-left px-4 py-2 text-sm text-gray-900 dark:text-gray-100
                                               hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
                                >
                                    {symbol}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

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