import { useState } from "react";
import api from "../services/api";

export default function Settings() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("staff");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCreateUser(e) {
    e.preventDefault();
    setMsg(""); setError(""); setLoading(true);
    try {
      await api.post("/api/auth/register", { username, email, password, role });
      setMsg(`User "${username}" created successfully.`);
      setUsername(""); setEmail(""); setPassword("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create user.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 540 }}>
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Settings</h2>
        <p style={{ color: "var(--muted)", marginTop: 2 }}>Manage dashboard users</p>
      </div>

      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius)", padding: "24px",
      }}>
        <h3 style={{ marginBottom: 18, fontSize: 15 }}>Create Dashboard User</h3>
        <form onSubmit={handleCreateUser} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            { label: "Username", val: username, set: setUsername, type: "text" },
            { label: "Email", val: email, set: setEmail, type: "email" },
            { label: "Password", val: password, set: setPassword, type: "password" },
          ].map(({ label, val, set, type }) => (
            <div key={label}>
              <label style={{ display: "block", marginBottom: 5, fontSize: 12, color: "var(--muted)" }}>{label}</label>
              <input type={type} value={val} required onChange={(e) => set(e.target.value)} />
            </div>
          ))}
          <div>
            <label style={{ display: "block", marginBottom: 5, fontSize: 12, color: "var(--muted)" }}>Role</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          {msg && <p style={{ color: "var(--success)", fontSize: 13 }}>{msg}</p>}
          {error && <p style={{ color: "var(--danger)", fontSize: 13 }}>{error}</p>}
          <button
            type="submit" disabled={loading}
            style={{ background: "var(--primary)", color: "#fff", fontWeight: 600, marginTop: 4 }}
          >
            {loading ? "Creating…" : "Create User"}
          </button>
        </form>
      </div>

      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius)", padding: "20px",
      }}>
        <h3 style={{ marginBottom: 12, fontSize: 15 }}>API Info</h3>
        <p style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.8 }}>
          Backend docs available at{" "}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">localhost:8000/docs</a>
          <br />
          ReDoc at{" "}
          <a href="http://localhost:8000/redoc" target="_blank" rel="noreferrer">localhost:8000/redoc</a>
        </p>
      </div>
    </div>
  );
}