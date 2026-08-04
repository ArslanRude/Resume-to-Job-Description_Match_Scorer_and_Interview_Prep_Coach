import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
SCORE_THRESHOLD = 0.70
SKILLS_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.30
EDUCATION_WEIGHT = 0.15
KEYWORDS_WEIGHT = 0.15


def load_env() -> None:
    load_dotenv()
