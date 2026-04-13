import api from "../services/api";

export async function downloadCSV(start, end) {
  const resp = await api.get("/api/reports/export/csv", {
    params: { start, end },
    responseType: "blob",
  });
  const url = URL.createObjectURL(new Blob([resp.data], { type: "text/csv" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `attendance_${start}_to_${end}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}