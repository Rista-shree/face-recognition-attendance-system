import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // ✅ FIX: send as form-data instead of JSON
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const resp = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await resp.json();

      if (!resp.ok) {
        // ✅ FIX: handle both string and array errors
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail.map((e) => e.msg).join(", "));
        } else {
          throw new Error(data.detail || "Login failed");
        }
      }

      // ✅ Save tokens
      const stored = {
        state: {
          token: data.access_token,
          refreshToken: data.refresh_token,
          user: null,
        },
        version: 0,
      };
      localStorage.setItem("auth-storage", JSON.stringify(stored));

      // ✅ Fetch user profile
      const meResp = await fetch("http://127.0.0.1:8000/api/auth/me", {
        headers: {
          Authorization: "Bearer " + data.access_token,
        },
      });

      if (meResp.ok) {
        const user = await meResp.json();
        stored.state.user = user;
        localStorage.setItem("auth-storage", JSON.stringify(stored));
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("refreshtoken", data.refresh_token);
      }

      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#0f1117",
      }}
    >
      <div
        style={{
          width: 360,
          background: "#1a1d27",
          border: "1px solid #2a2d3e",
          borderRadius: 10,
          padding: "36px 32px",
          boxShadow: "0 4px 24px rgba(0,0,0,.35)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>🎭</div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#e2e8f0", margin: 0 }}>
            FaceAttend
          </h1>
          <p style={{ color: "#64748b", fontSize: 13, marginTop: 6 }}>
            Sign in to your dashboard
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: 14 }}
        >
          <div>
            <label style={{ display: "block", marginBottom: 6, fontSize: 13, color: "#64748b" }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              autoFocus
              required
              placeholder="admin"
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: "100%",
                background: "#0f1117",
                border: "1px solid #2a2d3e",
                borderRadius: 8,
                color: "#e2e8f0",
                fontSize: 14,
                padding: "9px 12px",
                outline: "none",
                boxSizing: "border-box",
                fontFamily: "inherit",
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: 6, fontSize: 13, color: "#64748b" }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              required
              placeholder="••••••••"
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                background: "#0f1117",
                border: "1px solid #2a2d3e",
                borderRadius: 8,
                color: "#e2e8f0",
                fontSize: 14,
                padding: "9px 12px",
                outline: "none",
                boxSizing: "border-box",
                fontFamily: "inherit",
              }}
            />
          </div>

          {error && (
            <div
              style={{
                background: "rgba(248,113,113,.12)",
                border: "1px solid #f87171",
                color: "#f87171",
                borderRadius: 8,
                padding: "10px 14px",
                fontSize: 13,
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading ? "#2a3a6e" : "#4f8ef7",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "10px 0",
              fontWeight: 600,
              fontSize: 14,
              cursor: loading ? "not-allowed" : "pointer",
              marginTop: 4,
              fontFamily: "inherit",
            }}
          >
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: 18, color: "#64748b", fontSize: 12 }}>
          Default: admin / admin123
        </p>
      </div>
    </div>
  );
}