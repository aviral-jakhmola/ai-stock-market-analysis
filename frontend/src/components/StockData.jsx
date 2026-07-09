function StockData({ data }) {
    if (!data || data.length === 0) {
        return <p>No data available.</p>;
    }

    return (
        <div style={{ marginTop: "20px" }}>
            <h2>Historical Data</h2>

            <pre>
                {JSON.stringify(data.slice(0, 5), null, 2)}
            </pre>
        </div>
    );
}

export default StockData;