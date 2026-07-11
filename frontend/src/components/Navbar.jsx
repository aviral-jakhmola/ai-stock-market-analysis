import { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";

function Navbar() {
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem("theme") === "dark";
    });

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    }, [darkMode]);

    return (
        <nav className="bg-blue-600 dark:bg-gray-900 text-white px-6 py-4 flex items-center justify-between shadow-md">
            <span className="text-xl font-bold">
                AI Stock Market Analysis
            </span>

            <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg hover:bg-blue-700 dark:hover:bg-gray-800 transition-colors"
                aria-label="Toggle dark mode"
            >
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
        </nav>
    );
}

export default Navbar;