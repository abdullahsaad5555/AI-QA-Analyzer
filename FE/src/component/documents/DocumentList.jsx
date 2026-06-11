function getStatusBadgeStyle(status) {
    const normalized = (status || "unknown").toLowerCase();

    if (normalized === "ingested") {
        return {
            background: "#064e3b",
            border: "1px solid #10b981",
            color: "#d1fae5",
        };
    }

    if (normalized === "uploaded") {
        return {
            background: "#1e3a8a",
            border: "1px solid #60a5fa",
            color: "#dbeafe",
        };
    }

    if (normalized === "processing" || normalized === "ingesting") {
        return {
            background: "#3f2a0a",
            border: "1px solid #f59e0b",
            color: "#fde68a",
        };
    }

    if (normalized === "failed" || normalized === "error") {
        return {
            background: "#7f1d1d",
            border: "1px solid #ef4444",
            color: "#fee2e2",
        };
    }

    return {
        background: "#374151",
        border: "1px solid #6b7280",
        color: "#f3f4f6",
    };
}

export default function DocumentList({
    documents = [],
    loading = false,
    onIngest,
    onDelete,
    ingestingDocumentId = null,
    deletingDocumentId = null,
}) {
    if (loading) {
        return <p style={styles.muted}>Loading documents...</p>;
    }

    if (!documents.length) {
        return <p style={styles.muted}>No documents yet.</p>;
    }

    return (
        <div style={styles.documentList}>
            {documents.map((doc) => {
                const isIngesting = ingestingDocumentId === doc.id;
                const isDeleting = deletingDocumentId === doc.id;
                const normalizedStatus = (doc.status || "unknown").toLowerCase();
                const isAlreadyIngested = normalizedStatus === "ingested";

                return (
                    <div key={doc.id} style={styles.documentItem}>
                        <div style={styles.documentMain}>
                            <div style={styles.documentName}>
                                {doc.file_name || "Untitled Document"}
                            </div>

                            <div style={styles.documentMeta}>
                                <span>ID: {doc.id}</span>

                                <div
                                    style={{
                                        ...styles.statusBadge,
                                        ...getStatusBadgeStyle(doc.status),
                                    }}
                                >
                                    {doc.status || "unknown"}
                                </div>

                                <span>Source: {doc.source_type || "unknown"}</span>
                            </div>
                        </div>

                        <div style={styles.documentActions}>
                            <button
                                type="button"
                                style={styles.secondaryButton}
                                onClick={() => onIngest?.(doc.id)}
                                disabled={isIngesting || isDeleting || isAlreadyIngested}
                            >
                                {isAlreadyIngested
                                    ? "Ingested"
                                    : isIngesting
                                        ? "Ingesting..."
                                        : "Ingest"}
                            </button>

                            <button
                                type="button"
                                style={styles.dangerButton}
                                onClick={() => onDelete?.(doc.id)}
                                disabled={isDeleting || isIngesting}
                            >
                                {isDeleting ? "Deleting..." : "Delete"}
                            </button>
                        </div>
                    </div>
                );
            })}
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
        gap: "6px",
        color: "#9ca3af",
        fontSize: "13px",
        wordBreak: "break-word",
    },
    statusBadge: {
        display: "inline-flex",
        alignItems: "center",
        width: "fit-content",
        padding: "4px 10px",
        borderRadius: "999px",
        fontSize: "12px",
        fontWeight: "700",
        textTransform: "capitalize",
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