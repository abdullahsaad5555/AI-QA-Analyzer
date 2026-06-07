import { useAuth } from "../../context/AuthContext";

export default function AppShell({
    children,
    pageTitle = "AI QA Analyzer",
    pageSubtitle = "",
}) {
    const { user, logout } = useAuth();

    return (
        <div style={styles.page}>
            <div style={styles.container}>
                <header style={styles.header}>
                    <div>
                        <h1 style={styles.brand}>AI QA Analyzer</h1>
                        <p style={styles.brandSubtitle}>Local frontend workspace</p>
                    </div>

                    <div style={styles.userArea}>
                        <div style={styles.userInfo}>
                            <span style={styles.userLabel}>Signed in as</span>
                            <span style={styles.userEmail}>{user?.email || "Unknown user"}</span>
                        </div>

                        <button type="button" onClick={logout} style={styles.logoutButton}>
                            Logout
                        </button>
                    </div>
                </header>

                <main style={styles.main}>
                    <div style={styles.pageHeader}>
                        <h2 style={styles.pageTitle}>{pageTitle}</h2>
                        {pageSubtitle ? (
                            <p style={styles.pageSubtitle}>{pageSubtitle}</p>
                        ) : null}
                    </div>

                    <div style={styles.content}>{children}</div>
                </main>
            </div>
        </div>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        background: "#0f172a",
        color: "#ffffff",
        padding: "24px",
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
};
