export default function EmployeeCard({ employee, onEdit, onDelete }) {
  const { employee_id, name, department, email, is_active } = employee;

  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "var(--radius)", padding: "18px 20px",
      display: "flex", flexDirection: "column", gap: 6,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 700, fontSize: 15 }}>{name}</span>
        <span style={{
          fontSize: 11, padding: "2px 8px", borderRadius: 20,
          background: is_active ? "rgba(52,211,153,.15)" : "rgba(248,113,113,.15)",
          color: is_active ? "var(--success)" : "var(--danger)",
        }}>
          {is_active ? "Active" : "Inactive"}
        </span>
      </div>
      <div style={{ color: "var(--muted)", fontSize: 12, fontFamily: "monospace" }}>{employee_id}</div>
      {department && <div style={{ fontSize: 13 }}>🏢 {department}</div>}
      {email && <div style={{ fontSize: 13 }}>✉️  {email}</div>}
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button
          onClick={() => onEdit(employee)}
          style={{ flex: 1, background: "var(--primary)", color: "#fff", padding: "6px 0" }}
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(employee_id)}
          style={{ flex: 1, background: "transparent", border: "1px solid var(--danger)", color: "var(--danger)", padding: "6px 0" }}
        >
          Delete
        </button>
      </div>
    </div>
  );
}