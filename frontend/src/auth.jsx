import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("phishguard_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("phishguard_token"))
      .finally(() => setLoading(false));
  }, []);

  function saveSession(data) {
    localStorage.setItem("phishguard_token", data.access_token);
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem("phishguard_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, saveSession, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
