import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // On first load, check if a token already exists (e.g. page refresh)
    // and try to restore the logged-in user from it.
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            setLoading(false);
            return;
        }

        api
            .get("/api/auth/me")
            .then((response) => {
                setUser(response.data);
            })
            .catch(() => {
                // Token invalid/expired — interceptor already clears it and redirects,
                // but clear local state too just in case.
                setUser(null);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    async function login(username, password) {
        // Login endpoint expects form-encoded data, not JSON (OAuth2PasswordRequestForm)
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await api.post("/api/auth/login", formData, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        const { access_token } = response.data;
        localStorage.setItem("token", access_token);

        // Fetch the actual user info now that we have a valid token
        const me = await api.get("/api/auth/me");
        setUser(me.data);

        return me.data;
    }

    async function register(username, email, password) {
        await api.post("/api/auth/register", {
            username,
            email,
            password,
        });

        // Auto-login immediately after successful registration
        const user = await login(username, password);
        return user;
    }

    function logout() {
        localStorage.removeItem("token");
        setUser(null);
    }

    const value = {
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}