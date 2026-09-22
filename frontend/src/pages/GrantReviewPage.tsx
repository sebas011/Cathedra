import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getGrantReviews, standardizeGrant } from "../api";
import type { GrantReview, GrantType } from "../types";

const grantTypes: GrantType[] = ["Full Scholarship", "Partial Scholarship", "Dissertation Aid", "Others"];

const formatDate = (value: string | null) => value
  ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value))
  : "Not reviewed";

export default function GrantReviewPage() {
  const [items, setItems] = useState<GrantReview[]>([]);
  const [view, setView] = useState<"pending" | "all">("pending");
  const [choices, setChoices] = useState<Record<number, GrantType>>({});
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [saving, setSaving] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    try {
      setError("");
      setItems(await getGrantReviews(view));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load legacy grant reviews.");
    }
  };

  useEffect(() => { void load(); }, [view]);

  const applyDecision = async (item: GrantReview) => {
    const grantType = choices[item.participation_id] || item.current_grant_type || "Others";
    setSaving(item.participation_id);
    setNotice("");
    try {
      await standardizeGrant(item.participation_id, grantType, notes[item.participation_id] || "");
      setNotice(`${item.scholar_name}’s grant was standardized. The original label remains preserved.`);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to save the grant decision.");
    } finally {
      setSaving(null);
    }
  };

  const pendingCount = items.filter((item) => !item.standardized_at).length;
  const reviewedCount = items.filter((item) => item.standardized_at).length;

  return (
    <div className="stack-md grant-review-page">
      <section className="hero-card compact">
        <div><span className="eyebrow">FSDP DATA STANDARDIZATION</span><h1>Legacy Grant Review</h1><p>Map preserved ScholarDesk grant labels to Cathedra’s standard categories without losing the source label.</p></div>
        <Link className="btn secondary" to="/fsdp">Back to FSDP</Link>
      </section>

      {error && <div className="notice error">{error}</div>}
      {notice && <div className="notice success">{notice}</div>}

      <section className="review-guidance"><div><span className="eyebrow">SOURCE DATA IS PRESERVED</span><h2>Every decision keeps the original text.</h2><p>The value shown as <strong>Original ScholarDesk label</strong> stays in Other Grant, while the selected category becomes the standardized grant type.</p></div><div className="review-guidance-count"><strong>{view === "pending" ? pendingCount : reviewedCount}</strong><span>{view === "pending" ? "records awaiting review" : "reviewed records shown"}</span></div></section>

      <section className="data-card grant-review-table-card">
        <div className="toolbar review-toolbar"><div><strong>Review queue</strong><span>Imported FSDP grants with a preserved original label</span></div><select value={view} onChange={(event) => setView(event.target.value as "pending" | "all")} aria-label="Grant review filter"><option value="pending">Pending review</option><option value="all">All legacy labels</option></select></div>
        <div className="table-meta">{items.length} {items.length === 1 ? "grant" : "grants"} shown</div>
        <div className="table-scroll"><table><thead><tr><th>Scholar & program</th><th>Original ScholarDesk label</th><th>Current standard</th><th>Standardize as</th><th>Review note</th><th>Audit status</th><th className="right">Action</th></tr></thead><tbody>
          {items.length === 0 ? <tr><td colSpan={7} className="empty-table"><strong>{view === "pending" ? "No legacy grants are waiting for review." : "No imported grant labels are available."}</strong><span>{view === "pending" ? "All preserved labels have been standardized." : "Records appear here only when an imported label was kept in Other Grant."}</span></td></tr> : items.map((item) => {
            const choice = choices[item.participation_id] || item.current_grant_type || "Others";
            return <tr key={item.participation_id}>
              <td><div className="person-cell"><strong>{item.scholar_name}</strong><span>{item.program_name}{item.department ? ` · ${item.department}` : ""}</span></div></td>
              <td><span className="legacy-label">{item.original_grant_label}</span></td>
              <td><span className="standard-type">{item.current_grant_type || "Not set"}</span></td>
              <td><select className="table-select" value={choice} onChange={(event) => setChoices((current) => ({ ...current, [item.participation_id]: event.target.value as GrantType }))} disabled={saving === item.participation_id}>{grantTypes.map((grantType) => <option key={grantType}>{grantType}</option>)}</select></td>
              <td><input className="table-input" value={notes[item.participation_id] || item.standardization_note || ""} onChange={(event) => setNotes((current) => ({ ...current, [item.participation_id]: event.target.value }))} placeholder="Optional rationale" disabled={saving === item.participation_id} /></td>
              <td><div className="review-audit"><strong>{item.standardized_at ? "Standardized" : "Awaiting review"}</strong><span>{formatDate(item.standardized_at)}</span></div></td>
              <td className="right"><button className="btn primary" type="button" disabled={saving === item.participation_id} onClick={() => void applyDecision(item)}>{saving === item.participation_id ? "Saving…" : "Apply"}</button></td>
            </tr>;
          })}
        </tbody></table></div>
      </section>
    </div>
  );
}
