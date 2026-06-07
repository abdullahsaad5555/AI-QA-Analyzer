import api from "./client";

export async function listChats() {
    const response = await api.get("/chats");
    return response.data;
}

export async function createChat(payload) {
    const response = await api.post("/chats", payload);
    return response.data;
}

export async function getChat(chatId) {
    const response = await api.get(`/chats/${chatId}`);
    return response.data;
}

export async function updateChat(chatId, payload) {
    const response = await api.patch(`/chats/${chatId}`, payload);
    return response.data;
}

export async function deleteChat(chatId) {
    const response = await api.delete(`/chats/${chatId}`);
    return response.data;
}