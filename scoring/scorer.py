from schemas.resume import ResumeSchema
from schemas.job import JobSchema
from config import (
    SKILLS_WEIGHT,
    EXPERIENCE_WEIGHT,
    EDUCATION_WEIGHT,
    KEYWORDS_WEIGHT,
)


class MatchScorer:
    def __init__(self) -> None:
        pass

    def score(self, resume: ResumeSchema, job: JobSchema) -> dict:
        skills_score = self._compute_skills_score(resume, job)
        experience_score = self._compute_experience_score(resume, job)
        education_score = self._compute_education_score(resume, job)
        keywords_score = self._compute_keywords_score(resume, job)

        overall = (
            skills_score * SKILLS_WEIGHT
            + experience_score * EXPERIENCE_WEIGHT
            + education_score * EDUCATION_WEIGHT
            + keywords_score * KEYWORDS_WEIGHT
        )

        return {
            "overall": overall,
            "skills": skills_score,
            "experience": experience_score,
            "education": education_score,
            "keywords": keywords_score,
        }

    def _compute_skills_score(self, resume: ResumeSchema, job: JobSchema) -> float:
        if not job.required_skills:
            return 0.0

        resume_skills = {skill.strip().lower() for skill in resume.skills}
        matched = sum(
            1
            for skill in job.required_skills
            if skill.strip().lower() in resume_skills
        )
        return matched / len(job.required_skills)

    def _compute_experience_score(self, resume: ResumeSchema, job: JobSchema) -> float:
        if not job.years_required:
            return 0.0

        resume_years = {
            skill.strip().lower(): years
            for skill, years in resume.years_per_skill.items()
        }

        ratios = []
        for skill, required_years in job.years_required.items():
            key = skill.strip().lower()
            resume_years_value = resume_years.get(key, 0.0)
            if required_years > 0:
                ratio = resume_years_value / required_years
                ratios.append(min(ratio, 1.0))
            else:
                ratios.append(1.0)

        if not ratios:
            return 0.0

        return sum(ratios) / len(ratios)

    def _compute_education_score(self, resume: ResumeSchema, job: JobSchema) -> float:
        required_level = job.education_required.strip().lower()
        if not required_level:
            return 0.0

        resume_degrees = [edu.degree.strip().lower() for edu in resume.education]
        if not resume_degrees:
            return 0.0

        level_order = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "bachelor's": 3,
            "bachelors": 3,
            "master": 4,
            "master's": 4,
            "masters": 4,
            "phd": 5,
            "doctorate": 5,
        }

        required_rank = level_order.get(required_level)
        if required_rank is None:
            # Try to find the level within the string
            for key, rank in level_order.items():
                if key in required_level:
                    required_rank = rank
                    break
            if required_rank is None:
                return 0.0

        best_rank = 0
        for degree in resume_degrees:
            rank = level_order.get(degree)
            if rank is None:
                for key, candidate_rank in level_order.items():
                    if key in degree:
                        rank = candidate_rank
                        break
            if rank is not None and rank > best_rank:
                best_rank = rank

        if best_rank >= required_rank:
            return 1.0
        elif best_rank > 0:
            return 0.5
        else:
            return 0.0

    def _compute_keywords_score(self, resume: ResumeSchema, job: JobSchema) -> float:
        if not job.responsibilities:
            return 0.0

        resume_text = self._build_resume_text(resume)
        resume_keywords = set()
        for token in resume_text.split():
            cleaned = token.strip(".,;:!?()[]{}'\"")
            if cleaned:
                resume_keywords.add(cleaned.lower())

        job_keywords = set()
        for responsibility in job.responsibilities:
            for token in responsibility.split():
                cleaned = token.strip(".,;:!?()[]{}'\"")
                if cleaned:
                    job_keywords.add(cleaned.lower())

        if not job_keywords:
            return 0.0

        matched = len(job_keywords.intersection(resume_keywords))
        return matched / len(job_keywords)

    def _build_resume_text(self, resume: ResumeSchema) -> str:
        parts = list(resume.skills)

        for skill, years in resume.years_per_skill.items():
            parts.append(f"{skill} {years}")

        for edu in resume.education:
            parts.append(edu.degree)
            parts.append(edu.institution)

        for exp in resume.work_experience:
            parts.append(exp.title)
            parts.append(exp.dates)
            parts.extend(exp.bullets)

        return " ".join(parts)
