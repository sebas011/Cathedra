import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { deleteWorkload, getWorkloads } from "../api";
import type { FacultyWorkload } from "../types";

const terms = ["First Semester", "Second Semester", "Summer"];
const hours = (value: number) => `${value.toFixed(1)} h`;
const isImported = (dataSource?: string) => dataSource === "Imported from ScholarDesk";

function SourceBadge({ dataSource }: { dataSource?: string }) {
  return isImported(dataSource)
    ? <span className="source-badge imported">Imported from ScholarDesk</span>
    : <span className="source-badge">Cathedra</span>;
}

export default function WorkloadPage() {
  const [records, setRecords] = useState<FacultyWorkload[]>([]);
  const [search, setSearch] = useState("");
  const [academicYear, setAcademicYear] = useState("");
  const [term, setTerm] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setError("");
      setRecords(await getWorkloads(search, academicYear, term));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to load workloads.");
    }
  };

  useEffect(() => { void load(); }, [search, academicYear, term]);

  const removeRecord = async (record: FacultyWorkload) => {
    if (!confirm(`Delete the workload for ${record.faculty_name}?`)) return;
    try {
      setError("");
      await deleteWorkload(record.id);
      await load();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to delete workload.");
    }
  };

  const assignmentCount = records.reduce((total, record) => total + record.assignments.length, 0);
  const lectureHours = records.reduce((total, record) => total + record.total_lecture_hours, 0);
  const totalWeeklyHours = records.reduce((total, record) => total + record.total_weekly_hours, 0);

  return (
    <div className="stack-md workload-page">
      <section className="hero-card compact"><div><span className="eyebrow">FACULTY WORKLOAD</span><h1>Weekly Teaching Loads</h1><p>Review course assignments, teaching hours, and term coverage across the faculty.</p></div><Link className="btn primary" to="/workload/new">Add Workload</Link></section>
      {error && <div className="notice error">{error}</div>}
      <section className="metric-grid four" aria-label="Workload summary"><div className="metric-card"><span>Workload records</span><strong>{records.length}</strong></div><div className="metric-card"><span>Teaching assignments</span><strong>{assignmentCount}</strong></div><div className="metric-card"><span>Lecture hours / week</span><strong>{hours(lectureHours)}</strong></div><div className="metric-card"><span>Total hours / week</span><strong>{hours(totalWeeklyHours)}</strong></div></section>
      <section className="data-card workload-table-card">
        <div className="toolbar workload-toolbar"><div className="search-wrap"><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search faculty, department, rank, or term" aria-label="Search faculty workloads" /></div><input value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} placeholder="Academic year" aria-label="Filter by academic year" /><select value={term} onChange={(event) => setTerm(event.target.value)} aria-label="Filter by term"><option value="">All terms</option>{terms.map((item) => <option key={item} value={item}>{item}</option>)}</select><button className="btn secondary" type="button" onClick={() => { setSearch(""); setAcademicYear(""); setTerm(""); }}>Reset</button></div>
        <div className="table-meta">{records.length} {records.length === 1 ? "workload" : "workloads"} shown</div>
        <div className="table-scroll"><table><thead><tr><th>Faculty member</th><th>Period</th><th>Courses</th><th>Lecture / week</th><th>Laboratory / week</th><th>Total / week</th><th>Source</th><th className="right">Actions</th></tr></thead><tbody>
          {records.length === 0 ? <tr><td colSpan={8} className="empty-table"><strong>No workload records found.</strong><span>{search || academicYear || term ? "Try changing or clearing the filters." : "Add a weekly teaching workload to get started."}</span></td></tr> : records.map((record) => <tr key={record.id}>
            <td><div className="person-cell"><strong>{record.faculty_name}</strong><span>{record.rank || "Faculty"}{record.department ? ` · ${record.department}` : ""}</span></div></td>
            <td><div className="person-cell"><strong>{record.academic_year}</strong><span>{record.term}</span></div></td>
            <td>{record.assignments.length}</td><td>{hours(record.total_lecture_hours)}</td><td>{hours(record.total_laboratory_hours)}</td><td><strong>{hours(record.total_weekly_hours)}</strong></td>
            <td><SourceBadge dataSource={record.data_source} /></td>
            <td className="right"><div className="action-group"><Link className="btn secondary" to={`/workload/${record.id}/edit`}>Edit</Link><button className="btn secondary" type="button" onClick={() => void removeRecord(record)}>Delete</button></div></td>
          </tr>)}
        </tbody></table></div>
      </section>
    </div>
  );
}
