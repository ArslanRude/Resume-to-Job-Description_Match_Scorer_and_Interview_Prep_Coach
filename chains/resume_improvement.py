from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from prompts.resume_improvement import RESUME_IMPROVEMENT_PROMPT
from config import OPENAI_MODEL


class ResumeImprovementChain:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model=OPENAI_MODEL)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", RESUME_IMPROVEMENT_PROMPT),
                (
                    "human",
                    "Resume Summary:\n{resume_summary}\n\nJob Description Summary:\n{job_summary}\n\nMissing Items:\n{missing_items}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm

    def generate(self, resume_summary: str, job_summary: str, missing_items: list[str]) -> list[str]:
        missing_items_text = "\n".join(f"- {item}" for item in missing_items)
        response = self.chain.invoke(
            {
                "resume_summary": resume_summary,
                "job_summary": job_summary,
                "missing_items": missing_items_text,
            }
        )
        content = response.content if hasattr(response, "content") else str(response)
        return self._parse_suggestions(content)

    def _parse_suggestions(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        suggestions = []
        for line in lines:
            cleaned = line.lstrip("0123456789.)-•* \t")
            if cleaned:
                suggestions.append(cleaned)
        return suggestions
