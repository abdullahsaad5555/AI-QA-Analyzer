import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    createChat,
    deleteChat,
    listChats,
    updateChat,
} from "../api/chats";
import AppShell from "../component/layout/AppShell";

export default function ChatsPage() {
    const navigate = useNavigate();

    const [chats, setChats] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [newChatName, setNewChatName] = useState("");
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [renamingId, setRenamingId] = useState(null);
    const [editingChatId, setEditingChatId] = useState(null);
    const [editingName, setEditingName] = useState("");
    const [error, setError] = useState("");
    const [chatNameNotice, setChatNameNotice] = useState("");

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

    function handleNewChatNameChange(e) {
        setNewChatName(e.target.value);

        if (chatNameNotice) {
            setChatNameNotice("");
        }
    }

    async function handleCreateChat(e) {
        e.preventDefault();

        if (creating) return;

        const trimmedName = newChatName.trim();

        if (!trimmedName) {
            setChatNameNotice("Please enter a chat name");

            window.setTimeout(() => {
                setChatNameNotice("");
            }, 2200);

            return;
        }

        setCreating(true);
        setError("");
        setChatNameNotice("");

        try {
            const created = await createChat({
                name: trimmedName,
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
        if (deletingId === chatId || renamingId || creating) return;

        const confirmed = window.confirm("Delete this chat?");
        if (!confirmed) return;

        setDeletingId(chatId);
        setError("");

        try {
            await deleteChat(chatId);
            setChats((prev) => prev.filter((chat) => chat.id !== chatId));

            if (editingChatId === chatId) {
                setEditingChatId(null);
                setEditingName("");
            }
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to delete chat");
        } finally {
            setDeletingId(null);
        }
    }

    function handleOpenChat(chat) {
        if (creating || deletingId || renamingId) return;
        navigate(`/chats/${chat.id}`);
    }

    function handleStartRename(chat) {
        if (creating || deletingId || renamingId) return;

        setEditingChatId(chat.id);
        setEditingName(chat.name || chat.title || "");
        setError("");
    }

    function handleCancelRename() {
        if (renamingId) return;

        setEditingChatId(null);
        setEditingName("");
    }

    async function handleSaveRename(chatId) {
        if (renamingId === chatId || deletingId || creating) return;

        const trimmedName = editingName.trim();
        if (!trimmedName) return;

        setRenamingId(chatId);
        setError("");

        try {
            const updated = await updateChat(chatId, { name: trimmedName });

            setChats((prev) =>
                prev.map((chat) => (chat.id === chatId ? updated : chat))
            );

            setEditingChatId(null);
            setEditingName("");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to rename chat");
        } finally {
            setRenamingId(null);
        }
    }

    const filteredChats = useMemo(() => {
        const normalizedSearch = searchTerm.trim().toLowerCase();

        if (!normalizedSearch) return chats;

        return chats.filter((chat) => {
            const name = (chat.name || chat.title || "").toLowerCase();
            return name.includes(normalizedSearch);
        });
    }, [chats, searchTerm]);

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

                    {chatNameNotice ? (
                        <div
                            style={{
                                marginBottom: "12px",
                                padding: "10px 12px",
                                borderRadius: "10px",
                                background: "#78350f",
                                border: "1px solid #f59e0b",
                                color: "#fef3c7",
                                fontSize: "14px",
                                fontWeight: "600",
                            }}
                        >
                            {chatNameNotice}
                        </div>
                    ) : null}

                    <form onSubmit={handleCreateChat} style={styles.form}>
                        <input
                            type="text"
                            placeholder="Enter chat name"
                            value={newChatName}
                            onChange={handleNewChatNameChange}
                            style={styles.input}
                            disabled={creating}
                        />
                        <button
                            type="submit"
                            disabled={creating}
                            style={styles.primaryButton}
                        >
                            {creating ? "Creating..." : "Create Chat"}
                        </button>
                    </form>

                    <div style={{ marginBottom: "16px" }}>
                        <input
                            type="text"
                            placeholder="Search chats..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={styles.input}
                        />
                    </div>

                    <div style={styles.card}>
                        {loading ? (
                            <p style={styles.muted}>Loading chats...</p>
                        ) : chats.length === 0 ? (
                            <p style={styles.muted}>No chats found yet.</p>
                        ) : filteredChats.length === 0 ? (
                            <p style={styles.muted}>No chats match your search.</p>
                        ) : (
                            <div style={styles.list}>
                                {filteredChats.map((chat) => {
                                    const isEditing = editingChatId === chat.id;
                                    const isRenaming = renamingId === chat.id;
                                    const isDeleting = deletingId === chat.id;
                                    const isBusy =
                                        creating ||
                                        isRenaming ||
                                        isDeleting ||
                                        Boolean(deletingId) ||
                                        Boolean(renamingId);

                                    return (
                                        <div key={chat.id} style={styles.chatItem}>
                                            <div style={styles.chatContent}>
                                                {isEditing ? (
                                                    <div style={styles.renameRow}>
                                                        <input
                                                            type="text"
                                                            value={editingName}
                                                            onChange={(e) => setEditingName(e.target.value)}
                                                            style={styles.renameInput}
                                                            autoFocus
                                                            disabled={isRenaming}
                                                        />
                                                    </div>
                                                ) : (
                                                    <div style={styles.chatName}>
                                                        {chat.name || chat.title || "Untitled Chat"}
                                                    </div>
                                                )}

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
                                                {isEditing ? (
                                                    <>
                                                        <button
                                                            type="button"
                                                            style={styles.primarySmallButton}
                                                            onClick={() => handleSaveRename(chat.id)}
                                                            disabled={
                                                                isRenaming ||
                                                                !editingName.trim() ||
                                                                Boolean(deletingId) ||
                                                                creating
                                                            }
                                                        >
                                                            {isRenaming ? "Saving..." : "Save"}
                                                        </button>

                                                        <button
                                                            type="button"
                                                            style={styles.secondaryButton}
                                                            onClick={handleCancelRename}
                                                            disabled={isRenaming}
                                                        >
                                                            Cancel
                                                        </button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button
                                                            type="button"
                                                            style={styles.secondaryButton}
                                                            onClick={() => handleOpenChat(chat)}
                                                            disabled={isBusy}
                                                        >
                                                            Open
                                                        </button>

                                                        <button
                                                            type="button"
                                                            style={styles.secondaryButton}
                                                            onClick={() => handleStartRename(chat)}
                                                            disabled={isBusy}
                                                        >
                                                            Rename
                                                        </button>

                                                        <button
                                                            type="button"
                                                            style={styles.dangerButton}
                                                            onClick={() => handleDeleteChat(chat.id)}
                                                            disabled={isDeleting || creating || Boolean(renamingId)}
                                                        >
                                                            {isDeleting ? "Deleting..." : "Delete"}
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
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
    renameInput: {
        width: "100%",
        padding: "10px 12px",
        borderRadius: "10px",
        border: "1px solid #4b5563",
        background: "#111827",
        color: "#ffffff",
        outline: "none",
        fontSize: "16px",
        fontWeight: "600",
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
    primarySmallButton: {
        padding: "10px 14px",
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
    renameRow: {
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
        flexWrap: "wrap",
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