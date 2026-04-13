import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

const NAV = [
  { to: "/dashboard", label: "📊  Dashboard" },
  { to: "/employees", label: "👤  Employees" },
  { to: "/reports", label: "📋  Reports" },
  { to: "/settings", label: "⚙️  Settings" },
];

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>

      {/* Sidebar */}
      <aside style={{
        width: 220, flexShrink: 0,
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column",
        padding: "24px 0",
      }}>
        <div style={{ padding: "0 20px 24px", fontSize: 16, fontWeight: 700, color: "var(--primary)" }}>
          🎭 FaceAttend
        </div>

        <nav style={{ flex: 1 }}>
          {NAV.map(({ to, label }) => (
            <NavLink key={to} to={to} style={({ isActive }) => ({
              display: "block", padding: "10px 20px",
              color: isActive ? "var(--primary)" : "var(--text)",
              background: isActive ? "rgba(79,142,247,.12)" : "transparent",
              borderLeft: isActive ? "3px solid var(--primary)" : "3px solid transparent",
              fontWeight: isActive ? 600 : 400,
              textDecoration: "none",
              transition: "all .15s",
            })}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: "16px 20px", borderTop: "1px solid var(--border)" }}>
          <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>Logged in as</div>
          <div style={{ fontWeight: 600, marginBottom: 10 }}>{user?.username ?? "—"}</div>
          <button
            onClick={handleLogout}
            style={{ background: "var(--danger)", color: "#fff", width: "100%", padding: "7px 0" }}
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflow: "auto", padding: "28px 32px" }}>
        <Outlet />
      </main>
    </div>
  );
}