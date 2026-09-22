import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { ExpenseIcon, FsdpIcon, WorkloadIcon, ArrowIcon } from "../components/Icons";
import { getFsdpSummary } from "../api";
import type { FsdpSummary } from "../types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<FsdpSummary | null>(null);
  useEffect(() => { getFsdpSummary().then(setSummary).catch(() => setSummary(null)); }, []);
  return (
    <div className="stack-lg">
      <section className="hero-card">
        <div><span className="eyebrow">ADMINISTRATOR DASHBOARD</span><h1>System Overview</h1><p>Manage Cathedra's core operational areas from one workspace.</p></div>
        <div className="live-pill"><span/> Development workspace</div>
      </section>
      <section className="metric-grid four">
        <div className="metric-card"><span>FSDP Records</span><strong>{summary?.total ?? "—"}</strong><small>Faculty and staff development records</small></div>
        <div className="metric-card"><span>On Going FSDP</span><strong className="green">{summary?.ongoing ?? "—"}</strong><small>Current development programs</small></div>
        <div className="metric-card"><span>Graduated</span><strong>{summary?.graduated ?? "—"}</strong><small>Completed development programs</small></div>
        <div className="metric-card"><span>Missing Requirements</span><strong className="amber">{summary?.missing_requirements ?? "—"}</strong><small>Records needing follow-up</small></div>
      </section>
      <section className="section-heading"><div><span className="eyebrow">CORE MODULES</span><h2>Cathedra Workspace</h2><p>Each module is built independently to keep the system focused and reliable.</p></div></section>
      <section className="module-grid">
        <Link to="/fsdp" className="module-card ready"><div className="module-icon"><FsdpIcon /></div><div className="module-state">AVAILABLE</div><h3>Faculty & Staff Development Program</h3><p>Maintain FSDP beneficiaries, grants, progress status, requirements, and remarks.</p><span className="module-link">Open FSDP <ArrowIcon /></span></Link>
        <Link to="/workload" className="module-card ready"><div className="module-icon"><WorkloadIcon /></div><div className="module-state">AVAILABLE</div><h3>Faculty Workload</h3><p>Track weekly lecture and laboratory teaching hours by course and section.</p><span className="module-link">Open Faculty Workload <ArrowIcon /></span></Link>
        <div className="module-card disabled"><div className="module-icon"><ExpenseIcon /></div><div className="module-state muted">PAUSED</div><h3>Expenses Projection</h3><p>Salary-grade projection work is preserved and will resume in a later Cathedra phase.</p><span className="module-link muted">Paused for now</span></div>
      </section>
    </div>
  );
}
