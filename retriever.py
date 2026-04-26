import json
import os
import re


class PetCareRetriever:
    """Keyword-based retriever over a local pet-care knowledge base."""

    _DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "pet_knowledge.json")

    def __init__(self, knowledge_path: str = None):
        path = knowledge_path or self._DEFAULT_PATH
        with open(path, "r", encoding="utf-8") as f:
            self._knowledge = json.load(f)

    def _tokenise(self, text: str) -> set[str]:
        return set(re.findall(r"[a-z]+", text.lower()))

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Return the top-k most relevant tips for the given query.

        Scoring: each tag that appears in the query tokens adds 2 points;
        each query token found anywhere in the tip text adds 1 point.
        """
        query_tokens = self._tokenise(query)
        if not query_tokens:
            return []

        scored = []
        for entry in self._knowledge:
            tag_hits = len(query_tokens & set(entry["tags"]))
            text_hits = len(query_tokens & self._tokenise(entry["tip"]))
            score = tag_hits * 2 + text_hits
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]
