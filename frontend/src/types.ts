export type FsdpStatus = "On Going" | "Graduated" | "Payback" | "Withdrawn";
export type College = "CAS" | "COEd" | "CBMA" | "COE" | "COF" | "CIT" | "CCS" | "CCJ";

export type GrantType = "Full Scholarship"|"Partial Scholarship"|"Dissertation Aid"|"Others";
export interface ParticipationInput { program_name:string; delivering_hei:string; start_date:string|null; end_date:string|null; start_term:string; start_academic_year:string; end_term:string; end_academic_year:string; grant_type:GrantType|null; grant_other:string; status:FsdpStatus; extension:string; remarks:string; }
export interface Scholar { id:number; name:string; age:number|null; previous_degree:string|null; missing_requirements:boolean; department:string|null; rank:string|null; personnel_type:"Faculty"|"Staff"; tenure:string|null; data_source:string; participations:(ParticipationInput & {id:number;program_id:number;name:string;delivering_hei:string|null})[]; created_at:string; updated_at:string; }
export interface ScholarPayload { name:string; age:number|null; previous_degree:string; missing_requirements:boolean; department:string; rank:string; tenure:string; participations:ParticipationInput[]; }
export interface FsdpSummary { total:number; ongoing:number; graduated:number; payback:number; withdrawn:number; missing_requirements:number; }
export interface FacultyProfilePayload { name:string; rank:string; employment_status:"Full-time"|"Part-time"; salary_grade:string; college:College; department:string; }
export interface FacultyProfile extends FacultyProfilePayload { id:number; data_source?:string; created_at:string; updated_at:string; }
export interface TeachingAssignmentPayload { course_code:string; course_title:string; year_section:string; lecture_hours:number; laboratory_hours:number; }
export interface FacultyWorkloadPayload { faculty_profile_id:number; academic_year:string; term:string; remarks:string; assignments:TeachingAssignmentPayload[]; }
export interface FacultyWorkload extends FacultyWorkloadPayload { id:number; faculty_name:string; department:string|null; rank:string|null; data_source?:string; total_lecture_hours:number; total_laboratory_hours:number; total_weekly_hours:number; created_at:string; assignments:(TeachingAssignmentPayload & {id:number})[]; }
export interface BackupFile { filename:string; created_at:string; size_bytes:number; }
export interface MaintenanceStatus { database_status:"healthy"; database_file:string; database_size_bytes:number; fsdp_records:number; faculty_profiles:number; workload_records:number; backup_count:number; latest_backup_at:string|null; backup_retention:number; backups:BackupFile[]; }
export interface BackupResult { filename:string; created_at:string; size_bytes:number; }
export interface LocalUser { id:number; username:string; role:"admin"|"staff"; created_at?:string; }
export interface SessionResult { token:string; user:LocalUser; }
export interface SalaryGradeRule { id:number; salary_grade:string; monthly_salary:number; standard_weekly_hours:number; overload_hourly_rate:number; updated_at:string; }
export interface ExpenseProjectionRecord { faculty_id:number; faculty_name:string; department:string; salary_grade:string|null; weekly_hours:number; standard_weekly_hours:number|null; overload_hours:number; regular_cost:number; overload_cost:number; projected_cost:number; rule_available:boolean; }
export interface ExpenseProjection { academic_year:string; term:string; teaching_weeks:number; salary_months:number; records:ExpenseProjectionRecord[]; total_regular_cost:number; total_overload_cost:number; total_projected_cost:number; missing_rules:number; }
export interface ActivityEvent { id:number; username:string|null; action:string; area:string; created_at:string; }
export interface PagedResult<T> { items:T[]; total:number; page:number; page_size:number; }
export interface GrantReview { participation_id:number; scholar_id:number; scholar_name:string; department:string|null; program_name:string; current_grant_type:GrantType|null; original_grant_label:string; standardized_at:string|null; standardization_note:string|null; }
