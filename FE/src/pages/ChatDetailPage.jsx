import { useEffect, useState } from "react";
import { listMessages, sendMessage } from "../api/messages";
import {
    listChatDocuments,
    createTextDocument,
    uploadDocument,
    ingestDocument,
    deleteDocument,
} from "../api/documents";

import MessageComposer from "../component/messages/MessageComposer";
import MessageList from "../component/messages/MessageList";
import DocumentList from "../component/documents/DocumentList";
import TextDocumentForm from "../component/documents/TextDocumentForm";
import UploadDocumentForm from "../component/documents/UploadDocumentForm";
import AppShell from "../component/layout/AppShell";

export default function ChatDetailPage({ chat, onBack }) {
    const [messages, setMessages] = useState([]);
    const [documents, setDocuments] = useState([]);

    const [loadingMessages, setLoadingMessages] = useState(true);
    const [loadingDocuments, setLoadingDocuments] = useState(true);

    const [messageInput, setMessageInput] = useState("");
    const [sendingMessage, setSendingMessage] = useState(false);

    const [textDocName, setTextDocName] = useState("notes.txt");
    const [textDocContent, setTextDocContent] = useState("");
    const [creatingTextDoc, setCreatingTextDoc] = useState(false);

    const [uploadingFile, setUploadingFile] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    async function loadMessages() {
        if (!chat?.id) return;

        setLoadingMessages(true);

        try {
            const data = await listMessages(chat.id);
            setMessages(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to load messages");
        } finally {
            setLoadingMessages(false);
        }
    }

    async function loadDocuments() {
        if (!chat?.id) return;

        setLoadingDocuments(true);

        try {
            const data = await listChatDocuments(chat.id);
            setDocuments(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to load documents");
        } finally {
            setLoadingDocuments(false);
        }
    }

    useEffect(() => {
        loadMessages();
        loadDocuments();
    }, [chat?.id]);

    async function handleSendMessage(e) {
        e.preventDefault();

        if (!messageInput.trim()) return;

        setSendingMessage(true);
        setError("");
        setSuccess("");

        try {
            await sendMessage(chat.id, messageInput.trim());
            setMessageInput("");
            await loadMessages();
            setSuccess("Message sent successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to send message");
        } finally {
            setSendingMessage(false);
        }
    }

    async function handleCreateTextDocument(e) {
        e.preventDefault();

        if (!textDocName.trim() || !textDocContent.trim()) return;

        setCreatingTextDoc(true);
        setError("");
        setSuccess("");

        try {
            await createTextDocument(chat.id, {
                file_name: textDocName.trim(),
                raw_text: textDocContent.trim(),
            });

            setTextDocContent("");
            await loadDocuments();
            setSuccess("Text document created successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to create text document");
        } finally {
            setCreatingTextDoc(false);
        }
    }

    async function handleUploadFile(e) {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploadingFile(true);
        setError("");
        setSuccess("");

        try {
            await uploadDocument(chat.id, file);
            await loadDocuments();
            setSuccess("File uploaded successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to upload file");
        } finally {
            setUploadingFile(false);
            e.target.value = "";
        }
    }

    async function handleIngestDocument(documentId) {
        setError("");
        setSuccess("");

        try {
            await ingestDocument(documentId);
            await loadDocuments();
            setSuccess("Document ingested successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to ingest document");
        }
    }

    async function handleDeleteDocument(documentId) {
        const confirmed = window.confirm("Delete this document?");
        if (!confirmed) return;

        setError("");
        setSuccess("");

        try {
            await deleteDocument(documentId);
            await loadDocuments();
            setSuccess("Document deleted successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to delete document");
        }
    }

    if (!chat) {
        return (
            <AppShell pageTitle="Chat" pageSubtitle="No chat selected">
                <p style={styles.emptyText}>No chat selected.</p>
            </AppShell>
        );
    }

    return (
        <AppShell
            pageTitle={chat.name || chat.title || "Untitled Chat"}
            pageSubtitle={`Chat ID: ${chat.id}`}
        >
            {success ? <div style={styles.success}>{success}</div> : null}
            {error ? <div style={styles.error}>{error}</div> : null}

            <div style={styles.grid}>
                <div style={styles.column}>
                    <div style={styles.card}>
                        <h2 style={styles.sectionTitle}>Messages</h2>

                        <MessageList messages={messages} loading={loadingMessages} />

                        <MessageComposer
                            value={messageInput}
                            onChange={(e) => setMessageInput(e.target.value)}
                            onSubmit={handleSendMessage}
                            sending={sendingMessage}
                        />
                    </div>
                </div>

                <div style={styles.column}>
                    <div style={styles.card}>
                        <h2 style={styles.sectionTitle}>Documents</h2>

                        <DocumentList
                            documents={documents}
                            loading={loadingDocuments}
                            onIngest={handleIngestDocument}
                            onDelete={handleDeleteDocument}
                        />
                    </div>

                    <div style={styles.card}>
                        <h2 style={styles.sectionTitle}>Add Text Document</h2>

                        <TextDocumentForm
                            fileName={textDocName}
                            onFileNameChange={(e) => setTextDocName(e.target.value)}
                            content={textDocContent}
                            onContentChange={(e) => setTextDocContent(e.target.value)}
                            onSubmit={handleCreateTextDocument}
                            creating={creatingTextDoc}
                        />
                    </div>

                    <div style={styles.card}>
                        <h2 style={styles.sectionTitle}>Upload File</h2>

                        <UploadDocumentForm
                            onFileChange={handleUploadFile}
                            uploading={uploadingFile}
                        />
                    </div>

                    {onBack ? (
                        <button type="button" onClick={onBack} style={styles.backButton}>
                            Back to Chats
                        </button>
                    ) : null}
                </div>
            </div>
        </AppShell>
    );
}

const styles = {
    grid: {
        display: "grid",
        gridTemplateColumns: "1.4fr 1fr",
        gap: "20px",
    },
    column: {
        display: "flex",
        flexDirection: "column",
        gap: "20px",
    },
    card: {
        background: "#111827",
        borderRadius: "16px",
        padding: "20px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
    },
    sectionTitle: {
        marginTop: 0,
        marginBottom: "16px",
        fontSize: "20px",
        color: "#ffffff",
    },
    success: {
        marginBottom: "16px",
        padding: "12px",
        borderRadius: "10px",
        background: "#064e3b",
        color: "#d1fae5",
    },
    error: {
        marginBottom: "16px",
        padding: "12px",
        borderRadius: "10px",
        background: "#7f1d1d",
        color: "#fee2e2",
    },
    backButton: {
        padding: "12px 16px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "transparent",
        color: "#ffffff",
        cursor: "pointer",
    },
    emptyText: {
        color: "#d1d5db",
        margin: 0,
    },
};