import { format, parseISO } from "date-fns";

export const fmt = {
  date: (iso) => format(parseISO(iso), "MMM d, yyyy"),
  time: (iso) => format(parseISO(iso), "HH:mm:ss"),
  datetime: (iso) => format(parseISO(iso), "MMM d, yyyy  HH:mm"),
  apiDate: (d) => format(d, "yyyy-MM-dd"),
};