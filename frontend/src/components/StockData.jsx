function StockData({ data }) {
    if (!data || data.length === 0) {
        return <p>No data available.</p>;
    }

    return (
        <div style={{ marginTop: "20px" }}>
            <h2>Historical Data</h2>

            <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                    <tr>
                        <th style={thStyle}>Date</th>
                        <th style={thStyle}>Open</th>
                        <th style={thStyle}>High</th>
                        <th style={thStyle}>Low</th>
                        <th style={thStyle}>Close</th>
                        <th style={thStyle}>Volume</th>
                    </tr>
                </thead>
                <tbody>
                    {data.slice(0, 5).map((row, index) => (
                        <tr key={index}>
                            <td style={tdStyle}>
                                {new Date(row.date).toLocaleDateString()}
                            </td>
                            <td style={tdStyle}>{row.open?.toFixed(2) ?? "—"}</td>
                            <td style={tdStyle}>{row.high?.toFixed(2) ?? "—"}</td>
                            <td style={tdStyle}>{row.low?.toFixed(2) ?? "—"}</td>
                            <td style={tdStyle}>{row.close?.toFixed(2) ?? "—"}</td>
                            <td style={tdStyle}>{row.volume?.toLocaleString() ?? "—"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

const thStyle = {
    textAlign: "left",
    borderBottom: "2px solid #ddd",
    padding: "8px",
};

const tdStyle = {
    borderBottom: "1px solid #eee",
    padding: "8px",
};

export default StockData;