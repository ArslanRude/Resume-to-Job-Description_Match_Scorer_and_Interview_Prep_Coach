import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader


class ResumeLoader:
    def __init__(self) -> None:
        pass

    def load(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        documents = loader.load()
        return "\n".join(doc.page_content for doc in documents)
