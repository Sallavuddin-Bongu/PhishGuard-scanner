import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { useAuth } from "./auth.jsx";
import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Verify from "./pages/Verify.jsx";
import ForgotPassword from "./pages/ForgotPassword.jsx";
import ResetPassword from "./pages/ResetPassword.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Scan from "./pages/Scan.jsx";
import History from "./pages/History.jsx";
import ScanDetail from "./pages/ScanDetail.jsx";
import Profile from "./pages/Profile.jsx";
import Admin from "./pages/Admin.jsx";

function Protected({ children }) {
  return (
    <ProtectedRoute>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}

function AdminOnly({ children }) {
  const { user } = useAuth();
  if (user?.role !== "admin") return <Protected><p className="text-slate-400">Admin access required.</p></Protected>;
  return <Protected>{children}</Protected>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout><Landing /></Layout>} />
      <Route path="/login" element={<Layout><Login /></Layout>} />
      <Route path="/register" element={<Layout><Register /></Layout>} />
      <Route path="/verify" element={<Layout><Verify /></Layout>} />
      <Route path="/forgot-password" element={<Layout><ForgotPassword /></Layout>} />
      <Route path="/reset-password" element={<Layout><ResetPassword /></Layout>} />
      <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
      <Route path="/scan" element={<Protected><Scan /></Protected>} />
      <Route path="/history" element={<Protected><History /></Protected>} />
      <Route path="/history/:id" element={<Protected><ScanDetail /></Protected>} />
      <Route path="/profile" element={<Protected><Profile /></Protected>} />
      <Route path="/admin" element={<AdminOnly><Admin /></AdminOnly>} />
      <Route path="*" element={<Layout><p className="text-slate-400">Page not found. <a className="text-brand-400" href="/">Go home</a></p></Layout>} />
    </Routes>
  );
}
