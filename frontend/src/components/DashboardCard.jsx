function DashboardCard({ title, value }) {
    return (
        <div
            style={{
                border: "1px solid #ddd",
                borderRadius: "10px",
                padding: "15px",
                minWidth: "180px",
                textAlign: "center",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                backgroundColor: "#fff",
            }}
        >
            <h3>{title}</h3>

            <h2>{value}</h2>
        </div>
    );
}

export default DashboardCard;