import { useEffect, useMemo, useRef, useState } from "react";
import { sendOtp, verifyOtp } from "../api/auth";
import { useAuth } from "../context/AuthContext";

const MIN_LOADING_VISIBLE_MS = 850;

function sleep(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, ms);
    });
}

export default function LoginPage() {
    const { login } = useAuth();

    const otpInputRef = useRef(null);

    const [step, setStep] = useState("email");
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");

    const [loading, setLoading] = useState(false);
    const [loadingAction, setLoadingAction] = useState("");

    const [message, setMessage] = useState("");
    const [sessionNotice, setSessionNotice] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        const redirectMessage = sessionStorage.getItem("auth_redirect_message");

        if (redirectMessage) {
            setSessionNotice(redirectMessage);
            sessionStorage.removeItem("auth_redirect_message");
        }
    }, []);

    useEffect(() => {
        if (step === "otp") {
            otpInputRef.current?.focus();
        }
    }, [step]);

    useEffect(() => {
        if (!message) return;

        const timeout = window.setTimeout(() => {
            setMessage("");
        }, 2500);

        return () => window.clearTimeout(timeout);
    }, [message]);

    const loadingText = useMemo(() => {
        if (loadingAction === "sendOtp") {
            return "Sending your code ...";
        }

        if (loadingAction === "verifyOtp") {
            return "Signing you in ...";
        }

        return "Getting things ready ...";
    }, [loadingAction]);

    function resetFeedback() {
        setMessage("");
        setError("");
    }

    function handleEmailChange(e) {
        setEmail(e.target.value);
        setError("");
    }

    function handleOtpChange(e) {
        setOtp(e.target.value);
        setError("");
    }

    async function ensureMinimumLoaderTime(startedAt) {
        const elapsed = Date.now() - startedAt;
        const remaining = MIN_LOADING_VISIBLE_MS - elapsed;

        if (remaining > 0) {
            await sleep(remaining);
        }
    }

    async function handleSendOtp(e) {
        e.preventDefault();

        if (loading) return;

        const startedAt = Date.now();

        setLoading(true);
        setLoadingAction("sendOtp");
        setMessage("");
        setSessionNotice("");
        setError("");

        try {
            const data = await sendOtp(email);
            await ensureMinimumLoaderTime(startedAt);

            setMessage(data.message || "OTP sent successfully");
            setStep("otp");
        } catch (err) {
            await ensureMinimumLoaderTime(startedAt);
            setError(err?.response?.data?.detail || "Failed to send OTP");
        } finally {
            setLoading(false);
            setLoadingAction("");
        }
    }

    async function handleVerifyOtp(e) {
        e.preventDefault();

        if (loading) return;

        const startedAt = Date.now();

        setLoading(true);
        setLoadingAction("verifyOtp");
        setMessage("");
        setSessionNotice("");
        setError("");

        try {
            const data = await verifyOtp(email, otp);
            await ensureMinimumLoaderTime(startedAt);

            login(data.tokens.access_token, data.user);
            setMessage(data.message || "Logged in successfully");
        } catch (err) {
            await ensureMinimumLoaderTime(startedAt);
            setError(err?.response?.data?.detail || "Failed to verify OTP");
        } finally {
            setLoading(false);
            setLoadingAction("");
        }
    }

    return (
        <div style={styles.page}>
            <LoadingAnimations />

            {loading ? <AuthLoadingOverlay text={loadingText} /> : null}

            <div style={styles.card}>
                <h1 style={styles.title}>AI QA Analyzer</h1>
                <p style={styles.subtitle}>Login with email OTP</p>

                {sessionNotice ? (
                    <Banner
                        text={sessionNotice}
                        style={styles.sessionNotice}
                        onDismiss={() => setSessionNotice("")}
                    />
                ) : null}

                {message ? (
                    <Banner
                        text={message}
                        style={styles.success}
                        onDismiss={() => setMessage("")}
                    />
                ) : null}

                {error ? (
                    <Banner
                        text={error}
                        style={styles.error}
                        onDismiss={() => setError("")}
                    />
                ) : null}

                {step === "email" ? (
                    <form onSubmit={handleSendOtp} style={styles.form}>
                        <label style={styles.label}>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={handleEmailChange}
                            placeholder="test@example.com"
                            required
                            disabled={loading}
                            style={styles.input}
                        />

                        <button
                            type="submit"
                            disabled={loading || !email.trim()}
                            style={styles.button}
                        >
                            <ButtonContent
                                loading={loading}
                                loadingText="Sending..."
                                defaultText="Send OTP"
                            />
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} style={styles.form}>
                        <label style={styles.label}>Email</label>
                        <input value={email} disabled style={styles.input} />

                        <label style={styles.label}>OTP</label>
                        <input
                            ref={otpInputRef}
                            type="text"
                            value={otp}
                            onChange={handleOtpChange}
                            placeholder="Enter OTP sent on email"
                            required
                            disabled={loading}
                            style={styles.input}
                        />

                        <p style={styles.helperText}>Enter the OTP sent to your email.</p>

                        <button
                            type="submit"
                            disabled={loading || !otp.trim()}
                            style={styles.button}
                        >
                            <ButtonContent
                                loading={loading}
                                loadingText="Verifying..."
                                defaultText="Verify OTP"
                            />
                        </button>

                        <button
                            type="button"
                            onClick={() => {
                                setStep("email");
                                setOtp("");
                                resetFeedback();
                                setSessionNotice("");
                            }}
                            disabled={loading}
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

function Banner({ text, style, onDismiss }) {
    return (
        <div style={style}>
            <span>{text}</span>
            <button type="button" onClick={onDismiss} style={styles.bannerClose}>
                ×
            </button>
        </div>
    );
}

function ButtonContent({ loading, loadingText, defaultText }) {
    if (!loading) {
        return <span>{defaultText}</span>;
    }

    return (
        <span style={styles.buttonContent}>
            <span style={styles.buttonSpinner} />
            <span>{loadingText}</span>
        </span>
    );
}

function AuthLoadingOverlay({ text }) {
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

function LoadingAnimations() {
    return (
        <style>
            {`
        @keyframes aiqa-spin {
          to { transform: rotate(360deg); }
        }

        @keyframes aiqa-pulse {
          0%, 100% {
            transform: scale(0.92);
            opacity: 0.85;
          }
          50% {
            transform: scale(1.08);
            opacity: 1;
          }
        }

        @keyframes aiqa-fade-in {
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
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0f172a",
        color: "#ffffff",
        padding: "24px",
        position: "relative",
        overflow: "hidden",
    },
    card: {
        width: "100%",
        maxWidth: "420px",
        background: "#111827",
        borderRadius: "16px",
        padding: "24px",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.35)",
        position: "relative",
        zIndex: 1,
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
    helperText: {
        margin: 0,
        fontSize: "12px",
        lineHeight: 1.5,
        color: "#9ca3af",
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
    buttonContent: {
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "10px",
    },
    buttonSpinner: {
        width: "16px",
        height: "16px",
        borderRadius: "999px",
        border: "2px solid rgba(255, 255, 255, 0.35)",
        borderTopColor: "#ffffff",
        animation: "aiqa-spin 0.75s linear infinite",
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
        padding: "10px 12px",
        borderRadius: "10px",
        background: "#064e3b",
        color: "#d1fae5",
        fontSize: "14px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
    },
    sessionNotice: {
        marginBottom: "12px",
        padding: "10px 12px",
        borderRadius: "10px",
        background: "#3b0764",
        border: "1px solid #8b5cf6",
        color: "#ede9fe",
        fontSize: "14px",
        fontWeight: "600",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
    },
    error: {
        marginBottom: "12px",
        padding: "10px 12px",
        borderRadius: "10px",
        background: "#7f1d1d",
        color: "#fee2e2",
        fontSize: "14px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
    },
    bannerClose: {
        border: "none",
        background: "transparent",
        color: "inherit",
        cursor: "pointer",
        fontSize: "18px",
        lineHeight: 1,
        padding: 0,
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
        zIndex: 20,
        animation: "aiqa-fade-in 0.22s ease-out",
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
        animation: "aiqa-spin 1.1s linear infinite",
    },
    loaderInner: {
        position: "absolute",
        width: "46px",
        height: "46px",
        borderRadius: "50%",
        border: "4px solid rgba(168, 85, 247, 0.18)",
        borderBottomColor: "#a855f7",
        animation: "aiqa-spin 0.85s linear infinite reverse",
    },
    loaderCore: {
        width: "12px",
        height: "12px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #60a5fa, #a855f7)",
        boxShadow: "0 0 18px rgba(96, 165, 250, 0.6)",
        animation: "aiqa-pulse 1.2s ease-in-out infinite",
    },
    overlayText: {
        fontSize: "14px",
        fontWeight: "600",
        color: "#e5e7eb",
        letterSpacing: "0.01em",
        textAlign: "center",
    },
};
