from rapidfuzz import fuzz


class KnowledgeRetriever:

    def __init__(self, knowledge):
        self.knowledge = knowledge

    def search(self, query: str, top_k: int = 3):
        query = query.lower().strip()

        results = []

        for item in self.knowledge:

            intent = item.get("intent", "")
            keywords = item.get("keywords", [])
            answer = item.get("answer", "")
            steps = item.get("steps", [])

            best_score = 0
            matched_keyword = ""

            for keyword in keywords:

                keyword = keyword.lower().strip()

                score = fuzz.token_set_ratio(
                    query,
                    keyword
                )

                if score > best_score:
                    best_score = score
                    matched_keyword = keyword

            if best_score > 0:

                results.append({
                    "intent": intent,
                    "score": best_score,
                    "matched_keyword": matched_keyword,
                    "answer": answer,
                    "steps": steps
                })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]