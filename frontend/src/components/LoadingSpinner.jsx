function LoadingSpinner() {
    return (
        <div className="flex flex-col items-center justify-center gap-3 mt-10">
            <div className="w-10 h-10 border-4 border-gray-200 dark:border-gray-700 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin" />
            <p className="text-gray-500 dark:text-gray-400 text-sm">
                Loading stock data...
            </p>
        </div>
    );
}

export default LoadingSpinner;