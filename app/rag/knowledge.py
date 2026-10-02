from app.rag.loader import KnowledgeLoader
from app.rag.retriever import KnowledgeRetriever


class KnowledgeBase:

    def __init__(self):
        self.loader = KnowledgeLoader()

        self.knowledge = self.loader.load_all()

        self.retriever = KnowledgeRetriever(
            self.knowledge
        )

    def search(self, query: str, top_k: int = 3):
        return self.retriever.search(
            query=query,
            top_k=top_k
        )