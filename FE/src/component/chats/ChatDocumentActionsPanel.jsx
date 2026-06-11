import TextDocumentForm from "../documents/TextDocumentForm";
import UploadDocumentForm from "../documents/UploadDocumentForm";
import styles from "./ChatDocumentActionsPanel.module.css";

export default function ChatDocumentActionsPanel({
    textDocName,
    textDocContent,
    creatingTextDoc,
    uploadingFile,
    onFileNameChange,
    onContentChange,
    onCreateTextDocument,
    onUploadFile,
}) {
    return (
        <>
            <div className={styles.card}>
                <h2 className={styles.sectionTitle}>Add Text Document</h2>

                <TextDocumentForm
                    fileName={textDocName}
                    onFileNameChange={onFileNameChange}
                    content={textDocContent}
                    onContentChange={onContentChange}
                    onSubmit={onCreateTextDocument}
                    creating={creatingTextDoc}
                />
            </div>

            <div className={styles.card}>
                <h2 className={styles.sectionTitle}>Upload File</h2>

                <UploadDocumentForm
                    onFileChange={onUploadFile}
                    uploading={uploadingFile}
                />
            </div>
        </>
    );
}
