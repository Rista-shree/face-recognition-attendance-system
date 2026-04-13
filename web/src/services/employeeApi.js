import api from "./api";

export const employeeApi = {
  getAll: () => api.get("/api/employees/").then((r) => r.data),
  getOne: (id) => api.get(`/api/employees/${id}`).then((r) => r.data),
  create: (payload) => api.post("/api/employees/", payload).then((r) => r.data),
  update: (id, payload) => api.patch(`/api/employees/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/api/employees/${id}`),
};