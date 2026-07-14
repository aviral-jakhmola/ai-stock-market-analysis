import React from 'react';

function SentimentCard({ data }) {
    // Safety check to handle loading states or missing records safely
    if (!data || !data.articles || data.articles.length === 0) {
        return null;
    }

    const { summary, overall_sentiment, articles } = data;
    const total = summary.positive + summary.negative + summary.neutral;
    
    // Inline helper to calculate distribution percentages safely
    const getPercentage = (count) => (total > 0 ? (count / total) * 100 : 0);

    // CSS style configurations for individual news rows based on FinBERT output
    const rowTagStyles = {
        positive: "text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20",
        negative: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20",
        neutral: "text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700/40",
    };

    // Color coordination matrix for the main summary dashboard card metrics
    const overallCardStyles = {
        positive: { badge: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400", dot: "bg-green-500" },
        negative: { badge: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400", dot: "bg-red-500" },
        neutral: { badge: "bg-gray-100 text-gray-600 dark:bg-gray-700/40 dark:text-gray-300", dot: "bg-gray-400" },
    };

    return (
        <div className="mt-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4 shadow-sm transition-all">
            
            {/* 1. Header Area with Unified Status Indicators */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${overallCardStyles[overall_sentiment]?.dot || 'bg-gray-400'}`} />
                    <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                        News Sentiment
                    </h2>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${overallCardStyles[overall_sentiment]?.badge || 'bg-gray-100'}`}>
                    {overall_sentiment}
                </span>
            </div>
            
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Based on {total} recent news headline{total !== 1 ? "s" : ""} [cite: 91]
            </p>

            {/* 2. Visual Proportional Segmented Tracking Bar */}
            <div className="mt-4 flex h-2.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700">
                <div className="bg-green-500 transition-all duration-500" style={{ width: `${getPercentage(summary.positive)}%` }} />
                <div className="bg-gray-400 dark:bg-gray-500 transition-all duration-500" style={{ width: `${getPercentage(summary.neutral)}%` }} />
                <div className="bg-red-500 transition-all duration-500" style={{ width: `${getPercentage(summary.negative)}%` }} />
            </div>

            {/* 3. The Quantitative Distribution Legend */}
            <div className="mt-3 flex gap-5 text-xs font-medium text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-green-500" /> Positive ({summary.positive})
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-gray-400" /> Neutral ({summary.neutral})
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-red-500" /> Negative ({summary.negative})
                </span>
            </div>

            <hr className="my-4 border-gray-100 dark:border-gray-700/60" />

            {/* 4. Optimized Interactive Article Feed Collection */}
            <div className="space-y-2 max-h-72 overflow-y-auto pr-1 scrollbar-thin">
                {articles.map((article, i) => (
                    <a
                        key={i}
                        href={article.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start justify-between gap-4 rounded-xl border border-transparent px-3 py-2.5 hover:border-gray-150 dark:hover:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-all duration-150 group"
                    >
                        <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
                                {article.title}
                            </p>
                            <div className="mt-1 flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
                                <span className="font-semibold">{article.publisher}</span>
                                {article.published && (
                                    <>
                                        <span>•</span>
                                        <span>{new Date(article.published).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}</span>
                                    </>
                                )}
                            </div>
                        </div>
                        <span className={`shrink-0 px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wide border dark:border-none shadow-sm self-center ${rowTagStyles[article.sentiment.label]}`}>
                            {article.sentiment.label}
                        </span>
                    </a>
                ))}
            </div>
        </div>
    );
}

export default SentimentCard;