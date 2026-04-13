import { format, parseISO } from "date-fns";

export default function AttendanceTable({ records = [], loading }) {
  if (loading) return <p style={{ color: "var(--muted)" }}>Loading…</p>;
  if (!records.length) return <p style={{ color: "var(--muted)" }}>No records found.</p>;

  return (
    <div style={{ overflowX: "auto" }}>
      <table>
        <thead>
          <tr>
            <th>Employee ID</th>
            <th>Name</th>
            <th>Time</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td style={{ color: "var(--muted)", fontFamily: "monospace" }}>{r.employee_id}</td>
              <td style={{ fontWeight: 500 }}>{r.name}</td>
              <td>{format(parseISO(r.timestamp), "MMM d, yyyy  HH:mm")}</td>
              <td>
                <span style={{
                  padding: "2px 8px", borderRadius: 20, fontSize: 12,
                  background: r.confidence >= 0.8 ? "rgba(52,211,153,.15)" : "rgba(251,191,36,.15)",
                  color: r.confidence >= 0.8 ? "var(--success)" : "var(--warning)",
                }}>
                  {(r.confidence * 100).toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}