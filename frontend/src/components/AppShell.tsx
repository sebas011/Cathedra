import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BackupIcon, DashboardIcon, ExpenseIcon, FsdpIcon, LogoutIcon, MenuIcon, ReviewIcon, UserIcon, WorkloadIcon } from "./Icons";
import { useState } from "react";
import { clearSession, getCurrentUser, signOut } from "../api";

const navigation = [
  { to: "/", label: "Dashboard", icon: DashboardIcon },
  { to: "/fsdp", label: "FSDP", icon: FsdpIcon },
  { to: "/fsdp/grant-review", label: "Grant Review", icon: ReviewIcon },
  { to: "/faculty-profiles", label: "Faculty Profile", icon: WorkloadIcon },
  { to: "/workload", label: "Faculty Workload", icon: WorkloadIcon },
  { to: "/backup-export", label: "Backup & Export", icon: BackupIcon },
  { to: "/account-security", label: "Account Security", icon: UserIcon },
  { to: "/activity", label: "Activity History", icon: ReviewIcon, adminOnly: true },
];

export default function AppShell() {
  const [open, setOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const user = getCurrentUser();
  const logout = async () => {
    try { await signOut(); } catch { /* Clear the local session even if the service is unavailable. */ }
    clearSession();
    navigate("/login");
  };
  return (
    <div className={`app-layout ${collapsed ? "sidebar-collapsed" : ""}`}>
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand">
          <button className="sidebar-collapse-toggle" onClick={() => setCollapsed((value) => !value)} aria-label="Toggle sidebar"><MenuIcon /></button>
          <div className="brand-mark">SD</div>
          <div className="brand-copy"><strong>Cathedra</strong><span>Administrator Panel</span></div>
        </div>
        <div className="nav-caption">OVERVIEW</div>
        <nav className="nav-list">
          {navigation.filter((item) => !item.adminOnly || user?.role === "admin").map(({ to, label, icon: NavIcon }) => (
            <NavLink key={to} to={to} end={to === "/"} onClick={() => setOpen(false)} className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}>
              <NavIcon className="nav-icon"/><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot"><span>Cathedra R1</span><small>Incremental rebuild</small></div>
      </aside>
      {open && <button className="sidebar-scrim" aria-label="Close menu" onClick={() => setOpen(false)} />}
      <div className="workspace">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setOpen(true)} aria-label="Open menu"><MenuIcon /></button>
          <div className="topbar-title" />
          <div className="account-box">
            <button className="logout-button no-print" onClick={() => window.print()}><span>Print This Page</span></button>
            <div className="avatar">{user?.username.slice(0, 1).toUpperCase() || "A"}</div>
            <div className="account-copy"><strong>{user?.username || "Administrator"}</strong><span>{user?.role === "admin" ? "Administrator" : "Staff"}</span></div>
            <button className="logout-button" onClick={() => void logout()}><LogoutIcon /> <span>Logout</span></button>
          </div>
        </header>
        <main className="page"><Outlet /></main>
      </div>
    </div>
  );
}
