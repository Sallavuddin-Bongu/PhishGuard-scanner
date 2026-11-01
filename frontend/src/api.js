import axios from "axios";

// The backend runs on port 8001 (see start-backend.bat). Override with VITE_API_URL if needed.
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("phishguard_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status;
    if (status === 401 && !window.location.pathname.startsWith("/login")) {
      localStorage.removeItem("phishguard_token");
      window.location.href = "/login?expired=1";
    }
    return Promise.reject(error);
  }
);

export function errorMessage(error, fallback = "Something went wrong. Please try again.") {
  if (!error.response) {
    return `Cannot reach the backend at ${API_URL}. Double-click start-backend.bat and keep its window open.`;
  }
  const detail = error.response.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return fallback;
}
