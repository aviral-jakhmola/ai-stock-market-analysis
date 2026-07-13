import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

export default api;

export async function fetchCompanyOverview(ticker) {
    const response = await api.get(`/api/stocks/company/${ticker}`);
    return response.data;
}