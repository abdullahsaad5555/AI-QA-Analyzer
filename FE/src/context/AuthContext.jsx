import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AuthContext = createContext(null);
const MIN_LOGOUT_VISIBLE_MS = 850;

function sleep(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, ms);
    });
}

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem("access_token"));

    const [user, setUser] = useState(() => {
        const raw = localStorage.getItem("auth_user");
        return raw ? JSON.parse(raw) : null;
    });

    useEffect(() => {
        if (token) {
            localStorage.setItem("access_token", token);
        } else {
            localStorage.removeItem("access_token");
        }
    }, [token]);

    useEffect(() => {
        if (user) {
            localStorage.setItem("auth_user", JSON.stringify(user));
        } else {
            localStorage.removeItem("auth_user");
        }
    }, [user]);

    const login = (nextToken, nextUser) => {
        setToken(nextToken);
        setUser(nextUser);
    };

    const logout = async () => {
        await sleep(MIN_LOGOUT_VISIBLE_MS);

        setToken(null);
        setUser(null);

        if (window.location.pathname !== "/login") {
            window.location.replace("/login");
        }
    };

    useEffect(() => {
        function handleUnauthorized() {
            setToken(null);
            setUser(null);

            if (window.location.pathname !== "/login") {
                window.location.replace("/login");
            }
        }

        window.addEventListener("auth:unauthorized", handleUnauthorized);

        return () => {
            window.removeEventListener("auth:unauthorized", handleUnauthorized);
        };
    }, []);

    const value = useMemo(
        () => ({
            token,
            user,
            isAuthenticated: Boolean(token),
            login,
            logout,
        }),
        [token, user]
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider");
    }

    return context;
}