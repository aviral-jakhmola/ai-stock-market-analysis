import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sun, Moon } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Navbar() {
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem("theme") === "dark";
    });

    const { isAuthenticated, user, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    }, [darkMode]);

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="bg-blue-600 dark:bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
            <Link to="/" className="text-xl font-bold">
                AI Stock Market Analysis
            </Link>

            <div className="flex items-center gap-4">
                {isAuthenticated ? (
                    <>
                        <Link
                            to="/profile"
                            className="text-sm font-medium hover:underline"
                        >
                            {user?.username}
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="text-sm font-semibold bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors"
                        >
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link
                            to="/login"
                            className="text-sm font-medium hover:underline"
                        >
                            Login
                        </Link>
                        <Link
                            to="/register"
                            className="text-sm font-semibold bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors"
                        >
                            Register
                        </Link>
                    </>
                )}

                <button
                    onClick={() => setDarkMode(!darkMode)}
                    className="p-2 rounded-lg hover:bg-blue-700 dark:hover:bg-gray-800 transition-colors"
                    aria-label="Toggle dark mode"
                >
                    {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
            </div>
        </nav>
    );
}

export default Navbar;