from typing import List, Set

class QueryRefiner:
    """
    Deterministic query refinement engine.
    Takes an initial research plan and search results,
    identifies missing research areas, and generates
    additional search queries.
    This first implementation is intentionally deterministic.
    It can later be upgraded to a Gemini-powered agent.
    """

    def __init__(self, max_refined_queries: int = 5,):
        self.max_refined_queries = max_refined_queries

    def analyze_coverage(
        self,
        topic: str,
        sub_questions: List[str],
        search_results: List,
    ) -> List[str]:
        """
        Identify research areas that appear to have
        insufficient search coverage.
        """
        combined_text = self._combine_search_results(search_results)
        missing_areas = []
        for question in sub_questions:
            question_keywords = self._extract_keywords(question)
            if not question_keywords:
                continue

            matched = sum(1 for keyword in question_keywords if keyword in combined_text)
            threshold = max(1, len(question_keywords) // 2,)
            if matched < threshold:
                missing_areas.append(question)
        return missing_areas

    def generate_refined_queries(
        self,
        topic: str,
        missing_areas: List[str],
        existing_queries: List[str],
    ) -> List[str]:
        """
        Generate additional search queries for
        missing research areas.
        """
        existing_normalized = {
            query.lower().strip()
            for query in existing_queries
        }
        refined_queries = []
        for area in missing_areas:
            candidates = [
                f"{topic} {area}",
                f"{topic} evidence {area}",
                f"{topic} research study {area}",
            ]

            for query in candidates:
                normalized = (query.lower().strip())
                if normalized in existing_normalized:
                    continue
                if normalized in {
                    item.lower().strip()
                    for item in refined_queries
                }:
                    continue
                refined_queries.append(query)
                if (len(refined_queries)>= self.max_refined_queries):
                    return refined_queries

        return refined_queries

    def refine(
        self,
        topic: str,
        sub_questions: List[str],
        existing_queries: List[str],
        search_results: List,
    ) -> dict:
        """
        Analyze coverage and generate refined queries.
        """
        missing_areas = (
            self.analyze_coverage(
                topic,
                sub_questions,
                search_results,
            )
        )

        refined_queries = (
            self.generate_refined_queries(
                topic,
                missing_areas,
                existing_queries,
            )
        )

        return {
            "missing_areas": missing_areas,
            "refined_queries": refined_queries,
            "coverage_complete": (
                len(missing_areas) == 0
            ),
        }

    def _combine_search_results(self, search_results: List,) -> str:
        """
        Combine titles/snippets/content from search results.
        """
        parts = []
        for result in search_results:
            if isinstance(result,dict,):
                parts.extend(
                    [
                        str(result.get("title","",)),
                        str(result.get("snippet","",)),
                        str(result.get("content","",)),
                    ]
                )

            else:
                parts.extend(
                    [
                        str(getattr(result,"title","",)),
                        str(getattr(result,"snippet","",)),
                        str(getattr(result,"content","",)),
                    ]
                )
        return " ".join(parts).lower()

    def _extract_keywords(
        self,
        text: str,
    ) -> Set[str]:
        """
        Extract simple meaningful keywords.
        Stopwords are removed so the coverage check
        focuses on meaningful terms.
        """

        stopwords = {
            "what",
            "are",
            "the",
            "is",
            "of",
            "on",
            "in",
            "to",
            "and",
            "for",
            "a",
            "an",
            "about",
            "how",
            "does",
            "do",
            "can",
            "should",
            "be",
            "with",
            "from",
            "major",
            "aspects",
            "evidence",
            "supports",
            "claims",
            "limitations",
            "risks",
            "considered",
        }

        words = (
            text.lower()
            .replace("?", "")
            .replace(",", "")
            .replace(".", "")
            .split()
        )

        return {
            word
            for word in words
            if len(word) > 2
            and word not in stopwords
        }

if __name__ == "__main__":
    print("=" * 70)
    print("QUERY REFINER MODULE TEST")
    print("=" * 70)
    topic = (
        "impact of generative AI "
        "on software development"
    )

    sub_questions = [
        (
            "What are the major productivity "
            "benefits of generative AI?"
        ),
        (
            "What security risks are introduced "
            "by generative AI?"
        ),
        (
            "What are the long term maintenance "
            "implications?"
        ),
    ]

    existing_queries = [
        "generative AI software development",
        "generative AI developer productivity",
    ]

    search_results = [
        {
            "title": (
                "Generative AI Developer Productivity"
            ),
            "snippet": (
                "Generative AI coding assistants "
                "can improve developer productivity "
                "and software development workflows."
            ),
        },
        {
            "title": (
                "Generative AI Security Risks"
            ),
            "snippet": (
                "AI coding tools introduce security "
                "and code quality considerations."
            ),
        },
    ]

    refiner = QueryRefiner(max_refined_queries=5)
    result = refiner.refine(
        topic=topic,
        sub_questions=sub_questions,
        existing_queries=existing_queries,
        search_results=search_results,
    )

    print("\nMissing research areas:")
    for area in result["missing_areas"]:
        print(f"- {area}")
    print("\nRefined queries:")
    for query in result["refined_queries"]:
        print(f"- {query}")
    print(
        "\nCoverage complete:",
        result["coverage_complete"],
    )

    assert isinstance(result,dict,)
    assert ("missing_areas"in result)
    assert ("refined_queries"in result)
    assert ("coverage_complete" in result)
    assert len(result["missing_areas"]) > 0
    assert len(result["refined_queries"]) > 0
    for query in result["refined_queries"]:
        assert (
            query.lower()
            not in {
                item.lower()
                for item in existing_queries
            }
        )

    print("\n" + "=" * 70)
    print("QUERY REFINER MODULE TEST PASSED")
    print("=" * 70)