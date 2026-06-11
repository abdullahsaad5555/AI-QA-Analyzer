import { useEffect, useState } from "react";
import {
    Navigate,
    Route,
    Routes,
    useNavigate,
    useParams,
} from "react-router-dom";

import { useAuth } from "./context/AuthContext";
import { getChat } from "./api/chats";

import LoginPage from "./pages/LoginPage";
import ChatsPage from "./pages/ChatsPage";
import ChatDetailPage from "./pages/ChatDetailPage";

function RequireAuth({ children }) {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

function LoginRoute() {
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to="/chats" replace />;
    }

    return <LoginPage />;
}

function ChatDetailRoute() {
    const { chatId } = useParams();
    const navigate = useNavigate();

    const [chat, setChat] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadChat() {
            if (!chatId) return;

            setLoading(true);
            setError("");

            try {
                const data = await getChat(chatId);
                setChat(data);
            } catch (err) {
                setError(err?.response?.data?.detail || "Failed to load chat");
            } finally {
                setLoading(false);
            }
        }

        loadChat();
    }, [chatId]);

    if (loading) {
        return (
            <div style={styles.page}>
                <p style={styles.text}>Loading chat...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={styles.page}>
                <p style={styles.error}>{error}</p>
                <button
                    type="button"
                    onClick={() => navigate("/chats")}
                    style={styles.button}
                >
                    Back to Chats
                </button>
            </div>
        );
    }

    return (
        <ChatDetailPage
            chat={chat}
            onBack={() => navigate("/chats")}
        />
    );
}

export default function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginRoute />} />

            <Route
                path="/chats"
                element={
                    <RequireAuth>
                        <ChatsPage />
                    </RequireAuth>
                }
            />

            <Route
                path="/chats/:chatId"
                element={
                    <RequireAuth>
                        <ChatDetailRoute />
                    </RequireAuth>
                }
            />

            <Route path="/" element={<Navigate to="/chats" replace />} />
            <Route path="*" element={<Navigate to="/chats" replace />} />
        </Routes>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        background: "#0f172a",
        color: "#ffffff",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "16px",
        padding: "24px",
    },
    text: {
        margin: 0,
        fontSize: "16px",
        color: "#d1d5db",
    },
    error: {
        margin: 0,
        fontSize: "16px",
        color: "#fee2e2",
    },
    button: {
        padding: "12px 16px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "transparent",
        color: "#ffffff",
        cursor: "pointer",
    },
};
``