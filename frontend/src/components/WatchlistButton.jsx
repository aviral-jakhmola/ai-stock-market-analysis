import { useState, useEffect } from "react";
import { Star } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getWatchlist, addToWatchlist, removeFromWatchlist } from "../services/api";

function WatchlistButton({ ticker }) {
    const { isAuthenticated } = useAuth();
    const [watchlistItem, setWatchlistItem] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!isAuthenticated || !ticker) {
            setWatchlistItem(null);
            return;
        }

        getWatchlist()
            .then((items) => {
                const match = items.find((item) => item.ticker === ticker.toUpperCase());
                setWatchlistItem(match || null);
            })
            .catch((err) => console.error("Failed to load watchlist", err));
    }, [ticker, isAuthenticated]);

    if (!isAuthenticated || !ticker) {
        return null;
    }

    const isSaved = !!watchlistItem;

    const toggle = async () => {
        setLoading(true);
        try {
            if (isSaved) {
                await removeFromWatchlist(watchlistItem.id);
                setWatchlistItem(null);
            } else {
                const created = await addToWatchlist(ticker);
                setWatchlistItem(created);
            }
        } catch (err) {
            console.error("Watchlist toggle failed", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={toggle}
            disabled={loading}
            title={isSaved ? "Remove from Watchlist" : "Add to Watchlist"}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors disabled:opacity-50"
            aria-label={isSaved ? "Remove from watchlist" : "Add to watchlist"}
        >
            <Star
                size={20}
                className={isSaved ? "fill-yellow-400 text-yellow-400" : "text-gray-400 dark:text-gray-500"}
            />
        </button>
    );
}

export default WatchlistButton;