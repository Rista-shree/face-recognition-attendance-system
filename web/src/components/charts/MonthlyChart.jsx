import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

export default function MonthlyChart({ data = [] }) {
  if (!data.length) {
    return (
      <p style={{ color: "var(--muted)", textAlign: "center", padding: "40px 0" }}>
        No monthly data available.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="day"
          tick={{ fill: "var(--muted)", fontSize: 11 }}
          tickFormatter={(d) => d.slice(8)}
        />
        <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 8,
          }}
          labelStyle={{ color: "var(--text)" }}
        />
        <Line
          type="monotone"
          dataKey="present"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={{ fill: "var(--primary)", r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}