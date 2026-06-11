import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error?.response?.status;

        if (status === 401) {
            sessionStorage.setItem(
                "auth_redirect_message",
                "Session expired. Please log in again."
            );

            window.dispatchEvent(new CustomEvent("auth:unauthorized"));
        }

        return Promise.reject(error);
    }
);

export default api;