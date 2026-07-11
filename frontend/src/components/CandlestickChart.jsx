import { useState, useEffect } from "react";
import Chart from "react-apexcharts";

function CandlestickChart({ data }) {

    const [isDark, setIsDark] = useState(
        document.documentElement.classList.contains("dark")
    );

    useEffect(() => {
        // Watch for the "dark" class being added/removed on <html>
        const observer = new MutationObserver(() => {
            setIsDark(document.documentElement.classList.contains("dark"));
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ["class"],
        });

        return () => observer.disconnect();
    }, []);

    if (!data || data.length === 0) {
        return (
            <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 h-[350px] rounded-xl flex flex-col items-center justify-center">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Candlestick Chart
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    Search a stock to see the chart.
                </p>
            </div>
        );
    }

    const series = [
        {
            data: data.map((point) => ({
                x: new Date(point.date),
                y: [point.open, point.high, point.low, point.close],
            })),
        },
    ];

    const options = {
        chart: {
            type: "candlestick",
            height: 350,
            toolbar: { show: true },
            background: "transparent",
        },
        theme: {
            mode: isDark ? "dark" : "light",
        },
        grid: {
            borderColor: isDark ? "#374151" : "#e5e7eb",
        },
        xaxis: {
            type: "datetime",
            labels: {
                style: { colors: isDark ? "#9ca3af" : "#374151" },
            },
        },
        yaxis: {
            tooltip: { enabled: true },
            labels: {
                style: { colors: isDark ? "#9ca3af" : "#374151" },
            },
        },
    };

    return (
        <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Candlestick Chart
            </h2>

            <Chart
                options={options}
                series={series}
                type="candlestick"
                height={350}
            />
        </div>
    );
}

export default CandlestickChart;