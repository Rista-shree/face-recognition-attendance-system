import { useState, useEffect } from "react";
import { employeeApi } from "../services/employeeApi";
import EmployeeCard from "../components/EmployeeCard";

const EMPTY = { employee_id: "", name: "", department: "", email: "" };

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try { setEmployees(await employeeApi.getAll()); }
    catch { setError("Failed to load employees."); }
    finally { setLoading(false); }
  }

  async function handleSave() {
    setSaving(true); setError("");
    try {
      if (form._editing) {
        await employeeApi.update(form.employee_id, {
          name: form.name, department: form.department, email: form.email,
        });
      } else {
        await employeeApi.create(form);
      }
      setForm(null);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm(`Delete employee ${id}? This cannot be undone.`)) return;
    try { await employeeApi.remove(id); load(); }
    catch { setError("Delete failed."); }
  }

  const filtered = employees.filter((e) =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.employee_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Employees</h2>
          <p style={{ color: "var(--muted)", marginTop: 2 }}>{employees.length} registered</p>
        </div>
        <button
          onClick={() => setForm({ ...EMPTY })}
          style={{ background: "var(--primary)", color: "#fff", fontWeight: 600 }}
        >
          + Add Employee
        </button>
      </div>

      <input
        value={search} onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by name or ID…" style={{ maxWidth: 320 }}
      />

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading…</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}>
          {filtered.map((emp) => (
            <EmployeeCard
              key={emp.employee_id} employee={emp}
              onEdit={(e) => setForm({ ...e, _editing: true })}
              onDelete={handleDelete}
            />
          ))}
          {!filtered.length && <p style={{ color: "var(--muted)" }}>No employees found.</p>}
        </div>
      )}

      {/* Modal */}
      {form && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,.6)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
        }}>
          <div style={{
            background: "var(--surface)", border: "1px solid var(--border)",
            borderRadius: "var(--radius)", padding: "28px", width: 380,
            boxShadow: "var(--shadow)",
          }}>
            <h3 style={{ marginBottom: 20 }}>{form._editing ? "Edit Employee" : "Add Employee"}</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {["employee_id", "name", "department", "email"].map((field) => (
                <div key={field}>
                  <label style={{ display: "block", marginBottom: 4, fontSize: 12, color: "var(--muted)", textTransform: "capitalize" }}>
                    {field.replace("_", " ")}
                  </label>
                  <input
                    value={form[field] || ""}
                    disabled={field === "employee_id" && form._editing}
                    onChange={(e) => setForm((f) => ({ ...f, [field]: e.target.value }))}
                  />
                </div>
              ))}
            </div>
            {error && <p style={{ color: "var(--danger)", marginTop: 10, fontSize: 13 }}>{error}</p>}
            <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
              <button
                onClick={handleSave} disabled={saving}
                style={{ flex: 1, background: "var(--primary)", color: "#fff", fontWeight: 600 }}
              >
                {saving ? "Saving…" : "Save"}
              </button>
              <button
                onClick={() => { setForm(null); setError(""); }}
                style={{ flex: 1, background: "transparent", border: "1px solid var(--border)", color: "var(--text)" }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}