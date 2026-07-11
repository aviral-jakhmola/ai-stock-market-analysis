function StockData({ data }) {
    if (!data || data.length === 0) {
        return (
            <p className="text-gray-500 dark:text-gray-400 mt-5">
                No data available.
            </p>
        );
    }

    return (
        <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Historical Data
            </h2>

            <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                    <thead>
                        <tr>
                            <th className={thStyle}>Date</th>
                            <th className={thStyle}>Open</th>
                            <th className={thStyle}>High</th>
                            <th className={thStyle}>Low</th>
                            <th className={thStyle}>Close</th>
                            <th className={thStyle}>Volume</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.slice(0, 5).map((row, index) => (
                            <tr
                                key={index}
                                className="hover:bg-gray-50 dark:hover:bg-gray-700/50"
                            >
                                <td className={tdStyle}>
                                    {new Date(row.date).toLocaleDateString()}
                                </td>
                                <td className={tdStyle}>{row.open?.toFixed(2) ?? "—"}</td>
                                <td className={tdStyle}>{row.high?.toFixed(2) ?? "—"}</td>
                                <td className={tdStyle}>{row.low?.toFixed(2) ?? "—"}</td>
                                <td className={tdStyle}>{row.close?.toFixed(2) ?? "—"}</td>
                                <td className={tdStyle}>{row.volume?.toLocaleString() ?? "—"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

const thStyle =
    "text-left border-b-2 border-gray-200 dark:border-gray-600 py-2 px-3 text-gray-500 dark:text-gray-400 font-medium uppercase text-xs tracking-wide whitespace-nowrap";

const tdStyle =
    "border-b border-gray-100 dark:border-gray-700 py-2 px-3 text-gray-900 dark:text-white whitespace-nowrap";

export default StockData;