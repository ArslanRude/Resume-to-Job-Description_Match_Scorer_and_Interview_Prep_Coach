from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from schemas.resume import ResumeSchema
from schemas.job import JobSchema
from prompts.extraction import EXTRACTION_SYSTEM_PROMPT
from config import OPENAI_MODEL


class ResumeExtractionChain:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model=OPENAI_MODEL)
        self.parser = PydanticOutputParser(pydantic_object=ResumeSchema)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                (
                    "human",
                    "Here is the resume text:\n\n{resume_text}\n\n{format_instructions}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm | self.parser

    def extract(self, resume_text: str) -> ResumeSchema:
        return self.chain.invoke(
            {
                "resume_text": resume_text,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )


class JobExtractionChain:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model=OPENAI_MODEL)
        self.parser = PydanticOutputParser(pydantic_object=JobSchema)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                (
                    "human",
                    "Here is the job description text:\n\n{job_text}\n\n{format_instructions}",
                ),
            ]
        )
        self.chain = self.prompt | self.llm | self.parser

    def extract(self, job_text: str) -> JobSchema:
        return self.chain.invoke(
            {
                "job_text": job_text,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )
