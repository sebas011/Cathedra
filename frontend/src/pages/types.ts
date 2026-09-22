export type FsdpStatus = "On Going" | "Graduated" | "Payback" | "Withdrawn";
export interface Program { id: number; name: string; delivering_hei: string | null; description: string | null; }
export interface ProgramPayload { name: string; delivering_hei: string; description: string; }
export interface ParticipationInput { program_name: string; application_date: string | null; start_date: string | null; end_date: string | null; status: FsdpStatus; extension: string; remarks: string; }
export interface Scholar { id: number; name: string; age: number | null; previous_degree: string | null; missing_requirements: boolean; department: string | null; rank: string | null; personnel_type: "Faculty" | "Staff"; tenure: string | null; participations: (ParticipationInput & { id: number; program_id: number; name: string; program_type: string | null; delivering_hei: string | null; description: string | null })[]; created_at: string; updated_at: string; }
export interface ScholarPayload { name: string; age: number | null; previous_degree: string; missing_requirements: boolean; department: string; rank: string; tenure: string; participations: ParticipationInput[]; }
export interface FsdpSummary { total: number; ongoing: number; graduated: number; payback: number; withdrawn: number; missing_requirements: number; }
