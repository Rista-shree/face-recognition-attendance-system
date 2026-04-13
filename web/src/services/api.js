import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 15000,
});

// Attach JWT to every request
api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem("auth-storage");
    if (raw) {
      const parsed = JSON.parse(raw);
      const token = parsed?.state?.token;
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (_) { }
  return config;
});

// Auto-refresh on 401
let refreshing = false;
let queue = [];

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      if (refreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject });
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return api(original);
        });
      }
      refreshing = true;
      try {
        const raw = localStorage.getItem("auth-storage");
        const { state } = JSON.parse(raw || "{}");
        if (!state?.refreshToken) throw new Error("No refresh token");
        const { data } = await axios.post("/api/auth/refresh", {
          refresh_token: state.refreshToken,
        });
        const stored = JSON.parse(localStorage.getItem("auth-storage") || "{}");
        stored.state = { ...stored.state, token: data.access_token, refreshToken: data.refresh_token };
        localStorage.setItem("auth-storage", JSON.stringify(stored));
        queue.forEach((p) => p.resolve(data.access_token));
        queue = [];
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        queue.forEach((p) => p.reject(err));
        queue = [];
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
      } finally {
        refreshing = false;
      }
    }
    return Promise.reject(err);
  }
);

export default api;