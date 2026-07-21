import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Star, X } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
    getWatchlist,
    removeFromWatchlist,
    getSearchHistory,
} from "../services/api";

function Profile() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [watchlist, setWatchlist] = useState([]);
    const [loadingWatchlist, setLoadingWatchlist] = useState(true);
    const [searchHistory, setSearchHistory] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(true);

    useEffect(() => {
        getWatchlist()
            .then(setWatchlist)
            .catch((err) => console.error("Failed to load watchlist", err))
            .finally(() => setLoadingWatchlist(false));
        
        getSearchHistory()
    .then(setSearchHistory)
    .catch((err) => console.error("Failed to load search history", err))
    .finally(() => setLoadingHistory(false));
    }, []);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const handleRemove = async (id) => {
        try {
            await removeFromWatchlist(id);
            setWatchlist((prev) => prev.filter((item) => item.id !== id));
        } catch (err) {
            console.error("Failed to remove item", err);
        }
    };

    if (!user) return null;

    const joined = new Date(user.created_at).toLocaleDateString("en-IN", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 px-4 py-10 transition-colors">
            <div className="w-full max-w-2xl mx-auto flex flex-col gap-6">

                {/* Account details card */}
                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-md p-8">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                        Profile
                    </h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                        Your account details
                    </p>

                    <div className="flex flex-col gap-4">
                        <div>
                            <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                                Username
                            </span>
                            <span className="text-gray-900 dark:text-gray-100 font-medium">
                                {user.username}
                            </span>
                        </div>

                        <div>
                            <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                                Email
                            </span>
                            <span className="text-gray-900 dark:text-gray-100 font-medium">
                                {user.email}
                            </span>
                        </div>

                        <div>
                            <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                                Member since
                            </span>
                            <span className="text-gray-900 dark:text-gray-100 font-medium">
                                {joined}
                            </span>
                        </div>
                    </div>

                    <button
                        onClick={handleLogout}
                        className="mt-8 w-full bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg px-4 py-2 text-sm transition-colors shadow-md shadow-red-500/10"
                    >
                        Log out
                    </button>
                </div>

                {/* Watchlist card */}
                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-md p-8">
                    <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                        <Star size={18} className="fill-yellow-400 text-yellow-400" />
                        My Watchlist
                    </h2>

                    {loadingWatchlist ? (
                        <p className="text-sm text-gray-400 dark:text-gray-500">Loading...</p>
                    ) : watchlist.length === 0 ? (
                        <p className="text-sm text-gray-400 dark:text-gray-500">
                            You haven't added any stocks yet. Search a stock and click the star to save it here.
                        </p>
                    ) : (
                        <div className="flex flex-col gap-2">
                            {watchlist.map((item) => (
                                <div
                                    key={item.id}
                                    className="flex items-center justify-between rounded-lg bg-gray-50 dark:bg-gray-900/40 px-4 py-2.5"
                                >
                                    <button
                                        onClick={() => navigate("/", { state: { ticker: item.ticker } })}
                                        className="text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-left"
>
                                            {item.ticker}
                                    </button>
                                    <button
                                        onClick={() => handleRemove(item.id)}
                                        className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                                        aria-label="Remove from watchlist"
                                    >
                                        <X size={16} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>


                <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-md p-8">
    <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
        Recently Searched
    </h2>

    {loadingHistory ? (
        <p className="text-sm text-gray-400 dark:text-gray-500">
            Loading...
        </p>
    ) : searchHistory.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-gray-500">
            No recent searches yet.
        </p>
    ) : (
        <div className="flex flex-col gap-2">
            {searchHistory.map((item) => (
                <button
                    key={item.id}
                    onClick={() =>
                        navigate("/", {
                            state: { ticker: item.ticker },
                        })
                    }
                    className="flex justify-between items-center rounded-lg bg-gray-50 dark:bg-gray-900/40 px-4 py-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
                >
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                        {item.ticker}
                    </span>

                    <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(item.searched_at).toLocaleString("en-IN")}
                    </span>
                </button>
            ))}
        </div>
    )}
</div>


                

            </div>


            
        </div>

        
    );
}

export default Profile;