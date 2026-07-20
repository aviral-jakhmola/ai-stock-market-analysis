import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Profile() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    if (!user) return null;

    const joined = new Date(user.created_at).toLocaleDateString("en-IN", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 transition-colors">
            <div className="w-full max-w-sm bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-md p-8">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                    Profile
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                    Your account details
                </p>

                <div className="flex flex-col gap-4">
                    <div>
                        <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                            Username
                        </span>
                        <span className="text-gray-900 dark:text-gray-100 font-medium">
                            {user.username}
                        </span>
                    </div>

                    <div>
                        <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                            Email
                        </span>
                        <span className="text-gray-900 dark:text-gray-100 font-medium">
                            {user.email}
                        </span>
                    </div>

                    <div>
                        <span className="block text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">
                            Member since
                        </span>
                        <span className="text-gray-900 dark:text-gray-100 font-medium">
                            {joined}
                        </span>
                    </div>
                </div>

                <button
                    onClick={handleLogout}
                    className="mt-8 w-full bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg px-4 py-2 text-sm transition-colors shadow-md shadow-red-500/10"
                >
                    Log out
                </button>
            </div>
        </div>
    );
}

export default Profile;