import { useState } from "react";
import { sendOtp, verifyOtp } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
    const { login } = useAuth();

    const [step, setStep] = useState("email");
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    async function handleSendOtp(e) {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setError("");

        try {
            const data = await sendOtp(email);
            setMessage(data.message || "OTP sent successfully");
            setStep("otp");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to send OTP");
        } finally {
            setLoading(false);
        }
    }

    async function handleVerifyOtp(e) {
        e.preventDefault();
        setLoading(true);
        setMessage("");
        setError("");

        try {
            const data = await verifyOtp(email, otp);

            login(data.tokens.access_token, data.user);
            setMessage(data.message || "Logged in successfully");
        } catch (err) {
            setError(err?.response?.data?.detail || "Failed to verify OTP");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={styles.page}>
            <div style={styles.card}>
                <h1 style={styles.title}>AI QA Analyzer</h1>
                <p style={styles.subtitle}>Login with email OTP</p>

                {message ? <div style={styles.success}>{message}</div> : null}
                {error ? <div style={styles.error}>{error}</div> : null}

                {step === "email" ? (
                    <form onSubmit={handleSendOtp} style={styles.form}>
                        <label style={styles.label}>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="test@example.com"
                            required
                            style={styles.input}
                        />

                        <button type="submit" disabled={loading} style={styles.button}>
                            {loading ? "Sending..." : "Send OTP"}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} style={styles.form}>
                        <label style={styles.label}>Email</label>
                        <input value={email} disabled style={styles.input} />

                        <label style={styles.label}>OTP</label>
                        <input
                            type="text"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            placeholder="Enter OTP from backend console"
                            required
                            style={styles.input}
                        />

                        <button type="submit" disabled={loading} style={styles.button}>
                            {loading ? "Verifying..." : "Verify OTP"}
                        </button>

                        <button
                            type="button"
                            onClick={() => {
                                setStep("email");
                                setOtp("");
                                setMessage("");
                                setError("");
                            }}
                            style={styles.secondaryButton}
                        >
                            Back
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0f172a",
        color: "#ffffff",
        padding: "24px",
    },
    card: {
        width: "100%",
        maxWidth: "420px",
        background: "#111827",
        borderRadius: "16px",
        padding: "24px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
    },
    title: {
        margin: 0,
        fontSize: "28px",
        fontWeight: "700",
    },
    subtitle: {
        marginTop: "8px",
        marginBottom: "20px",
        color: "#9ca3af",
    },
    form: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
    },
    label: {
        fontSize: "14px",
        color: "#d1d5db",
    },
    input: {
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "#1f2937",
        color: "#ffffff",
        outline: "none",
    },
    button: {
        marginTop: "8px",
        padding: "12px",
        borderRadius: "10px",
        border: "none",
        background: "#2563eb",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: "600",
    },
    secondaryButton: {
        padding: "12px",
        borderRadius: "10px",
        border: "1px solid #374151",
        background: "transparent",
        color: "#ffffff",
        cursor: "pointer",
    },
    success: {
        marginBottom: "12px",
        padding: "10px",
        borderRadius: "10px",
        background: "#064e3b",
        color: "#d1fae5",
        fontSize: "14px",
    },
    error: {
        marginBottom: "12px",
        padding: "10px",
        borderRadius: "10px",
        background: "#7f1d1d",
        color: "#fee2e2",
        fontSize: "14px",
    },
};
