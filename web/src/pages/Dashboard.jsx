import { useEffect } from "react";
import { useAttendanceStore } from "../store/attendanceStore";
import AttendanceTable from "../components/AttendanceTable";
import DailyChart from "../components/charts/DailyChart";
import MonthlyChart from "../components/charts/MonthlyChart";

function StatCard({ label, value, color = "var(--primary)" }) {
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "var(--radius)", padding: "20px 24px", flex: 1,
    }}>
      <div style={{ color: "var(--muted)", fontSize: 12, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color }}>{value ?? "—"}</div>
    </div>
  );
}

export default function Dashboard() {
  const { todaySummary, monthlyData, loading, fetchToday, fetchMonthly } = useAttendanceStore();

  useEffect(() => {
    fetchToday();
    const now = new Date();
    fetchMonthly(now.getFullYear(), now.getMonth() + 1);
  }, []);

  const records = todaySummary?.records ?? [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Live Dashboard</h2>
        <p style={{ color: "var(--muted)", marginTop: 2 }}>Today's attendance overview</p>
      </div>

      <div style={{ display: "flex", gap: 16 }}>
        <StatCard label="Present Today" value={todaySummary?.total_present} color="var(--success)" />
        <StatCard label="Total Check-ins" value={records.length} />
        <StatCard label="Date" value={todaySummary?.date ?? new Date().toLocaleDateString()} color="var(--muted)" />
      </div>

      <div style={{ display: "flex", gap: 16 }}>
        <div style={{
          flex: 1, background: "var(--surface)",
          border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 20,
        }}>
          <h3 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600 }}>Check-ins by Hour</h3>
          <DailyChart records={records} />
        </div>
        <div style={{
          flex: 1, background: "var(--surface)",
          border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 20,
        }}>
          <h3 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600 }}>Monthly Attendance</h3>
          <MonthlyChart data={monthlyData} />
        </div>
      </div>

      <div style={{
        background: "var(--surface)", border: "1px solid var(--border)",
        borderRadius: "var(--radius)", padding: 20,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600 }}>Today's Records</h3>
          <button
            onClick={fetchToday}
            style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text)", padding: "5px 14px" }}
          >
            ↻ Refresh
          </button>
        </div>
        <AttendanceTable records={records} loading={loading} />
      </div>
    </div>
  );
}