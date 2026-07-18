function PredictionCard({ data }) {
    if (!data) {
        return null;
    }

    const { direction, probability_up, probability_down, model_accuracy_on_test_set } = data;
    const isUp = direction === "UP";
    const confidencePct = Math.max(probability_up, probability_down) * 100;

    return (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4 shadow-sm hover:shadow-md transition-shadow">

            <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                    ML Direction Prediction
                </h2>
                <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                        isUp
                            ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400"
                            : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400"
                    }`}
                >
                    {direction}
                </span>
            </div>

            <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-100">
                {confidencePct.toFixed(1)}%
                <span className="ml-2 text-sm font-normal text-gray-400 dark:text-gray-500">
                    probability forecast
                </span>
            </p>

            <div className="mt-3 flex h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700">
                <div className="bg-green-500 transition-all duration-500" style={{ width: `${probability_up * 100}%` }} />
                <div className="bg-red-500 transition-all duration-500" style={{ width: `${probability_down * 100}%` }} />
            </div>

            <div className="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span className={isUp ? "font-semibold text-green-600 dark:text-green-400" : ""}>
                    UP {(probability_up * 100).toFixed(1)}%
                </span>
                <span className={!isUp ? "font-semibold text-red-600 dark:text-red-400" : ""}>
                    DOWN {(probability_down * 100).toFixed(1)}%
                </span>
            </div>

            <div className="mt-4 rounded-lg bg-gray-50 dark:bg-gray-900/40 border border-gray-100 dark:border-gray-700 px-3 py-2 text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                <span className="font-semibold text-gray-600 dark:text-gray-300">⚠️ Model accuracy:</span>{" "}
                {(model_accuracy_on_test_set * 100).toFixed(1)}% on historical test data — close to chance level. Treat as experimental, not a reliable signal.
            </div>
        </div>
    );
}

export default PredictionCard;