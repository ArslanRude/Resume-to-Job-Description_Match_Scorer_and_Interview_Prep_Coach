from loaders.resume_loader import ResumeLoader
from loaders.job_loader import JobDescriptionLoader
from chains.extraction import ResumeExtractionChain, JobExtractionChain
from chains.gap_analysis import GapAnalysisChain
from chains.interview_prep import InterviewPrepChain
from chains.resume_improvement import ResumeImprovementChain
from scoring.scorer import MatchScorer
from config import SCORE_THRESHOLD


def ingest_resume(state: dict) -> dict:
    resume_loader = ResumeLoader()
    state['resume_text'] = resume_loader.load(state['resume_path'])
    return state


def ingest_job(state: dict) -> dict:
    job_loader = JobDescriptionLoader()
    state['job_text'] = job_loader.load(state['job_source'])
    return state


def extract_resume(state: dict) -> dict:
    chain = ResumeExtractionChain()
    state['resume_schema'] = chain.extract(state['resume_text'])
    return state


def extract_job(state: dict) -> dict:
    chain = JobExtractionChain()
    state['job_schema'] = chain.extract(state['job_text'])
    return state


def review_resume(state: dict) -> dict:
    schema = state['resume_schema']
    while True:
        print("\n--- Resume Schema Review ---")
        print(schema.model_dump_json(indent=2))
        response = input("\nIs this correct? (yes/no): ").strip().lower()
        if response in ('yes', 'y'):
            break
        print("Enter field to edit (e.g., 'skills', 'education', 'work_experience', 'years_per_skill') or 'done' to finish editing:")
        field = input().strip().lower()
        if field == 'done':
            break
        if field in ('skills', 'education', 'work_experience', 'years_per_skill'):
            print(f"Current value: {getattr(schema, field)}")
            print("Enter new value as Python literal (e.g., ['Python', 'SQL']):")
            new_value = input().strip()
            try:
                import ast
                parsed_value = ast.literal_eval(new_value)
                setattr(schema, field, parsed_value)
                print(f"Updated {field}.")
            except (SyntaxError, ValueError):
                print("Invalid input. Please enter a valid Python literal.")
        else:
            print(f"Unknown field: {field}")
    state['resume_schema'] = schema
    return state


def score_match(state: dict) -> dict:
    scorer = MatchScorer()
    state['scores'] = scorer.score(state['resume_schema'], state['job_schema'])
    return state


def gap_analysis(state: dict) -> dict:
    chain = GapAnalysisChain()
    resume_summary = _build_resume_summary(state['resume_schema'])
    job_summary = _build_job_summary(state['job_schema'])
    missing_items = _identify_missing_items(state['resume_schema'], state['job_schema'])
    state['gaps'] = chain.analyze(resume_summary, job_summary, missing_items)
    return state


def interview_prep(state: dict) -> dict:
    chain = InterviewPrepChain()
    resume_summary = _build_resume_summary(state['resume_schema'])
    job_summary = _build_job_summary(state['job_schema'])
    gaps = state.get('gaps', [])
    state['prep_plan'] = chain.generate(resume_summary, job_summary, gaps)
    return state


def resume_improvement(state: dict) -> dict:
    chain = ResumeImprovementChain()
    resume_summary = _build_resume_summary(state['resume_schema'])
    job_summary = _build_job_summary(state['job_schema'])
    missing_items = _identify_missing_items(state['resume_schema'], state['job_schema'])
    state['improvements'] = chain.generate(resume_summary, job_summary, missing_items)
    return state


def should_route(state: dict) -> str:
    if state['scores']['overall'] >= SCORE_THRESHOLD:
        return 'interview_prep'
    return 'resume_improvement'


def _build_resume_summary(resume_schema) -> str:
    parts = []
    parts.append("Skills: " + ", ".join(resume_schema.skills))
    if resume_schema.years_per_skill:
        years_text = ", ".join(f"{k} ({v} yrs)" for k, v in resume_schema.years_per_skill.items())
        parts.append("Years per skill: " + years_text)
    if resume_schema.education:
        edu_text = "; ".join(f"{edu.degree} - {edu.institution}" for edu in resume_schema.education)
        parts.append("Education: " + edu_text)
    if resume_schema.work_experience:
        exp_parts = []
        for exp in resume_schema.work_experience:
            exp_parts.append(f"{exp.title} ({exp.dates}): " + "; ".join(exp.bullets))
        parts.append("Work Experience: " + " | ".join(exp_parts))
    return "\n".join(parts)


def _build_job_summary(job_schema) -> str:
    parts = []
    parts.append("Required skills: " + ", ".join(job_schema.required_skills))
    if job_schema.preferred_skills:
        parts.append("Preferred skills: " + ", ".join(job_schema.preferred_skills))
    if job_schema.years_required:
        years_text = ", ".join(f"{k} ({v} yrs)" for k, v in job_schema.years_required.items())
        parts.append("Years required: " + years_text)
    parts.append("Education required: " + job_schema.education_required)
    parts.append("Responsibilities: " + "; ".join(job_schema.responsibilities))
    return "\n".join(parts)


def _identify_missing_items(resume_schema, job_schema) -> list[str]:
    missing = []
    resume_skills = {skill.strip().lower() for skill in resume_schema.skills}

    for skill in job_schema.required_skills:
        if skill.strip().lower() not in resume_skills:
            missing.append(f"Missing required skill: {skill}")

    for skill in job_schema.preferred_skills:
        if skill.strip().lower() not in resume_skills:
            missing.append(f"Missing preferred skill: {skill}")

    resume_years = {k.strip().lower(): v for k, v in resume_schema.years_per_skill.items()}
    for skill, required_years in job_schema.years_required.items():
        key = skill.strip().lower()
        if key in resume_years and resume_years[key] < required_years:
            missing.append(f"Insufficient experience in {skill}: have {resume_years[key]} yrs, need {required_years} yrs")

    return missing
