import { useState, useEffect } from "react";
import Chart from "react-apexcharts";

function RSIChart({ data }) {

    const [isDark, setIsDark] = useState(
        document.documentElement.classList.contains("dark")
    );

    useEffect(() => {
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
            <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 h-[220px] rounded-xl flex flex-col items-center justify-center">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    RSI (14)
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    Search a stock to see RSI.
                </p>
            </div>
        );
    }

    const series = [
        {
            name: "RSI (14)",
            data: data
                .filter((point) => point.rsi_14 !== null && point.rsi_14 !== undefined)
                .map((point) => ({
                    x: new Date(point.date),
                    y: point.rsi_14,
                })),
        },
    ];

    const options = {
        chart: {
            type: "line",
            height: 220,
            toolbar: { show: false },
            background: "transparent",
        },
        theme: {
            mode: isDark ? "dark" : "light",
        },
        stroke: {
            width: 2,
            curve: "smooth",
        },
        colors: ["#3b82f6"],
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
            min: 0,
            max: 100,
            tickAmount: 4,
            labels: {
                style: { colors: isDark ? "#9ca3af" : "#374151" },
            },
        },
        // Horizontal reference lines at the standard overbought/oversold thresholds
        annotations: {
            yaxis: [
                {
                    y: 70,
                    borderColor: "#ef4444",
                    label: {
                        text: "Overbought (70)",
                        style: { color: "#fff", background: "#ef4444" },
                    },
                },
                {
                    y: 30,
                    borderColor: "#22c55e",
                    label: {
                        text: "Oversold (30)",
                        style: { color: "#fff", background: "#22c55e" },
                    },
                },
            ],
        },
        tooltip: {
            y: {
                formatter: (val) => val.toFixed(2),
            },
        },
    };

    return (
        <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                RSI (14)
            </h2>

            <Chart
                options={options}
                series={series}
                type="line"
                height={220}
            />
        </div>
    );
}

export default RSIChart;