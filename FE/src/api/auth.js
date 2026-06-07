import api from "./client";

export async function sendOtp(email) {
    const response = await api.post("/auth/send-otp", {
        email,
    });

    return response.data;
}

export async function verifyOtp(email, otp) {
    const response = await api.post("/auth/verify-otp", {
        email,
        otp,
    });

    return response.data;
}
