import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

const linkClass = ({ isActive }) =>
  `rounded-md px-3 py-2 text-sm transition ${isActive ? "bg-brand-500/20 text-brand-400" : "text-slate-300 hover:text-white"}`;

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-white/10 bg-navy-900/60 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <Link to={user ? "/dashboard" : "/"} className="text-lg font-bold text-brand-400">PhishGuard</Link>
          {user && (
            <nav className="flex flex-wrap items-center gap-1">
              <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
              <NavLink to="/scan" className={linkClass}>Scan</NavLink>
              <NavLink to="/history" className={linkClass}>History</NavLink>
              <NavLink to="/profile" className={linkClass}>Profile</NavLink>
              {user.role === "admin" && <NavLink to="/admin" className={linkClass}>Admin</NavLink>}
              <span className="mx-2 hidden text-xs text-slate-400 md:inline">{user.email}</span>
              <button onClick={handleLogout} className="btn-ghost ml-1 px-3 py-1.5 text-sm">Log out</button>
            </nav>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      <footer className="px-4 pb-8 text-center text-xs text-slate-500">
        Automated URL detection cannot guarantee that a website is safe.
      </footer>
    </div>
  );
}
