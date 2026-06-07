export default function MessageComposer({
    value,
    onChange,
    onSubmit,
    sending = false,
}) {
    return (
        <form onSubmit={onSubmit} style={styles.form}>
            <textarea
                value={value}
                onChange={onChange}
                placeholder="Type your message..."
                rows={4}
                style={styles.textarea}
            />

            <button
                type="submit"
                disabled={sending || !value.trim()}
                style={styles.button}
            >
                {sending ? "Sending..." : "Send Message"}
            </button>
        </form>
    );
}

const styles = {
    form: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        marginTop: "16px",
    },
    textarea: {
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "#1f2937",
        color: "#ffffff",
        outline: "none",
        resize: "vertical",
        minHeight: "120px",
    },
    button: {
        padding: "12px 16px",
        borderRadius: "10px",
        border: "none",
        background: "#2563eb",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
};
