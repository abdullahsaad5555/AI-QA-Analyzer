export default function MessageList({ messages = [], loading = false }) {
    if (loading) {
        return <p style={styles.muted}>Loading messages...</p>;
    }

    if (!messages.length) {
        return <p style={styles.muted}>No messages yet.</p>;
    }

    return (
        <div style={styles.messageList}>
            {messages.map((msg) => (
                <div
                    key={msg.id}
                    style={{
                        ...styles.messageItem,
                        ...(msg.role === "assistant"
                            ? styles.assistantMessage
                            : msg.role === "user"
                                ? styles.userMessage
                                : styles.systemMessage),
                    }}
                >
                    <div style={styles.messageHeader}>
                        <span style={styles.messageRole}>{msg.role}</span>

                        {msg.created_at ? (
                            <span style={styles.messageTime}>
                                {new Date(msg.created_at).toLocaleString()}
                            </span>
                        ) : null}
                    </div>

                    <div style={styles.messageContent}>{msg.content}</div>
                </div>
            ))}
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
    muted: {
        color: "#9ca3af",
        margin: 0,
    },
};
