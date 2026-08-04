from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from prompts.interview_prep import INTERVIEW_PREP_PROMPT
from config import OPENAI_MODEL


class InterviewPrepChain:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model=OPENAI_MODEL)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", INTERVIEW_PREP_PROMPT),
                (
                    "human",
                    "Resume Summary:\n{resume_summary}\n\nJob Description Summary:\n{job_summary}\n\nIdentified Gaps:\n{gaps}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm

    def generate(self, resume_summary: str, job_summary: str, gaps: list[str]) -> dict:
        gaps_text = "\n".join(f"- {gap}" for gap in gaps)
        response = self.chain.invoke(
            {
                "resume_summary": resume_summary,
                "job_summary": job_summary,
                "gaps": gaps_text,
            }
        )
        content = response.content if hasattr(response, "content") else str(response)
        return self._parse_content(content)

    def _parse_content(self, text: str) -> dict:
        questions = []
        talking_points = []
        current_section = None

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            lower = stripped.lower()
            if "behavioral questions" in lower:
                current_section = "questions"
                continue
            elif "gap reframing" in lower:
                current_section = "gap_reframing"
                continue
            elif "key talking points" in lower:
                current_section = "talking_points"
                continue

            if current_section == "questions":
                if stripped[0].isdigit() or stripped.startswith(("-", "•", "*")):
                    questions.append(stripped.lstrip("0123456789.)-•* \t"))
                elif stripped and not stripped.endswith(":"):
                    questions.append(stripped)
            elif current_section == "talking_points":
                if stripped[0].isdigit() or stripped.startswith(("-", "•", "*")):
                    talking_points.append(stripped.lstrip("0123456789.)-•* \t"))
                elif stripped and not stripped.endswith(":"):
                    talking_points.append(stripped)
            elif current_section == "gap_reframing":
                if stripped[0].isdigit() or stripped.startswith(("-", "•", "*")):
                    talking_points.append(stripped.lstrip("0123456789.)-•* \t"))
                elif stripped and not stripped.endswith(":"):
                    talking_points.append(stripped)

        return {
            "questions": questions,
            "talking_points": talking_points,
        }
