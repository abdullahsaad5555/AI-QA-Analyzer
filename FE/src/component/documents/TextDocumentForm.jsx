export default function TextDocumentForm({
    fileName,
    onFileNameChange,
    content,
    onContentChange,
    onSubmit,
    creating = false,
}) {
    return (
        <form onSubmit={onSubmit} style={styles.form}>
            <input
                type="text"
                value={fileName}
                onChange={onFileNameChange}
                placeholder="File name"
                style={styles.input}
            />

            <textarea
                value={content}
                onChange={onContentChange}
                placeholder="Paste document text here..."
                rows={6}
                style={styles.textarea}
            />

            <button
                type="submit"
                disabled={creating || !fileName.trim() || !content.trim()}
                style={styles.button}
            >
                {creating ? "Creating..." : "Create Text Document"}
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
    input: {
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "#1f2937",
        color: "#ffffff",
        outline: "none",
    },
    textarea: {
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "#1f2937",
        color: "#ffffff",
        outline: "none",
        resize: "vertical",
        minHeight: "140px",
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
