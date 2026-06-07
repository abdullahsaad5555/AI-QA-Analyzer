export default function UploadDocumentForm({
    onFileChange,
    uploading = false,
}) {
    return (
        <div style={styles.wrapper}>
            <label style={styles.uploadLabel}>
                <input
                    type="file"
                    onChange={onFileChange}
                    style={{ display: "none" }}
                />
                <span style={styles.uploadButton}>
                    {uploading ? "Uploading..." : "Choose File"}
                </span>
            </label>

            <p style={styles.helperText}>Supported: .txt, .pdf, .docx</p>
        </div>
    );
}

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        marginTop: "8px",
    },
    uploadLabel: {
        display: "inline-block",
    },
    uploadButton: {
        display: "inline-block",
        padding: "12px 16px",
        borderRadius: "10px",
        background: "#2563eb",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
    helperText: {
        margin: 0,
        color: "#9ca3af",
        fontSize: "14px",
    },
};