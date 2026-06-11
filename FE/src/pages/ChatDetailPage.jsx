import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listMessages, sendMessage } from "../api/messages";
import {
    listChatDocuments,
    createTextDocument,
    uploadDocument,
    getDocument,
    ingestDocument,
    deleteDocument,
} from "../api/documents";
import AppShell from "../component/layout/AppShell";
import ChatMessagesPanel from "../component/chats/ChatMessagesPanel";
import ChatDocumentsPanel from "../component/chats/ChatDocumentsPanel";
import ChatDocumentActionsPanel from "../component/chats/ChatDocumentActionsPanel";
import styles from "./ChatDetailPage.module.css";


export default function ChatDetailPage({ chat, onBack }) {
    const navigate = useNavigate();
    const sendAbortControllerRef = useRef(null);
    const [messages, setMessages] = useState([]);
    const [documents, setDocuments] = useState([]);

    const [loadingMessages, setLoadingMessages] = useState(true);
    const [loadingDocuments, setLoadingDocuments] = useState(true);

    const [messageInput, setMessageInput] = useState("");
    const [sendingMessage, setSendingMessage] = useState(false);
    const [pendingUserMessage, setPendingUserMessage] = useState(null);
    const [failedUserMessage, setFailedUserMessage] = useState(null);

    const [textDocName, setTextDocName] = useState("notes.txt");
    const [textDocContent, setTextDocContent] = useState("");
    const [creatingTextDoc, setCreatingTextDoc] = useState(false);

    const [uploadingFile, setUploadingFile] = useState(false);
    const [ingestingDocumentId, setIngestingDocumentId] = useState(null);
    const [deletingDocumentId, setDeletingDocumentId] = useState(null);

    const [previewDocument, setPreviewDocument] = useState(null);
    const [previewLoading, setPreviewLoading] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    function handleStopResponse() {
        if (sendAbortControllerRef.current) {
            sendAbortControllerRef.current.abort();
            sendAbortControllerRef.current = null;
        }

        setSendingMessage(false);
        setPendingUserMessage(null);
        setError("");
        setSuccess("");
    }
    async function loadMessages(silent = false) {
        if (!chat?.id) return;

        if (!silent) {
            setLoadingMessages(true);
        }

        try {
            const data = await listMessages(chat.id);
            setMessages(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to load messages");
        } finally {
            if (!silent) {
                setLoadingMessages(false);
            }
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
        setPendingUserMessage(null);
        setFailedUserMessage(null);
        setIngestingDocumentId(null);
        setDeletingDocumentId(null);
        setPreviewDocument?.(null);

        loadMessages();
        loadDocuments();

        return () => {
            if (sendAbortControllerRef.current) {
                sendAbortControllerRef.current.abort();
                sendAbortControllerRef.current = null;
            }
        };
    }, [chat?.id]);

    async function submitMessage(messageText) {
        if (sendingMessage) return;

        const trimmedMessage = messageText.trim();
        if (!trimmedMessage) return;

        const controller = new AbortController();
        sendAbortControllerRef.current = controller;

        setSendingMessage(true);
        setError("");
        setSuccess("");
        setFailedUserMessage(null);

        setPendingUserMessage({
            id: `pending-user-${Date.now()}`,
            role: "user",
            content: trimmedMessage,
            created_at: new Date().toISOString(),
        });

        setMessageInput("");

        try {
            await sendMessage(chat.id, trimmedMessage, {
                signal: controller.signal,
            });

            sendAbortControllerRef.current = null;
            setPendingUserMessage(null);
            await loadMessages(true);
            setSuccess("Message sent successfully");
        } catch (err) {
            const wasAborted = controller.signal.aborted;
            sendAbortControllerRef.current = null;
            setPendingUserMessage(null);

            if (wasAborted) {
                return;
            }

            setFailedUserMessage({
                id: `failed-user-${Date.now()}`,
                role: "user",
                content: trimmedMessage,
                created_at: new Date().toISOString(),
            });
            setError(err?.response?.data?.detail || "Failed to send message");
        } finally {
            setSendingMessage(false);
        }
    }

    async function handleSendMessage(e) {
        e.preventDefault();
        await submitMessage(messageInput);
    }

    async function handleRetryFailedMessage() {
        if (!failedUserMessage) return;
        await submitMessage(failedUserMessage.content);
    }

    async function handleCreateTextDocument(e) {
        e.preventDefault();

        if (creatingTextDoc) return;
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
        if (uploadingFile) return;

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

    async function handlePreviewDocument(documentId) {
        setPreviewLoading(true);
        setError("");

        try {
            const data = await getDocument(documentId);
            setPreviewDocument(data);
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to load document preview");
        } finally {
            setPreviewLoading(false);
        }
    }

    function handleClosePreview() {
        setPreviewDocument(null);
    }

    async function handleIngestDocument(documentId) {
        if (ingestingDocumentId === documentId) return;

        setIngestingDocumentId(documentId);
        setError("");
        setSuccess("");

        try {
            await ingestDocument(documentId);
            await loadDocuments();
            setSuccess("Document ingested successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to ingest document");
        } finally {
            setIngestingDocumentId(null);
        }
    }

    async function handleDeleteDocument(documentId) {
        if (deletingDocumentId === documentId) return;

        const confirmed = window.confirm("Delete this document?");
        if (!confirmed) return;

        setDeletingDocumentId(documentId);
        setError("");
        setSuccess("");

        try {
            await deleteDocument(documentId);
            await loadDocuments();
            setSuccess("Document deleted successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to delete document");
        } finally {
            setDeletingDocumentId(null);
        }
    }

    function handleBack() {
        if (onBack) {
            onBack();
        } else {
            navigate("/chats");
        }
    }

    const displayedMessages = useMemo(() => {
        const nextMessages = [...messages];

        if (failedUserMessage) {
            nextMessages.push({
                ...failedUserMessage,
                id: failedUserMessage.id,
            });
        }

        if (pendingUserMessage) {
            nextMessages.push(pendingUserMessage);
        }

        if (sendingMessage) {
            nextMessages.push({
                id: "assistant-thinking",
                role: "assistant",
                content: "Thinking...",
                created_at: new Date().toISOString(),
            });
        }

        return nextMessages;
    }, [messages, failedUserMessage, pendingUserMessage, sendingMessage]);

    if (!chat) {
        return (
            <AppShell pageTitle="Chat" pageSubtitle="No chat selected">
                <p className={styles.emptyText}>No chat selected.</p>
                <button
                    type="button"
                    onClick={handleBack}
                    className={styles.backButton}
                >
                    Back to Chats
                </button>
            </AppShell>
        );
    }

    return (
        <AppShell
            pageTitle={chat.name || chat.title || "Untitled Chat"}
            pageSubtitle={`Chat ID: ${chat.id}`}
        >
            {success ? <div className={styles.success}>{success}</div> : null}
            {error ? <div className={styles.error}>{error}</div> : null}

            {previewLoading ? (
                <div style={previewStyles.loadingText}>Loading document preview...</div>
            ) : null}

            <div className={styles.grid}>
                <div className={styles.column}>
                    <ChatMessagesPanel
                        messages={displayedMessages}
                        loading={loadingMessages && !messages.length}
                        failedUserMessage={failedUserMessage}
                        sendingMessage={sendingMessage}
                        messageInput={messageInput}
                        onMessageInputChange={(e) => setMessageInput(e.target.value)}
                        onSendMessage={handleSendMessage}
                        onRetryFailedMessage={handleRetryFailedMessage}
                        onStopResponse={handleStopResponse}
                    />
                </div>

                <div className={styles.column}>
                    <ChatDocumentsPanel
                        documents={documents}
                        loading={loadingDocuments}
                        ingestingDocumentId={ingestingDocumentId}
                        deletingDocumentId={deletingDocumentId}
                        onPreview={handlePreviewDocument}
                        onIngest={handleIngestDocument}
                        onDelete={handleDeleteDocument}
                    />

                    <ChatDocumentActionsPanel
                        textDocName={textDocName}
                        textDocContent={textDocContent}
                        creatingTextDoc={creatingTextDoc}
                        uploadingFile={uploadingFile}
                        onFileNameChange={(e) => setTextDocName(e.target.value)}
                        onContentChange={(e) => setTextDocContent(e.target.value)}
                        onCreateTextDocument={handleCreateTextDocument}
                        onUploadFile={handleUploadFile}
                    />

                    <button
                        type="button"
                        onClick={handleBack}
                        className={styles.backButton}
                    >
                        Back to Chats
                    </button>
                </div>
            </div>

            {previewDocument ? (
                <div style={previewStyles.overlay}>
                    <div style={previewStyles.modal}>
                        <div style={previewStyles.header}>
                            <div>
                                <h3 style={previewStyles.title}>
                                    {previewDocument.file_name || "Document Preview"}
                                </h3>
                                <p style={previewStyles.subtitle}>ID: {previewDocument.id}</p>
                            </div>

                            <button
                                type="button"
                                onClick={handleClosePreview}
                                style={previewStyles.closeButton}
                            >
                                Close
                            </button>
                        </div>

                        <div style={previewStyles.meta}>
                            <span>Status: {previewDocument.status || "unknown"}</span>
                            <span>Source: {previewDocument.source_type || "unknown"}</span>
                            <span>Version: {previewDocument.version}</span>
                            <span>MIME: {previewDocument.mime_type || "unknown"}</span>
                        </div>

                        <div style={previewStyles.body}>
                            <pre style={previewStyles.content}>
                                {previewDocument.raw_text || "No preview text available."}
                            </pre>
                        </div>
                    </div>
                </div>
            ) : null}
        </AppShell>
    );
}

const previewStyles = {
    overlay: {
        position: "fixed",
        inset: 0,
        background: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        zIndex: 1000,
    },
    modal: {
        width: "100%",
        maxWidth: "900px",
        maxHeight: "85vh",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        background: "#111827",
        border: "1px solid #374151",
        borderRadius: "16px",
        boxShadow: "0 20px 40px rgba(0,0,0,0.45)",
    },
    header: {
        display: "flex",
        justifyContent: "space-between",
        gap: "16px",
        alignItems: "flex-start",
        padding: "20px",
        borderBottom: "1px solid #374151",
    },
    title: {
        margin: 0,
        color: "#ffffff",
        fontSize: "20px",
    },
    subtitle: {
        margin: "6px 0 0 0",
        color: "#9ca3af",
        fontSize: "13px",
    },
    meta: {
        display: "flex",
        gap: "16px",
        flexWrap: "wrap",
        padding: "14px 20px",
        borderBottom: "1px solid #374151",
        color: "#cbd5e1",
        fontSize: "14px",
    },
    body: {
        padding: "20px",
        overflowY: "auto",
    },
    content: {
        margin: 0,
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        lineHeight: 1.6,
        color: "#e5e7eb",
        fontFamily: "inherit",
    },
    closeButton: {
        padding: "10px 14px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "transparent",
        color: "#ffffff",
        cursor: "pointer",
    },
    loadingText: {
        marginBottom: "12px",
        color: "#cbd5e1",
    },
};