import Navbar from "./components/Navbar";
import SearchBar from "./components/SearchBar";
import StockData from "./components/StockData";

function App() {
  return (
    <>
      <Navbar />

      <div
        style={{
          padding: "20px",
        }}
      >
        <SearchBar />

        <StockData />
      </div>
    </>
  );
}

export default App;