export default function DocumentList({
    documents = [],
    loading = false,
    onIngest,
    onDelete,
}) {
    if (loading) {
        return <p style={styles.muted}>Loading documents...</p>;
    }

    if (!documents.length) {
        return <p style={styles.muted}>No documents yet.</p>;
    }

    return (
        <div style={styles.documentList}>
            {documents.map((doc) => (
                <div key={doc.id} style={styles.documentItem}>
                    <div style={styles.documentMain}>
                        <div style={styles.documentName}>
                            {doc.file_name || "Untitled Document"}
                        </div>

                        <div style={styles.documentMeta}>
                            <span>ID: {doc.id}</span>
                            <span>Status: {doc.status || "unknown"}</span>
                            <span>Source: {doc.source_type || "unknown"}</span>
                        </div>
                    </div>

                    <div style={styles.documentActions}>
                        <button
                            type="button"
                            style={styles.secondaryButton}
                            onClick={() => onIngest?.(doc.id)}
                        >
                            Ingest
                        </button>

                        <button
                            type="button"
                            style={styles.dangerButton}
                            onClick={() => onDelete?.(doc.id)}
                        >
                            Delete
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}

const styles = {
    documentList: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
    },
    documentItem: {
        display: "flex",
        justifyContent: "space-between",
        gap: "12px",
        alignItems: "flex-start",
        flexWrap: "wrap",
        background: "#1f2937",
        border: "1px solid #374151",
        borderRadius: "12px",
        padding: "14px",
    },
    documentMain: {
        flex: 1,
        minWidth: "220px",
    },
    documentName: {
        fontWeight: "600",
        marginBottom: "8px",
    },
    documentMeta: {
        display: "flex",
        flexDirection: "column",
        gap: "4px",
        color: "#9ca3af",
        fontSize: "13px",
        wordBreak: "break-word",
    },
    documentActions: {
        display: "flex",
        gap: "8px",
        flexWrap: "wrap",
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
    muted: {
        color: "#9ca3af",
        margin: 0,
    },
};
