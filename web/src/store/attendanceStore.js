import { create } from "zustand";
import { attendanceApi } from "../services/attendanceApi";

export const useAttendanceStore = create((set) => ({
  todaySummary: null,
  monthlyData: [],
  loading: false,
  error: null,

  fetchToday: async () => {
    set({ loading: true, error: null });
    try {
      const data = await attendanceApi.getToday();
      set({ todaySummary: data, loading: false });
    } catch (e) {
      set({ error: e.message, loading: false });
    }
  },

  fetchMonthly: async (year, month) => {
    set({ loading: true, error: null });
    try {
      const data = await attendanceApi.getMonthly(year, month);
      set({ monthlyData: data, loading: false });
    } catch (e) {
      set({ error: e.message, loading: false });
    }
  },

  clear: () => set({ todaySummary: null, monthlyData: [] }),
}));