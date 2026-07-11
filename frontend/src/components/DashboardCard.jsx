function DashboardCard({ title, value, trend = "neutral" }) {

    const trendStyles = {
        up: "text-green-600 dark:text-green-400",
        down: "text-red-600 dark:text-red-400",
        neutral: "text-gray-900 dark:text-white",
    };

    return (
        <div className="border border-gray-200 dark:border-gray-700
                         bg-white dark:bg-gray-800
                         rounded-xl p-5 min-w-[160px] flex-1
                         shadow-sm hover:shadow-md transition-shadow
                         text-center">

            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                {title}
            </h3>

            <p className={`text-2xl font-semibold mt-1 ${trendStyles[trend]}`}>
                {value}
            </p>

        </div>
    );
}

export default DashboardCard;