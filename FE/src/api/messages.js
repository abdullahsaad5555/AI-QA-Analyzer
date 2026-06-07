import api from "./client";

export async function listMessages(chatId) {
    const response = await api.get(`/chats/${chatId}/messages`);
    return response.data;
}

export async function sendMessage(chatId, content) {
    const response = await api.post(`/chats/${chatId}/messages`, {
        content,
    });

    return response.data;
}
