import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";

export default function DailyChart({ records = [] }) {
  const hours = Array.from({ length: 24 }, (_, h) => ({
    hour: `${String(h).padStart(2, "0")}:00`,
    count: 0,
  }));
  records.forEach((r) => {
    const h = new Date(r.timestamp).getHours();
    hours[h].count += 1;
  });
  const data = hours.filter((h) => h.count > 0);

  if (!data.length) {
    return (
      <p style={{ color: "var(--muted)", textAlign: "center", padding: "40px 0" }}>
        No check-ins today yet.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <XAxis dataKey="hour" tick={{ fill: "var(--muted)", fontSize: 11 }} />
        <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 8,
          }}
          labelStyle={{ color: "var(--text)" }}
          cursor={{ fill: "rgba(255,255,255,.05)" }}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill="var(--primary)" />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}