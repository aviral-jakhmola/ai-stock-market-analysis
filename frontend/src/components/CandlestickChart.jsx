import Chart from "react-apexcharts";

function CandlestickChart({ data }) {

    if (!data || data.length === 0) {
        return (
            <div
                style={{
                    border: "1px solid #ddd",
                    marginTop: "20px",
                    padding: "20px",
                    height: "350px",
                    borderRadius: "10px",
                }}
            >
                <h2>Candlestick Chart</h2>
                <p>Search a stock to see the chart.</p>
            </div>
        );
    }

    // ApexCharts candlestick format: { x: date, y: [open, high, low, close] }
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
        },
        xaxis: {
            type: "datetime",
        },
        yaxis: {
            tooltip: { enabled: true },
        },
    };

    return (
        <div
            style={{
                border: "1px solid #ddd",
                marginTop: "20px",
                padding: "20px",
                borderRadius: "10px",
            }}
        >
            <h2>Candlestick Chart</h2>

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