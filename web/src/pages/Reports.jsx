import { useState } from "react";
import { format } from "date-fns";
import { downloadCSV } from "../utils/exportCSV";
import { attendanceApi } from "../services/attendanceApi";
import AttendanceTable from "../components/AttendanceTable";

export default function Reports() {
  const today = format(new Date(), "yyyy-MM-dd");
  const [start, setStart] = useState(today);
  const [end, setEnd] = useState(today);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    setLoading(true); setError("");
    try {
      const data = await attendanceApi.getByDate(start);
      setRecords(data.records ?? []);
    } catch {
      setError("Failed to load records.");
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    try { await downloadCSV(start, end); }
    catch { setError("Export failed."); }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Reports</h2>
        <p style={{ color: "var(--muted)", marginTop: 2 }}>Search and export attendance records</p>
      </div>

      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius)", padding: "18px 20px",
        display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap",
      }}>
        <div>
          <label style={{ display: "block", marginBottom: 5, fontSize: 12, color: "var(--muted)" }}>Start Date</label>
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} style={{ width: 160 }} />
        </div>
        <div>
          <label style={{ display: "block", marginBottom: 5, fontSize: 12, color: "var(--muted)" }}>End Date</label>
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} style={{ width: 160 }} />
        </div>
        <button
          onClick={handleSearch}
          style={{ background: "var(--primary)", color: "#fff", fontWeight: 600, padding: "8px 20px" }}
        >
          Search
        </button>
        <button
          onClick={handleExport}
          style={{ background: "transparent", border: "1px solid var(--success)", color: "var(--success)", padding: "8px 20px" }}
        >
          ↓ Export CSV
        </button>
      </div>

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius)", padding: 20,
      }}>
        <h3 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600 }}>
          Results {records.length > 0 && `(${records.length})`}
        </h3>
        <AttendanceTable records={records} loading={loading} />
      </div>
    </div>
  );
}