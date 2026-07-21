import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

// Attach the JWT to every outgoing request automatically, if one exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// If the backend ever returns 401 (expired/invalid token), log the user out
// automatically instead of leaving the app in a broken half-authenticated state
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default api;

export async function fetchCompanyOverview(ticker) {
    const response = await api.get(`/api/stocks/company/${ticker}`);
    return response.data;
}

export async function fetchSentiment(ticker) {
    const response = await api.get(`/api/stocks/${ticker}/sentiment`);
    return response.data;
}

export async function getWatchlist() {
    const response = await api.get("/api/watchlist");
    return response.data;
}

export async function addToWatchlist(ticker) {
    const response = await api.post("/api/watchlist", { ticker });
    return response.data;
}

export async function removeFromWatchlist(itemId) {
    const response = await api.delete(`/api/watchlist/${itemId}`);
    return response.data;
}