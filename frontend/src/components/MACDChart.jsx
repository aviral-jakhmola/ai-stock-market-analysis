import { useState, useEffect } from "react";
import Chart from "react-apexcharts";

function MACDChart({ data }) {

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
                    MACD
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    Search a stock to see MACD.
                </p>
            </div>
        );
    }

    const macdLine = {
        name: "MACD",
        type: "line",
        data: data
            .filter((p) => p.macd !== null && p.macd !== undefined)
            .map((p) => ({ x: new Date(p.date), y: p.macd })),
    };

    const signalLine = {
        name: "Signal",
        type: "line",
        data: data
            .filter((p) => p.macd_signal !== null && p.macd_signal !== undefined)
            .map((p) => ({ x: new Date(p.date), y: p.macd_signal })),
    };

    const histogram = {
        name: "Histogram",
        type: "bar",
        data: data
            .filter((p) => p.macd_histogram !== null && p.macd_histogram !== undefined)
            .map((p) => ({ x: new Date(p.date), y: p.macd_histogram })),
    };

    const series = [histogram, macdLine, signalLine];

    const options = {
        chart: {
            height: 220,
            toolbar: { show: false },
            background: "transparent",
            stacked: false,
        },
        theme: {
            mode: isDark ? "dark" : "light",
        },
        stroke: {
            width: [0, 2, 2],
            curve: "smooth",
        },
        colors: ["#94a3b8", "#3b82f6", "#f59e0b"],
        plotOptions: {
            bar: {
                columnWidth: "70%",
            },
        },
        // Color histogram bars green/red based on positive/negative value
        fill: {
            opacity: [1, 1, 1],
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
            y: {
                formatter: (val) => val?.toFixed(2),
            },
        },
    };

    return (
        <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                MACD
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

export default MACDChart;