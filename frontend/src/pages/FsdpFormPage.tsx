import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { createFsdpRecord, getFsdpRecord, updateFsdpRecord } from "../api";
import type { ParticipationInput, ScholarPayload } from "../types";

const statuses = ["On Going", "Graduated", "Payback", "Withdrawn"] as const;
const grantTypes = ["Full Scholarship", "Partial Scholarship", "Dissertation Aid", "Others"] as const;
const newGrant = (): ParticipationInput => ({ program_name: "", delivering_hei: "", start_date: null, end_date: null, start_term: "", start_academic_year: "", end_term: "", end_academic_year: "", grant_type: null, grant_other: "", status: "On Going", extension: "", remarks: "" });
const emptyScholar = (): ScholarPayload => ({ name: "", age: null, previous_degree: "", missing_requirements: false, department: "", rank: "", tenure: "", participations: [] });

export default function FsdpFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState<ScholarPayload>(emptyScholar);
  const [draft, setDraft] = useState<ParticipationInput>(newGrant);
  const [editingGrant, setEditingGrant] = useState<number | null>(null);
  const [grantEditorOpen, setGrantEditorOpen] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getFsdpRecord(Number(id)).then((scholar) => setForm({ name: scholar.name, age: scholar.age, previous_degree: scholar.previous_degree || "", missing_requirements: scholar.missing_requirements, department: scholar.department || "", rank: scholar.rank || "", tenure: scholar.tenure || "", participations: scholar.participations.map(({ name, delivering_hei, start_date, end_date, start_term, start_academic_year, end_term, end_academic_year, grant_type, grant_other, status, extension, remarks }) => ({ program_name: name, delivering_hei: delivering_hei || "", start_date, end_date, start_term: start_term || "", start_academic_year: start_academic_year || "", end_term: end_term || "", end_academic_year: end_academic_year || "", grant_type, grant_other: grant_other || "", status, extension: extension || "", remarks: remarks || "" })) })).catch((caughtError) => setError(caughtError.message));
  }, [id]);

  const updateDraft = (changes: Partial<ParticipationInput>) => setDraft((current) => ({ ...current, ...changes }));
  const openNewGrant = () => { setDraft(newGrant()); setEditingGrant(null); setGrantEditorOpen(true); setError(""); };
  const openEditGrant = (index: number) => { setDraft({ ...form.participations[index] }); setEditingGrant(index); setGrantEditorOpen(true); setError(""); };
  const saveGrant = () => {
    if (!draft.program_name.trim()) { setError("Program Applied is required."); return; }
    if (draft.grant_type === "Others" && !draft.grant_other.trim()) { setError("Describe the other grant type."); return; }
    setForm((current) => ({ ...current, participations: editingGrant === null ? [...current.participations, draft] : current.participations.map((grant, index) => index === editingGrant ? draft : grant) }));
    setGrantEditorOpen(false); setEditingGrant(null); setDraft(newGrant()); setError("");
  };
  const saveScholar = async (event: FormEvent) => {
    event.preventDefault();
    try { id ? await updateFsdpRecord(Number(id), form) : await createFsdpRecord(form); navigate("/fsdp"); }
    catch (caughtError) { setError(caughtError instanceof Error ? caughtError.message : "Unable to save scholar."); }
  };

  return <form onSubmit={saveScholar} className="stack-md form-page">
    <section className="hero-card compact"><div><span className="eyebrow">FSDP SCHOLAR</span><h1>{id ? "Edit Scholar" : "New Scholar"}</h1></div><Link className="btn secondary" to="/fsdp">Back</Link></section>
    {error && <div className="notice error">{error}</div>}
    <section className="form-card"><div className="form-card-head"><span>01</span><div><h2>Scholar Information</h2></div></div><div className="form-grid three"><label className="span-2">Name *<input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label><label>Age<input type="number" value={form.age ?? ""} onChange={(event) => setForm({ ...form, age: event.target.value ? Number(event.target.value) : null })} /></label><label>Academic Rank<input value={form.rank} onChange={(event) => setForm({ ...form, rank: event.target.value })} /></label><label>Department<input value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} /></label><label>Tenure at CHMSC<input value={form.tenure} onChange={(event) => setForm({ ...form, tenure: event.target.value })} /></label><label className="span-2">Previous Degree<input value={form.previous_degree} onChange={(event) => setForm({ ...form, previous_degree: event.target.value })} /></label><label className="check-label"><input type="checkbox" checked={form.missing_requirements} onChange={(event) => setForm({ ...form, missing_requirements: event.target.checked })} /><span><strong>Missing Requirements</strong><small>Mark for follow-up.</small></span></label></div></section>
    <section className="form-card"><div className="form-card-head"><span>02</span><div><h2>FSDP Grants</h2><p>Each added grant appears below and is saved with this scholar.</p></div></div>
      <div className="table-scroll"><table><thead><tr><th>Program Applied</th><th>Delivering HEI</th><th>Grant Type</th><th>Status</th><th>Term Coverage</th><th className="right">Actions</th></tr></thead><tbody>{form.participations.length === 0 ? <tr><td colSpan={6} className="empty-table"><strong>No grants added yet.</strong><span>Select Add Grant to enter the first record.</span></td></tr> : form.participations.map((grant, index) => <tr key={`${grant.program_name}-${index}`}><td>{grant.program_name}</td><td>{grant.delivering_hei || "—"}</td><td>{grant.grant_type === "Others" ? grant.grant_other : grant.grant_type || "—"}</td><td>{grant.status}</td><td>{grant.start_term && grant.start_academic_year ? `${grant.start_term} ${grant.start_academic_year}` : grant.start_date || "—"} to {grant.end_term && grant.end_academic_year ? `${grant.end_term} ${grant.end_academic_year}` : grant.end_date || "Present"}</td><td className="right"><button type="button" className="btn secondary" onClick={() => openEditGrant(index)}>Edit</button> <button type="button" className="btn secondary" onClick={() => setForm((current) => ({ ...current, participations: current.participations.filter((_, itemIndex) => itemIndex !== index) }))}>Remove</button></td></tr>)}</tbody></table></div>
      {!grantEditorOpen && <button type="button" className="btn secondary" onClick={openNewGrant}>Add Grant</button>}
      {grantEditorOpen && <div className="relation-editor"><div className="form-grid three"><label>Program Applied *<input value={draft.program_name} onChange={(event) => updateDraft({ program_name: event.target.value })} /></label><label>Delivering HEI<input value={draft.delivering_hei} onChange={(event) => updateDraft({ delivering_hei: event.target.value })} /></label><label>Type of Grant<select value={draft.grant_type || ""} onChange={(event) => updateDraft({ grant_type: (event.target.value || null) as ParticipationInput["grant_type"] })}><option value="">Select grant</option>{grantTypes.map((item) => <option key={item}>{item}</option>)}</select></label>{draft.grant_type === "Others" && <label className="span-3">Other Grant *<input value={draft.grant_other} onChange={(event) => updateDraft({ grant_other: event.target.value })} /></label>}<label>Start Term<input value={draft.start_term} placeholder="e.g. 1st Term" onChange={(event) => updateDraft({ start_term: event.target.value })} /></label><label>Start Academic Year<input value={draft.start_academic_year} placeholder="e.g. 2024-2025" onChange={(event) => updateDraft({ start_academic_year: event.target.value })} /></label><label>End Term<input value={draft.end_term} placeholder="e.g. 2nd Term" onChange={(event) => updateDraft({ end_term: event.target.value })} /></label><label>End Academic Year<input value={draft.end_academic_year} placeholder="e.g. 2025-2026" onChange={(event) => updateDraft({ end_academic_year: event.target.value })} /></label><label>Status<select value={draft.status} onChange={(event) => updateDraft({ status: event.target.value as ParticipationInput["status"] })}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label><label>Extension<input value={draft.extension} onChange={(event) => updateDraft({ extension: event.target.value })} /></label><label className="span-2">Remarks<input value={draft.remarks} onChange={(event) => updateDraft({ remarks: event.target.value })} /></label></div><div className="form-actions"><button type="button" className="btn secondary" onClick={() => setGrantEditorOpen(false)}>Cancel</button><button type="button" className="btn primary" onClick={saveGrant}>{editingGrant === null ? "Save Grant" : "Update Grant"}</button></div></div>}
    </section>
    <div className="form-actions"><button className="btn primary">Save Scholar</button></div>
  </form>;
}
