import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

function MarketStatus() {
    const now = new Date();
    const istHour = now.getUTCHours() + 5.5; // rough IST offset, good enough for display
    const day = now.getUTCDay();
    const isWeekday = day >= 1 && day <= 5;
    const hourIST = (now.getUTCHours() + 5) % 24 + now.getUTCMinutes() / 60 + 0.5;
    const isMarketHours = hourIST >= 9.25 && hourIST < 15.5;
    const isOpen = isWeekday && isMarketHours;

    return (
        <div className="flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${isOpen ? "bg-green-500" : "bg-gray-400"}`} />
            <span className="text-gray-600 dark:text-gray-400">
                NSE {isOpen ? "Open" : "Closed"}
            </span>
        </div>
    );
}

function IndicatorRow({ vote }) {
    const [expanded, setExpanded] = useState(false);

    const dotColor = {
        bullish: "bg-green-500",
        bearish: "bg-red-500",
        neutral: "bg-gray-400",
    }[vote.direction];

    return (
        <div className="border border-gray-100 dark:border-gray-700 rounded-lg px-3 py-2">
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between text-left"
            >
                <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${dotColor}`} />
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {vote.indicator}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                        {vote.value}
                    </span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                    {vote.text}
                    {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </div>
            </button>
            {expanded && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 pl-4">
                    {vote.why}
                </p>
            )}
        </div>
    );
}

function RecommendationCard({ recommendation }) {

    if (!recommendation) {
        return (
            <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    AI Recommendation
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    Search a stock to see a recommendation.
                </p>
            </div>
        );
    }

    const { recommendation: rec, votes, signal_strength, historical_accuracy, lookahead_days } = recommendation;

    const theme = {
        BUY: { border: "border-l-green-500", badge: "bg-green-500 text-white", bar: "bg-green-500" },
        SELL: { border: "border-l-red-500", badge: "bg-red-500 text-white", bar: "bg-red-500" },
        HOLD: { border: "border-l-gray-400", badge: "bg-gray-400 text-white", bar: "bg-gray-400" },
    }[rec];

    const bullishVotes = votes.filter((v) => v.direction === "bullish");
    const bearishVotes = votes.filter((v) => v.direction === "bearish");
    const neutralVotes = votes.filter((v) => v.direction === "neutral");

    return (
        <div className={`border border-gray-200 dark:border-gray-700 border-l-4 ${theme.border} bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl`}>
            <div className="flex items-center justify-between mb-1">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    AI Recommendation
                </h2>
                <span className={`px-4 py-1.5 rounded-full font-bold text-lg tracking-wide ${theme.badge}`}>
                    {rec}
                </span>
            </div>
            <div className="mb-4">
                <MarketStatus />
            </div>

            {/* Trend strength bar */}
            <div className="mb-5">
                <div className="flex items-center justify-between mb-1.5">
                    <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                        Trend Strength
                    </h3>
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        {signal_strength.agreement_pct !== null ? `${signal_strength.agreement_pct}%` : "—"}
                    </span>
                </div>
                <div className="w-full h-2 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
                    <div
                        className={`h-full rounded-full ${theme.bar} transition-all`}
                        style={{ width: `${signal_strength.agreement_pct ?? 0}%` }}
                    />
                </div>
            </div>

            {/* Bullish signals */}
            {bullishVotes.length > 0 && (
                <div className="mb-4">
                    <h3 className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide mb-2">
                        Bullish Signals
                    </h3>
                    <div className="space-y-1.5">
                        {bullishVotes.map((v, i) => <IndicatorRow key={i} vote={v} />)}
                    </div>
                </div>
            )}

            {/* Bearish signals */}
            {bearishVotes.length > 0 && (
                <div className="mb-4">
                    <h3 className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wide mb-2">
                        Bearish Signals
                    </h3>
                    <div className="space-y-1.5">
                        {bearishVotes.map((v, i) => <IndicatorRow key={i} vote={v} />)}
                    </div>
                </div>
            )}

            {/* Neutral signals */}
            {neutralVotes.length > 0 && (
                <div className="mb-5">
                    <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                        Neutral Signals
                    </h3>
                    <div className="space-y-1.5">
                        {neutralVotes.map((v, i) => <IndicatorRow key={i} vote={v} />)}
                    </div>
                </div>
            )}

            {/* Historical accuracy */}
            <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
                <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1.5">
                    Historical Accuracy
                </h3>
                {historical_accuracy ? (
                    <>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-gray-900 dark:text-white">
                                {historical_accuracy.success_rate_pct}%
                            </span>
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                                correct over {historical_accuracy.sample_size} past signals ({lookahead_days}d lookahead)
                            </span>
                        </div>
                        {!historical_accuracy.reliable && (
                            <p className="text-xs text-amber-600 dark:text-amber-400 mt-1.5">
                                ⚠ Small sample size — treat this percentage with caution.
                            </p>
                        )}
                    </>
                ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        Not available for HOLD signals.
                    </p>
                )}
            </div>
        </div>
    );
}

export default RecommendationCard;