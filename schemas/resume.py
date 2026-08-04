from pydantic import BaseModel, Field
from typing import List, Dict


class WorkExperience(BaseModel):
    title: str
    dates: str
    bullets: List[str]


class Education(BaseModel):
    degree: str
    institution: str


class ResumeSchema(BaseModel):
    skills: List[str]
    years_per_skill: Dict[str, float]
    education: List[Education]
    work_experience: List[WorkExperience]
