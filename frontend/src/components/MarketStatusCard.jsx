function getMarketStatus(ticker) {
    const isIndianStock = ticker?.toUpperCase().endsWith(".NS");
    const timeZone = isIndianStock ? "Asia/Kolkata" : "America/New_York";
    const exchangeLabel = isIndianStock ? "NSE" : "NASDAQ / NYSE";

    const now = new Date();
    const parts = new Intl.DateTimeFormat("en-US", {
        timeZone,
        weekday: "short",
        hour: "numeric",
        minute: "numeric",
        hour12: false,
    }).formatToParts(now);

    const weekday = parts.find((p) => p.type === "weekday").value;
    const hour = parseInt(parts.find((p) => p.type === "hour").value, 10);
    const minute = parseInt(parts.find((p) => p.type === "minute").value, 10);
    const minutesNow = hour * 60 + minute;

    const isWeekday = !["Sat", "Sun"].includes(weekday);

    const openMinutes = isIndianStock ? 9 * 60 + 15 : 9 * 60 + 30;
    const closeMinutes = isIndianStock ? 15 * 60 + 30 : 16 * 60;

    const isOpen = isWeekday && minutesNow >= openMinutes && minutesNow < closeMinutes;

    const timeLabel = new Intl.DateTimeFormat("en-US", {
        timeZone,
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
    }).format(now);

    return { isOpen, exchangeLabel, timeLabel };
}

function MarketStatusCard({ ticker }) {
    if (!ticker) {
        return null;
    }

    const { isOpen, exchangeLabel, timeLabel } = getMarketStatus(ticker);

    return (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3 shadow-sm">
            <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${isOpen ? "bg-green-500" : "bg-gray-400"}`} />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {exchangeLabel} {isOpen ? "Open" : "Closed"}
                </span>
            </div>
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                {timeLabel} local exchange time
            </p>
        </div>
    );
}

export default MarketStatusCard;