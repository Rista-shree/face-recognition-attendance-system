import api from "./api";

export const attendanceApi = {
  getToday: () => api.get("/api/attendance/today").then((r) => r.data),
  getByDate: (date) => api.get(`/api/attendance/date/${date}`).then((r) => r.data),
  getByEmployee: (id, limit = 100) => api.get(`/api/attendance/employee/${id}?limit=${limit}`).then((r) => r.data),
  getMonthly: (year, month) => api.get(`/api/attendance/monthly/${year}/${month}`).then((r) => r.data),
};