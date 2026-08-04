from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from prompts.gap_analysis import GAP_ANALYSIS_PROMPT
from config import OPENAI_MODEL


class GapAnalysisChain:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model=OPENAI_MODEL)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", GAP_ANALYSIS_PROMPT),
                (
                    "human",
                    "Resume Summary:\n{resume_summary}\n\nJob Description Summary:\n{job_summary}\n\nMissing Items:\n{missing_items}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm

    def analyze(self, resume_summary: str, job_summary: str, missing_items: list[str]) -> list[str]:
        missing_items_text = "\n".join(f"- {item}" for item in missing_items)
        response = self.chain.invoke(
            {
                "resume_summary": resume_summary,
                "job_summary": job_summary,
                "missing_items": missing_items_text,
            }
        )
        content = response.content if hasattr(response, "content") else str(response)
        return self._parse_gaps(content)

    def _parse_gaps(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        gaps = []
        for line in lines:
            cleaned = line.lstrip("0123456789.)- \t")
            if cleaned:
                gaps.append(cleaned)
        return gaps
