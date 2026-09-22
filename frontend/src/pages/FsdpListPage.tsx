import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { deleteFsdpRecord, getFsdpRecords, getFsdpSummary } from "../api";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type { FsdpSummary, Scholar } from "../types";

const statuses = ["On Going", "Graduated", "Payback", "Withdrawn"];

export default function FsdpListPage() {
  const [items, setItems] = useState<Scholar[]>([]); const [summary, setSummary] = useState<FsdpSummary|null>(null); const [search,setSearch]=useState(""); const [status,setStatus]=useState(""); const [error,setError]=useState("");
  const debouncedSearch = useDebouncedValue(search);
  const loadRecords=async()=>{try{setItems(await getFsdpRecords(debouncedSearch,status))}catch(caught){setError(caught instanceof Error?caught.message:"Unable to load FSDP.")}};
  const loadSummary=async()=>{try{setSummary(await getFsdpSummary())}catch(caught){setError(caught instanceof Error?caught.message:"Unable to load FSDP.")}};
  const load=async()=>{await Promise.all([loadRecords(),loadSummary()])};
  useEffect(()=>{void loadRecords()},[debouncedSearch,status]);
  useEffect(()=>{void loadSummary()},[]);
  return <div className="stack-md"><section className="hero-card compact"><div><span className="eyebrow">FACULTY & STAFF DEVELOPMENT PROGRAM</span><h1>FSDP Scholars</h1><p>Manage scholar grants and development records.</p></div><Link className="btn primary" to="/fsdp/new">Add Scholar</Link></section>{error&&<div className="notice error">{error}</div>}<section className="metric-grid four">{[["Total",summary?.total],["On Going",summary?.ongoing],["Graduated",summary?.graduated],["Missing Requirements",summary?.missing_requirements]].map(([label,value])=><div className="metric-card" key={String(label)}><span>{label}</span><strong>{value??"—"}</strong></div>)}</section><section className="data-card"><div className="toolbar"><input value={search} onChange={event=>setSearch(event.target.value)} placeholder="Search scholars or programs"/><select value={status} onChange={event=>setStatus(event.target.value)}><option value="">All statuses</option>{statuses.map(item=><option key={item}>{item}</option>)}</select><button className="btn secondary" onClick={()=>{setSearch("");setStatus("")}}>Reset</button></div><div className="table-scroll"><table><thead><tr><th>Scholar</th><th>Department</th><th>Programs</th><th>Source</th><th className="right">Actions</th></tr></thead><tbody>{items.map(item=><tr key={item.id}><td><Link to={`/fsdp/${item.id}`}>{item.name}</Link></td><td>{item.department||"—"}</td><td>{item.participations.length}</td><td>{item.data_source==="Imported from ScholarDesk"?<span className="warning-chip">Imported</span>:"Cathedra"}</td><td className="right"><Link className="btn secondary" to={`/fsdp/${item.id}/edit`}>Edit</Link> <button className="btn secondary" onClick={()=>{if(confirm(`Delete ${item.name}?`))void deleteFsdpRecord(item.id).then(load)}}>Delete</button></td></tr>)}</tbody></table></div></section></div>;
}
