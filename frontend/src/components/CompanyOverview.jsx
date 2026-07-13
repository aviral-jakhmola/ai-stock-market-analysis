function CompanyOverview({ data }) {
    if (!data) return null;

    const formatMarketCap = (value) => {
        if (value == null) return "—";
        if (value >= 1e12) return `${(value / 1e12).toFixed(2)}T`;
        if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
        if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
        return value.toLocaleString();
    };

    const stats = [
        {
            label: "Market Cap",
            value: formatMarketCap(data.market_cap),
        },
        {
            label: "P/E",
            value: data.pe_ratio?.toFixed(2) ?? "—",
        },
        {
            label: "Beta",
            value: data.beta?.toFixed(2) ?? "—",
        },
        {
            label: "Dividend",
            value:
                data.dividend_yield != null
                    ? `${data.dividend_yield}%`
                    : "—",
        },
        {
            label: "52W High",
            value:
                data.fifty_two_week_high?.toFixed(2) ?? "—",
        },
        {
            label: "52W Low",
            value:
                data.fifty_two_week_low?.toFixed(2) ?? "—",
        },
    ];

    return (
        <div className="mt-6 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm p-5">

            {/* Header */}
            <div className="mb-5">
                <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
                    {data.name}
                </h2>

                {(data.sector || data.industry) && (
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        {data.sector}
                        {data.sector && data.industry && " • "}
                        {data.industry}
                    </p>
                )}
            </div>

            {/* Stats */}
            <div
                className="grid gap-4"
                style={{
                    gridTemplateColumns:
                        "repeat(auto-fit, minmax(160px, 1fr))",
                }}
            >
                {stats.map((stat) => (
                    <div
                        key={stat.label}
                        className="
                            rounded-xl
                            border
                            border-gray-200
                            dark:border-gray-700
                            bg-gray-50/80
                            dark:bg-gray-900
                            px-4
                            py-3
                            transition-all
                            duration-200
                            hover:shadow-md
                            hover:border-blue-400
                            dark:hover:border-blue-500
                        "
                    >
                        <p className="text-[11px] font-semibold uppercase tracking-widest text-gray-500 dark:text-gray-400">
                            {stat.label}
                        </p>

                        <p className="mt-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
    {stat.value}
</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default CompanyOverview;