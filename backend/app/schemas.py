from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
FsdpStatus = Literal["On Going", "Graduated", "Payback", "Withdrawn"]
GrantType = Literal["Full Scholarship", "Partial Scholarship", "Dissertation Aid", "Others"]
class ProgramBase(BaseModel): name: str = Field(min_length=1,max_length=300); delivering_hei: str|None = Field(default=None,max_length=200); description: str|None=None
class ProgramCreate(ProgramBase): pass
class ProgramUpdate(ProgramBase): pass
class ProgramRead(ProgramBase): model_config=ConfigDict(from_attributes=True); id:int
class ParticipationInput(BaseModel):
    program_name:str=Field(min_length=1,max_length=300); delivering_hei:str|None=Field(default=None,max_length=200); start_date:date|None=None; end_date:date|None=None; start_term:str|None=Field(default=None,max_length=50); start_academic_year:str|None=Field(default=None,max_length=20); end_term:str|None=Field(default=None,max_length=50); end_academic_year:str|None=Field(default=None,max_length=20); grant_type:GrantType|None=None; grant_other:str|None=Field(default=None,max_length=200); status:FsdpStatus="On Going"; extension:str|None=Field(default=None,max_length=200); remarks:str|None=None
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and not self.start_date: raise ValueError("An end date requires a start date.")
        if self.start_date and self.end_date and self.end_date<self.start_date: raise ValueError("End date cannot precede start date.")
        if bool(self.start_term) != bool(self.start_academic_year): raise ValueError("Enter both the starting term and academic year.")
        if bool(self.end_term) != bool(self.end_academic_year): raise ValueError("Enter both the ending term and academic year.")
        if self.grant_type=="Others" and not (self.grant_other or "").strip(): raise ValueError("Describe the other grant type.")
        return self
class ScholarBase(BaseModel):
    name:str=Field(min_length=1,max_length=200); age:int|None=Field(default=None,ge=18,le=100); previous_degree:str|None=Field(default=None,max_length=300); missing_requirements:bool=False; department:str|None=Field(default=None,max_length=120); rank:str|None=Field(default=None,max_length=120); tenure:str|None=Field(default=None,max_length=120); participations:list[ParticipationInput]=Field(default_factory=list)
class ScholarCreate(ScholarBase): pass
class ScholarUpdate(ScholarBase): pass
class ParticipationRead(BaseModel): id:int; program_id:int; name:str; delivering_hei:str|None; description:str|None; start_date:date|None; end_date:date|None; start_term:str|None; start_academic_year:str|None; end_term:str|None; end_academic_year:str|None; grant_type:GrantType|None; grant_other:str|None; status:FsdpStatus; extension:str|None; remarks:str|None
class ScholarRead(BaseModel): id:int; name:str; age:int|None; previous_degree:str|None; missing_requirements:bool; department:str|None; rank:str|None; personnel_type:Literal["Faculty","Staff"]; tenure:str|None; data_source:str; participations:list[ParticipationRead]; created_at:datetime; updated_at:datetime
class FsdpSummary(BaseModel): total:int; ongoing:int; graduated:int; payback:int; withdrawn:int; missing_requirements:int
