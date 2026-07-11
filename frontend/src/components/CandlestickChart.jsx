import { useState, useEffect } from "react";
import Chart from "react-apexcharts";

function CandlestickChart({ data }) {

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

    const candlestickSeries = {
        name: "Price",
        type: "candlestick",
        data: data.map((point) => ({
            x: new Date(point.date),
            y: [point.open, point.high, point.low, point.close],
        })),
    };

    const buildLineSeries = (field, name) => ({
        name,
        type: "line",
        data: data
            .filter((point) => point[field] !== null && point[field] !== undefined)
            .map((point) => ({
                x: new Date(point.date),
                y: point[field],
            })),
    });

    const sma20Series = buildLineSeries("sma_20", "SMA 20");
    const sma50Series = buildLineSeries("sma_50", "SMA 50");
    const ema20Series = buildLineSeries("ema_20", "EMA 20");
    const ema50Series = buildLineSeries("ema_50", "EMA 50");
    const bbUpperSeries = buildLineSeries("bb_upper", "BB Upper");
    const bbLowerSeries = buildLineSeries("bb_lower", "BB Lower");

    const series = [
        candlestickSeries,
        sma20Series,
        sma50Series,
        ema20Series,
        ema50Series,
        bbUpperSeries,
        bbLowerSeries,
    ];

    const options = {
        chart: {
            height: 350,
            toolbar: { show: true },
            background: "transparent",
        },
        theme: {
            mode: isDark ? "dark" : "light",
        },
        stroke: {
            // 0: candlestick, 1: SMA20, 2: SMA50, 3: EMA20, 4: EMA50, 5: BB Upper, 6: BB Lower
            width: [1, 2, 2, 2, 2, 1, 1],
            dashArray: [0, 0, 0, 0, 0, 4, 4],
        },
        colors: [
            "#000000", // candlestick (unused directly, controlled by plotOptions)
            "#f59e0b", // SMA 20 - amber
            "#8b5cf6", // SMA 50 - purple
            "#06b6d4", // EMA 20 - cyan
            "#ec4899", // EMA 50 - pink
            "#94a3b8", // BB Upper - gray
            "#94a3b8", // BB Lower - gray
        ],
        plotOptions: {
            candlestick: {
                colors: {
                    upward: "#22c55e",
                    downward: "#ef4444",
                },
            },
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
        legend: {
            show: true,
            labels: {
                colors: isDark ? "#9ca3af" : "#374151",
            },
        },
        tooltip: {
            shared: true,
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