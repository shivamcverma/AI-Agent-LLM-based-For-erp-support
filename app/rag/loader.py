import json
from pathlib import Path


class KnowledgeLoader:

    def __init__(self, knowledge_directory: str = "knowledge"):
        self.knowledge_directory = Path(knowledge_directory)

    def load_json(self, filename: str):
        file_path = self.knowledge_directory / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge file not found: {file_path}"
            )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                f"Knowledge file must contain a JSON list: {file_path}"
            )

        return data

    def load_all(self):
        knowledge = []

        for file_path in self.knowledge_directory.glob("*.json"):
            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(data, list):
                knowledge.extend(data)

        return knowledge