import { useState } from "react";
import RecommendationCard from "./RecommendationCard";
import PredictionCard from "./PredictionCard";
import SentimentCard from "./SentimentCard";

function FinalRecommendationCard({ data, recommendation, prediction, sentiment }) {
    const [expanded, setExpanded] = useState({});

    if (!data) {
        return null;
    }

    const { final_recommendation, note, breakdown, weighted_bullish, weighted_bearish, total_weight } = data;

    const styles = {
        BUY: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400",
        SELL: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400",
        HOLD: "bg-gray-100 text-gray-600 dark:bg-gray-700/40 dark:text-gray-300",
    };

    const noteBorder = {
        BUY: "border-green-300 dark:border-green-700",
        SELL: "border-red-300 dark:border-red-700",
        HOLD: "border-gray-200 dark:border-gray-700",
    };

    const voteColor = {
        bullish: "text-green-600 dark:text-green-400",
        bearish: "text-red-600 dark:text-red-400",
        neutral: "text-gray-500 dark:text-gray-400",
    };

    const sources = [
        { key: "technical", label: "Technical (Rule-Based)", panel: <RecommendationCard recommendation={recommendation} /> },
        { key: "ml", label: "ML Prediction", panel: <PredictionCard data={prediction} /> },
        { key: "sentiment", label: "News Sentiment", panel: <SentimentCard data={sentiment} /> },
    ];

    const toggle = (key) => {
        setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
    };

    

    return (
        <div className="mt-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4 shadow-sm">
            <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                    Final Recommendation
                </h2>
                <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wide ${styles[final_recommendation]}`}>
                    {final_recommendation}
                </span>
            </div>

            <div className={`mt-3 flex items-start gap-2 rounded-lg border px-3 py-2 text-xs leading-relaxed bg-gray-50 dark:bg-gray-900/20 text-gray-600 dark:text-gray-400 ${noteBorder[final_recommendation]}`}>
                <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{note}</span>
            </div>

            <div className="mt-3 flex h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700">
                <div className="bg-green-500" style={{ width: `${(weighted_bullish / total_weight) * 100}%` }} />
                <div className="bg-gray-300 dark:bg-gray-600" style={{ width: `${((total_weight - weighted_bullish - weighted_bearish) / total_weight) * 100}%` }} />
                <div className="bg-red-500" style={{ width: `${(weighted_bearish / total_weight) * 100}%` }} />
            </div>

            <div className="mt-4 space-y-2">
                {sources.map(({ key, label, panel }) => {
                    const item = breakdown[key];
                    if (!item) return null;
                    const isOpen = expanded[key];

                    return (
                        <div key={key}>
                            <button
                                onClick={() => toggle(key)}
                                className="w-full flex items-center justify-between text-sm rounded-lg bg-gray-50 dark:bg-gray-900/40 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700/40 transition-colors"
                            >
                                <span className="text-gray-600 dark:text-gray-300">{label}</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-gray-400 dark:text-gray-500">
                                        weight {item.weight}
                                    </span>
                                    <span className={`font-semibold ${voteColor[item.vote]}`}>
                                        {item.detail}
                                    </span>
                                    <svg
                                        className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
                                        fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </div>
                            </button>

                            {isOpen && (
                                <div className="mt-2 mb-1">
                                    {panel}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default FinalRecommendationCard;