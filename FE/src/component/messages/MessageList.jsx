import { useEffect, useRef, useState } from "react";

export default function MessageList({ messages = [], loading = false }) {
    const listRef = useRef(null);
    const [thinkingDots, setThinkingDots] = useState("");

    useEffect(() => {
        if (loading) return;

        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [messages, loading]);

    useEffect(() => {
        const hasThinkingMessage = messages.some(
            (msg) => msg.id === "assistant-thinking"
        );

        if (!hasThinkingMessage) {
            setThinkingDots("");
            return;
        }

        const interval = window.setInterval(() => {
            setThinkingDots((prev) => {
                if (prev === "") return ".";
                if (prev === ".") return "..";
                if (prev === "..") return "...";
                return "";
            });
        }, 450);

        return () => window.clearInterval(interval);
    }, [messages]);

    if (loading) {
        return <p style={styles.muted}>Loading messages...</p>;
    }

    if (!messages.length) {
        return <p style={styles.muted}>No messages yet.</p>;
    }

    return (
        <div ref={listRef} style={styles.messageList}>
            {messages.map((msg) => {
                const isThinking = msg.id === "assistant-thinking";

                return (
                    <div
                        key={msg.id}
                        style={{
                            ...styles.messageItem,
                            ...(isThinking
                                ? styles.thinkingMessage
                                : msg.role === "assistant"
                                    ? styles.assistantMessage
                                    : msg.role === "user"
                                        ? styles.userMessage
                                        : styles.systemMessage),
                        }}
                    >
                        <div style={styles.messageHeader}>
                            <span style={styles.messageRole}>
                                {isThinking ? "assistant" : msg.role}
                            </span>

                            {msg.created_at ? (
                                <span style={styles.messageTime}>
                                    {new Date(msg.created_at).toLocaleString()}
                                </span>
                            ) : null}
                        </div>

                        <div
                            style={{
                                ...styles.messageContent,
                                ...(isThinking ? styles.thinkingContent : null),
                            }}
                        >
                            {isThinking ? (
                                <span>
                                    Thinking
                                    <span style={styles.thinkingDots}>{thinkingDots}</span>
                                </span>
                            ) : (
                                msg.content
                            )}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

const styles = {
    messageList: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        maxHeight: "420px",
        overflowY: "auto",
        paddingRight: "4px",
    },
    messageItem: {
        borderRadius: "12px",
        padding: "14px",
        border: "1px solid #374151",
    },
    userMessage: {
        background: "#172554",
    },
    assistantMessage: {
        background: "#052e16",
    },
    systemMessage: {
        background: "#3f3f46",
    },
    thinkingMessage: {
        background: "#1e293b",
        border: "1px dashed #60a5fa",
    },
    messageHeader: {
        display: "flex",
        justifyContent: "space-between",
        gap: "12px",
        marginBottom: "8px",
        flexWrap: "wrap",
    },
    messageRole: {
        fontWeight: "700",
        textTransform: "capitalize",
    },
    messageTime: {
        fontSize: "12px",
        color: "#cbd5e1",
    },
    messageContent: {
        whiteSpace: "pre-wrap",
        lineHeight: 1.6,
    },
    thinkingContent: {
        fontStyle: "italic",
        color: "#bfdbfe",
    },
    thinkingDots: {
        display: "inline-block",
        minWidth: "24px",
    },
    muted: {
        color: "#9ca3af",
        margin: 0,
    },
};