import Chart from "react-apexcharts";

function VolumeChart({ data }) {

    if (!data || data.length === 0) {
        return (
            <div
                style={{
                    border: "1px solid #ddd",
                    marginTop: "20px",
                    padding: "20px",
                    height: "250px",
                    borderRadius: "10px",
                }}
            >
                <h2>Volume Chart</h2>
                <p>Search a stock to see volume.</p>
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
        },
        xaxis: {
            type: "datetime",
        },
        yaxis: {
            labels: {
                formatter: (val) => val.toLocaleString(),
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
        <div
            style={{
                border: "1px solid #ddd",
                marginTop: "20px",
                padding: "20px",
                borderRadius: "10px",
            }}
        >
            <h2>Volume Chart</h2>

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