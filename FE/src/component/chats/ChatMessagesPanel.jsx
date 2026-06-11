import MessageComposer from "../messages/MessageComposer";
import MessageList from "../messages/MessageList";
import styles from "./ChatMessagesPanel.module.css";

export default function ChatMessagesPanel({
    messages,
    loading,
    failedUserMessage,
    sendingMessage,
    messageInput,
    onMessageInputChange,
    onSendMessage,
    onRetryFailedMessage,
    onStopResponse,
}) {
    return (
        <div className={styles.card}>
            <h2 className={styles.sectionTitle}>Messages</h2>

            <MessageList messages={messages} loading={loading} />

            {failedUserMessage ? (
                <div className={styles.retryCard}>
                    <div className={styles.retryText}>
                        Message failed to send. You can retry without retyping.
                    </div>

                    <button
                        type="button"
                        onClick={onRetryFailedMessage}
                        disabled={sendingMessage}
                        className={styles.retryButton}
                    >
                        {sendingMessage ? "Retrying..." : "Retry"}
                    </button>
                </div>
            ) : null}

            {sendingMessage ? (
                <div style={localStyles.stopRow}>
                    <button
                        type="button"
                        onClick={onStopResponse}
                        style={localStyles.stopButton}
                    >
                        Stop Response
                    </button>
                </div>
            ) : null}

            <MessageComposer
                value={messageInput}
                onChange={onMessageInputChange}
                onSubmit={onSendMessage}
                sending={sendingMessage}
            />
        </div>
    );
}

const localStyles = {
    stopRow: {
        marginTop: "12px",
        display: "flex",
        justifyContent: "flex-end",
    },
    stopButton: {
        padding: "10px 14px",
        borderRadius: "10px",
        border: "1px solid #dc2626",
        background: "transparent",
        color: "#fecaca",
        cursor: "pointer",
        fontWeight: "700",
    },
};