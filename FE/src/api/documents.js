import api from "./client";

export async function listChatDocuments(chatId) {
    const response = await api.get(`/chats/${chatId}/documents`);
    return response.data;
}

export async function createTextDocument(chatId, payload) {
    const response = await api.post(`/chats/${chatId}/documents/text`, payload);
    return response.data;
}

export async function uploadDocument(chatId, file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(`/chats/${chatId}/documents/upload`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
}

export async function getDocument(documentId) {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
}

export async function updateDocument(documentId, payload) {
    const response = await api.patch(`/documents/${documentId}`, payload);
    return response.data;
}

export async function ingestDocument(documentId) {
    const response = await api.post(`/documents/${documentId}/ingest`);
    return response.data;
}

export async function deleteDocument(documentId) {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
}