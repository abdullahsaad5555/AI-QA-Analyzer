import DocumentList from "../documents/DocumentList";
import styles from "./ChatDocumentsPanel.module.css";

export default function ChatDocumentsPanel({
    documents,
    loading,
    ingestingDocumentId,
    deletingDocumentId,
    onPreview,
    onIngest,
    onDelete,
}) {
    return (
        <div className={styles.card}>
            <h2 className={styles.sectionTitle}>Documents</h2>

            <DocumentList
                documents={documents}
                loading={loading}
                onPreview={onPreview}
                onIngest={onIngest}
                onDelete={onDelete}
                ingestingDocumentId={ingestingDocumentId}
                deletingDocumentId={deletingDocumentId}
            />
        </div>
    );
}