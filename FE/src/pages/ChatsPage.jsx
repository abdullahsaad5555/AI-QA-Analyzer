import { useEffect, useState } from "react";
import { createChat, deleteChat, listChats } from "../api/chats";
import ChatDetailPage from "./ChatDetailPage";
import AppShell from "../component/layout/AppShell";

export default function ChatsPage() {
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);

    const [newChatName, setNewChatName] = useState("");
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [error, setError] = useState("");

    async function loadChats() {
        setLoading(true);
        setError("");

        try {
            const data = await listChats();
            setChats(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to load chats");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadChats();
    }, []);

    async function handleCreateChat(e) {
        e.preventDefault();

        if (!newChatName.trim()) return;

        setCreating(true);
        setError("");

        try {
            const created = await createChat({
                name: newChatName.trim(),
            });

            setChats((prev) => [created, ...prev]);
            setNewChatName("");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to create chat");
        } finally {
            setCreating(false);
        }
    }

    async function handleDeleteChat(chatId) {
        const confirmed = window.confirm("Delete this chat?");
        if (!confirmed) return;

        setDeletingId(chatId);
        setError("");

        try {
            await deleteChat(chatId);
            setChats((prev) => prev.filter((chat) => chat.id !== chatId));

            if (selectedChat?.id === chatId) {
                setSelectedChat(null);
            }
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to delete chat");
        } finally {
            setDeletingId(null);
        }
    }

    function handleOpenChat(chat) {
        setSelectedChat(chat);
    }

    function handleBackToChats() {
        setSelectedChat(null);
    }

    if (selectedChat) {
        return <ChatDetailPage chat={selectedChat} onBack={handleBackToChats} />;
    }

    return (
        <AppShell
            pageTitle="Chats"
            pageSubtitle="Create and manage chat sessions"
        >
            <div style={styles.page}>
                <div style={styles.container}>
                    <div style={styles.header}>
                        <div>
                            <h1 style={styles.title}>Chats</h1>
                            <p style={styles.subtitle}>Create and manage chat sessions</p>
                        </div>
                    </div>

                    {error ? <div style={styles.error}>{error}</div> : null}

                    <form onSubmit={handleCreateChat} style={styles.form}>
                        <input
                            type="text"
                            placeholder="Enter chat name"
                            value={newChatName}
                            onChange={(e) => setNewChatName(e.target.value)}
                            style={styles.input}
                        />
                        <button type="submit" disabled={creating} style={styles.primaryButton}>
                            {creating ? "Creating..." : "Create Chat"}
                        </button>
                    </form>

                    <div style={styles.card}>
                        {loading ? (
                            <p style={styles.muted}>Loading chats...</p>
                        ) : chats.length === 0 ? (
                            <p style={styles.muted}>No chats found yet.</p>
                        ) : (
                            <div style={styles.list}>
                                {chats.map((chat) => (
                                    <div key={chat.id} style={styles.chatItem}>
                                        <div style={styles.chatContent}>
                                            <div style={styles.chatName}>
                                                {chat.name || chat.title || "Untitled Chat"}
                                            </div>

                                            <div style={styles.chatMeta}>
                                                <span>ID: {chat.id}</span>
                                                {chat.created_at ? (
                                                    <span>
                                                        Created: {new Date(chat.created_at).toLocaleString()}
                                                    </span>
                                                ) : null}
                                            </div>
                                        </div>

                                        <div style={styles.actions}>
                                            <button
                                                type="button"
                                                style={styles.secondaryButton}
                                                onClick={() => handleOpenChat(chat)}
                                            >
                                                Open
                                            </button>

                                            <button
                                                type="button"
                                                style={styles.dangerButton}
                                                onClick={() => handleDeleteChat(chat.id)}
                                                disabled={deletingId === chat.id}
                                            >
                                                {deletingId === chat.id ? "Deleting..." : "Delete"}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AppShell>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        background: "#0f172a",
        color: "#ffffff",
        padding: "24px",
    },
    container: {
        maxWidth: "900px",
        margin: "0 auto",
    },
    header: {
        marginBottom: "24px",
    },
    title: {
        margin: 0,
        fontSize: "30px",
        fontWeight: "700",
    },
    subtitle: {
        marginTop: "8px",
        color: "#9ca3af",
    },
    form: {
        display: "flex",
        gap: "12px",
        marginBottom: "20px",
        flexWrap: "wrap",
    },
    input: {
        flex: 1,
        minWidth: "260px",
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "#111827",
        color: "#ffffff",
        outline: "none",
    },
    primaryButton: {
        padding: "12px 16px",
        borderRadius: "10px",
        border: "none",
        background: "#2563eb",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
    secondaryButton: {
        padding: "10px 14px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "transparent",
        color: "#ffffff",
        cursor: "pointer",
    },
    dangerButton: {
        padding: "10px 14px",
        borderRadius: "10px",
        border: "none",
        background: "#dc2626",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
    card: {
        background: "#111827",
        borderRadius: "16px",
        padding: "20px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
    },
    list: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
    },
    chatItem: {
        display: "flex",
        justifyContent: "space-between",
        gap: "16px",
        alignItems: "center",
        background: "#1f2937",
        border: "1px solid #374151",
        borderRadius: "12px",
        padding: "16px",
        flexWrap: "wrap",
    },
    chatContent: {
        flex: 1,
        minWidth: "260px",
    },
    chatName: {
        fontSize: "18px",
        fontWeight: "600",
        marginBottom: "8px",
    },
    chatMeta: {
        display: "flex",
        flexDirection: "column",
        gap: "4px",
        color: "#9ca3af",
        fontSize: "13px",
        wordBreak: "break-word",
    },
    actions: {
        display: "flex",
        gap: "10px",
        alignItems: "center",
    },
    muted: {
        color: "#9ca3af",
        margin: 0,
    },
    error: {
        marginBottom: "16px",
        padding: "12px",
        borderRadius: "10px",
        background: "#7f1d1d",
        color: "#fee2e2",
    },
};