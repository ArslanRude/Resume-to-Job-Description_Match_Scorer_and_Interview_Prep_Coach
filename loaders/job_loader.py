import requests


class JobDescriptionLoader:
    def __init__(self) -> None:
        pass

    def load(self, source: str) -> str:
        if source.startswith('http://') or source.startswith('https://'):
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            return response.text
        return source
