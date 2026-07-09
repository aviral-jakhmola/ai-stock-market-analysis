function SearchBar() {
  return (
    <div style={{ marginTop: "20px" }}>
      <input
        type="text"
        placeholder="Enter Stock Symbol"
      />

      <button>
        Search
      </button>
    </div>
  );
}

export default SearchBar;