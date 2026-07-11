import { useState, useEffect } from "react";
import Chart from "react-apexcharts";

function VolumeChart({ data }) {

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
            <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 h-[250px] rounded-xl flex flex-col items-center justify-center">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Volume Chart
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                    Search a stock to see volume.
                </p>
            </div>
        );
    }

    const series = [
        {
            name: "Volume",
            data: data.map((point) => ({
                x: new Date(point.date),
                y: point.volume,
            })),
        },
    ];

    const options = {
        chart: {
            type: "bar",
            height: 250,
            toolbar: { show: false },
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
            labels: {
                formatter: (val) => val.toLocaleString(),
                style: { colors: isDark ? "#9ca3af" : "#374151" },
            },
        },
        plotOptions: {
            bar: {
                columnWidth: "80%",
            },
        },
        dataLabels: { enabled: false },
    };

    return (
        <div className="border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mt-5 p-5 rounded-xl">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Volume Chart
            </h2>

            <Chart
                options={options}
                series={series}
                type="bar"
                height={250}
            />
        </div>
    );
}

export default VolumeChart;