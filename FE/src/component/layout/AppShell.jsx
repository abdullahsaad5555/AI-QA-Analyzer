import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function AppShell({
    children,
    pageTitle = "AI QA Analyzer",
    pageSubtitle = "",
}) {
    const { user, logout } = useAuth();
    const [loggingOut, setLoggingOut] = useState(false);

    async function handleLogout() {
        if (loggingOut) return;

        setLoggingOut(true);

        try {
            await logout();
        } finally {
            setLoggingOut(false);
        }
    }

    return (
        <div style={styles.page}>
            <ShellAnimations />

            {loggingOut ? <ShellLoadingOverlay text="Signing you out ..." /> : null}

            <div style={styles.container}>
                <header style={styles.header}>
                    <div>
                        <h1 style={styles.brand}>AI QA Analyzer</h1>
                        <p style={styles.brandSubtitle}>Ask Away And Unlock The Magic</p>
                    </div>

                    <div style={styles.userArea}>
                        <div style={styles.userInfo}>
                            <span style={styles.userLabel}>Signed in as</span>
                            <span style={styles.userEmail}>{user?.email || "Unknown user"}</span>
                        </div>

                        <button
                            type="button"
                            onClick={handleLogout}
                            disabled={loggingOut}
                            style={styles.logoutButton}
                        >
                            {loggingOut ? (
                                <span style={styles.logoutButtonContent}>
                                    <span style={styles.logoutSpinner} />
                                    <span>Signing out...</span>
                                </span>
                            ) : (
                                "Logout"
                            )}
                        </button>
                    </div>
                </header>

                <main style={styles.main}>
                    <div style={styles.pageHeader}>
                        <h2 style={styles.pageTitle}>{pageTitle}</h2>
                        {pageSubtitle ? <p style={styles.pageSubtitle}>{pageSubtitle}</p> : null}
                    </div>

                    <div style={styles.content}>{children}</div>
                </main>
            </div>
        </div>
    );
}

function ShellLoadingOverlay({ text }) {
    return (
        <div style={styles.overlay} aria-live="polite" aria-busy="true">
            <div style={styles.overlayCard}>
                <div style={styles.loaderWrap}>
                    <div style={styles.loaderOuter} />
                    <div style={styles.loaderInner} />
                    <div style={styles.loaderCore} />
                </div>
                <div style={styles.overlayText}>{text}</div>
            </div>
        </div>
    );
}

function ShellAnimations() {
    return (
        <style>
            {`
        @keyframes shell-spin {
          to { transform: rotate(360deg); }
        }

        @keyframes shell-pulse {
          0%, 100% {
            transform: scale(0.92);
            opacity: 0.85;
          }
          50% {
            transform: scale(1.08);
            opacity: 1;
          }
        }

        @keyframes shell-fade-in {
          from {
            opacity: 0;
            transform: translateY(6px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          * {
            scroll-behavior: auto !important;
          }
        }
      `}
        </style>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        background: "#0f172a",
        color: "#ffffff",
        padding: "24px",
        position: "relative",
    },
    container: {
        maxWidth: "1280px",
        margin: "0 auto",
    },
    header: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "16px",
        flexWrap: "wrap",
        marginBottom: "24px",
        padding: "20px",
        background: "#111827",
        borderRadius: "16px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
    },
    brand: {
        margin: 0,
        fontSize: "28px",
        fontWeight: "700",
    },
    brandSubtitle: {
        marginTop: "8px",
        marginBottom: 0,
        color: "#9ca3af",
    },
    userArea: {
        display: "flex",
        alignItems: "center",
        gap: "16px",
        flexWrap: "wrap",
    },
    userInfo: {
        display: "flex",
        flexDirection: "column",
        gap: "4px",
    },
    userLabel: {
        fontSize: "12px",
        color: "#93c5fd",
        textTransform: "uppercase",
        letterSpacing: "0.05em",
    },
    userEmail: {
        fontSize: "14px",
        fontWeight: "600",
        wordBreak: "break-word",
    },
    logoutButton: {
        padding: "10px 14px",
        borderRadius: "10px",
        border: "none",
        background: "#dc2626",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
    logoutButtonContent: {
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
    },
    logoutSpinner: {
        width: "16px",
        height: "16px",
        borderRadius: "999px",
        border: "2px solid rgba(255, 255, 255, 0.35)",
        borderTopColor: "#ffffff",
        animation: "shell-spin 0.75s linear infinite",
    },
    main: {
        display: "flex",
        flexDirection: "column",
        gap: "20px",
    },
    pageHeader: {
        padding: "20px",
        background: "#111827",
        borderRadius: "16px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
    },
    pageTitle: {
        margin: 0,
        fontSize: "24px",
        fontWeight: "700",
    },
    pageSubtitle: {
        marginTop: "8px",
        marginBottom: 0,
        color: "#9ca3af",
    },
    content: {
        display: "flex",
        flexDirection: "column",
        gap: "20px",
    },
    overlay: {
        position: "fixed",
        inset: 0,
        background: "rgba(15, 23, 42, 0.64)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 30,
        animation: "shell-fade-in 0.22s ease-out",
    },
    overlayCard: {
        minWidth: "240px",
        background: "rgba(17, 24, 39, 0.92)",
        border: "1px solid rgba(148, 163, 184, 0.18)",
        borderRadius: "18px",
        padding: "24px 22px",
        boxShadow: "0 20px 60px rgba(0, 0, 0, 0.45)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "16px",
    },
    loaderWrap: {
        width: "72px",
        height: "72px",
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
    },
    loaderOuter: {
        position: "absolute",
        width: "72px",
        height: "72px",
        borderRadius: "50%",
        border: "4px solid rgba(96, 165, 250, 0.18)",
        borderTopColor: "#60a5fa",
        animation: "shell-spin 1.1s linear infinite",
    },
    loaderInner: {
        position: "absolute",
        width: "46px",
        height: "46px",
        borderRadius: "50%",
        border: "4px solid rgba(168, 85, 247, 0.18)",
        borderBottomColor: "#a855f7",
        animation: "shell-spin 0.85s linear infinite reverse",
    },
    loaderCore: {
        width: "12px",
        height: "12px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #60a5fa, #a855f7)",
        boxShadow: "0 0 18px rgba(96, 165, 250, 0.6)",
        animation: "shell-pulse 1.2s ease-in-out infinite",
    },
    overlayText: {
        fontSize: "14px",
        fontWeight: "600",
        color: "#e5e7eb",
        letterSpacing: "0.01em",
        textAlign: "center",
    },
};