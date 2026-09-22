import { FormEvent, useEffect, useState } from "react";

import { createFacultyProfile, deleteFacultyProfile, getFacultyProfiles, updateFacultyProfile } from "../api";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type { FacultyProfile, FacultyProfilePayload } from "../types";

const colleges = ["CAS", "COEd", "CBMA", "COE", "COF", "CIT", "CCS", "CCJ"] as const;

const blankProfile = (): FacultyProfilePayload => ({ name: "", rank: "", employment_status: "Full-time", salary_grade: "", college: "CAS", department: "" });
const isImported = (dataSource?: string) => dataSource === "Imported from ScholarDesk";

function SourceBadge({ dataSource }: { dataSource?: string }) {
  return isImported(dataSource)
    ? <span className="source-badge imported">Imported from ScholarDesk</span>
    : <span className="source-badge">Cathedra</span>;
}

export default function FacultyProfilesPage() {
  const [profiles, setProfiles] = useState<FacultyProfile[]>([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState<FacultyProfilePayload>(blankProfile);
  const [editing, setEditing] = useState<number | null>(null);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [error, setError] = useState("");
  const debouncedSearch = useDebouncedValue(search);

  const load = async () => {
    try {
      setError("");
      setProfiles(await getFacultyProfiles(debouncedSearch));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load faculty profiles.");
    }
  };

  useEffect(() => { void load(); }, [debouncedSearch]);

  const closeEditor = () => {
    setIsEditorOpen(false);
    setEditing(null);
    setForm(blankProfile());
  };

  const editProfile = (profile: FacultyProfile) => {
    setForm({ name: profile.name, rank: profile.rank, employment_status: profile.employment_status, salary_grade: profile.salary_grade, college: profile.college, department: profile.department });
    setEditing(profile.id);
    setIsEditorOpen(true);
  };

  const saveProfile = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setError("");
      if (editing !== null) await updateFacultyProfile(editing, form);
      else await createFacultyProfile(form);
      closeEditor();
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to save profile.");
    }
  };

  const removeProfile = async (profile: FacultyProfile) => {
    if (!confirm(`Delete ${profile.name}?`)) return;
    try {
      setError("");
      await deleteFacultyProfile(profile.id);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to delete profile.");
    }
  };

  const importedCount = profiles.filter((profile) => isImported(profile.data_source)).length;

  return (
    <div className="stack-md faculty-directory-page">
      <section className="hero-card compact">
        <div>
          <span className="eyebrow">FACULTY DIRECTORY</span>
          <h1>Faculty Profiles</h1>
          <p>Keep faculty appointments, ranks, and department assignments in one directory.</p>
        </div>
        <button className="btn primary" type="button" onClick={() => { setForm(blankProfile()); setEditing(null); setIsEditorOpen(true); }}>Add Faculty</button>
      </section>

      {error && <div className="notice error">{error}</div>}

      <section className="directory-summary" aria-label="Faculty profile summary">
        <div><span>Faculty profiles</span><strong>{profiles.length}</strong></div>
        <div><span>Full-time</span><strong>{profiles.filter((profile) => profile.employment_status === "Full-time").length}</strong></div>
        <div><span>Colleges represented</span><strong>{new Set(profiles.map((profile) => profile.college)).size}</strong></div>
        <div><span>ScholarDesk imports</span><strong>{importedCount}</strong></div>
      </section>

      {isEditorOpen && (
        <form onSubmit={saveProfile} className="form-card faculty-editor">
          <div className="form-card-head"><span>{editing !== null ? "EDIT" : "NEW"}</span><div><h2>{editing !== null ? "Edit faculty profile" : "New faculty profile"}</h2><p>Enter the faculty member’s current appointment details.</p></div></div>
          <div className="form-grid three">
            <label className="span-2">Name *<input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
            <label>Academic rank *<input required value={form.rank} onChange={(event) => setForm({ ...form, rank: event.target.value })} /></label>
            <label>Employment status<select value={form.employment_status} onChange={(event) => setForm({ ...form, employment_status: event.target.value as FacultyProfilePayload["employment_status"] })}><option>Full-time</option><option>Part-time</option></select></label>
            <label>Salary grade<input value={form.salary_grade} onChange={(event) => setForm({ ...form, salary_grade: event.target.value })} placeholder="e.g. SG 18" /></label>
            <label>College<select value={form.college} onChange={(event) => setForm({ ...form, college: event.target.value as FacultyProfilePayload["college"] })}>{colleges.map((college) => <option key={college}>{college}</option>)}</select></label>
            <label className="span-3">Department *<input required value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} placeholder="Department within the selected college" /></label>
          </div>
          <div className="form-actions"><button type="button" className="btn secondary" onClick={closeEditor}>Cancel</button><button className="btn primary">{editing !== null ? "Save Changes" : "Save Faculty"}</button></div>
        </form>
      )}

      <section className="data-card directory-table-card">
        <div className="toolbar directory-toolbar"><div className="search-wrap"><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search name, rank, college, or department" aria-label="Search faculty profiles" /></div>{search && <button className="btn secondary" type="button" onClick={() => setSearch("")}>Clear search</button>}</div>
        <div className="table-meta">{profiles.length} {profiles.length === 1 ? "profile" : "profiles"} shown</div>
        <div className="table-scroll"><table><thead><tr><th>Faculty member</th><th>Appointment</th><th>College & department</th><th>Source</th><th className="right">Actions</th></tr></thead><tbody>
          {profiles.length === 0 ? <tr><td colSpan={5} className="empty-table"><strong>No faculty profiles found.</strong><span>{search ? "Try a broader search term." : "Add a faculty member to begin the directory."}</span></td></tr> : profiles.map((profile) => <tr key={profile.id}>
            <td><div className="person-cell"><strong>{profile.name}</strong><span>{profile.employment_status}</span></div></td>
            <td><div className="person-cell"><strong>{profile.rank}</strong><span>{profile.salary_grade || "No salary grade"}</span></div></td>
            <td><div className="person-cell"><strong>{profile.college}</strong><span>{profile.department}</span></div></td>
            <td><SourceBadge dataSource={profile.data_source} /></td>
            <td className="right"><div className="action-group"><button className="btn secondary" type="button" onClick={() => editProfile(profile)}>Edit</button><button className="btn secondary" type="button" onClick={() => void removeProfile(profile)}>Delete</button></div></td>
          </tr>)}
        </tbody></table></div>
      </section>
    </div>
  );
}
