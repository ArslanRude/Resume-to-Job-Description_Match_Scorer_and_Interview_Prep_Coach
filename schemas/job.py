from pydantic import BaseModel
from typing import List, Dict


class JobSchema(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    years_required: Dict[str, float]
    education_required: str
    responsibilities: List[str]
