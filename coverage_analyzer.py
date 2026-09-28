from typing import List, Dict, Any
class CoverageAnalyzer:
    def __init__(self, min_keyword_matches: int = 2):
        self.min_keyword_matches = min_keyword_matches

    def analyze(
        self,
        topic: str,
        sub_questions: List[str],
        search_results: List[Any],
        claims: List[Any],
        evidence: Any = None,
    ) -> Dict[str, Any]:
        search_text = self._combine_items(search_results)
        claim_text = self._combine_items(claims)
        evidence_text = self._combine_evidence(evidence)
        combined_text = f"{search_text} {claim_text} {evidence_text}".lower()
        covered_questions = []
        partial_questions = []
        missing_questions = []

        for question in sub_questions:
            keywords = self._extract_keywords(question)
            if not keywords:
                continue
            search_matches = sum(
                1 for keyword in keywords
                if keyword in search_text
            )
            claim_matches = sum(
                1 for keyword in keywords
                if keyword in claim_text
            )
            evidence_matches = sum(
                1 for keyword in keywords
                if keyword in evidence_text
            )
            total_matches = sum(
                1 for keyword in keywords
                if keyword in combined_text
            )

            if total_matches >= self.min_keyword_matches and evidence_matches > 0:
                covered_questions.append(question)
            elif total_matches >= self.min_keyword_matches:
                partial_questions.append(question)
            else:
                missing_questions.append(question)

        coverage_ratio = (
            len(covered_questions) / len(sub_questions)
            if sub_questions
            else 1.0
        )
        weak_evidence_areas = list(partial_questions)
        missing_source_types = self._detect_missing_source_types(search_results)
        if missing_questions:
            status = "INSUFFICIENT"
        elif partial_questions:
            status = "PARTIAL"
        else:
            status = "SUFFICIENT"

        return {
            "status": status,
            "coverage_ratio": round(coverage_ratio, 2),
            "covered_questions": covered_questions,
            "partial_questions": partial_questions,
            "missing_questions": missing_questions,
            "weak_evidence_areas": weak_evidence_areas,
            "missing_source_types": missing_source_types,
            "total_questions": len(sub_questions),
            "covered_count": len(covered_questions),
            "partial_count": len(partial_questions),
            "missing_count": len(missing_questions),
        }

    def generate_gap_queries(
        self,
        topic: str,
        coverage: Dict[str, Any],
        existing_queries: List[str],
        max_queries: int = 5,
    ) -> List[str]:
        candidates = []
        missing_questions = coverage.get("missing_questions", [])
        partial_questions = coverage.get("partial_questions", [])
        weak_areas = coverage.get("weak_evidence_areas", [])
        missing_source_types = coverage.get("missing_source_types", [])

        for question in missing_questions:
            candidates.extend([
                f"{topic} {question}",
                f"{topic} evidence {question}",
                f"{topic} research study {question}",
            ])

        for question in partial_questions:
            candidates.extend([
                f"{topic} evidence {question}",
                f"{topic} peer reviewed study {question}",
            ])

        for area in weak_areas:
            candidates.append(f"{topic} reliable evidence {area}")

        source_queries = {
            "research paper": [
                f"{topic} research paper",
                f"{topic} peer reviewed study",
            ],
            "technical documentation": [
                f"{topic} technical documentation",
                f"{topic} developer documentation",
            ],
            "industry source": [
                f"{topic} industry report",
                f"{topic} industry analysis",
            ],
            "news source": [
                f"{topic} latest news",
                f"{topic} technology news",
            ],
        }

        for source_type in missing_source_types:
            candidates.extend(
                source_queries.get(
                    source_type,
                    [f"{topic} {source_type}"],
                )
            )

        existing = {
            query.lower().strip()
            for query in existing_queries
        }

        queries = []
        for query in candidates:
            normalized = query.lower().strip()
            if normalized in existing:
                continue
            if normalized in {
                item.lower().strip()
                for item in queries
            }:
                continue
            queries.append(query)
            if len(queries) >= max_queries:
                break
        return queries

    def _detect_missing_source_types(self, search_results: List[Any]) -> List[str]:
        detected_types = set()
        for result in search_results:
            if isinstance(result, dict):
                text = " ".join(
                    str(result.get(key, ""))
                    for key in ("title", "snippet", "content", "url")
                ).lower()
            else:
                values = []
                for attribute in (
                    "title",
                    "snippet",
                    "content",
                    "url",
                    "source_type",
                ):
                    value = getattr(result, attribute, None)
                    if value:
                        values.append(str(value))

                text = " ".join(values).lower()

            if any(
                term in text
                for term in (
                    "research paper",
                    "journal",
                    "arxiv",
                    "doi",
                    "university",
                )
            ):
                detected_types.add("research paper")

            if any(
                term in text
                for term in (
                    "documentation",
                    "developer guide",
                    "official documentation",
                    "docs",
                )
            ):
                detected_types.add("technical documentation")

            if any(
                term in text
                for term in (
                    "company",
                    "industry",
                    "market",
                    "business",
                )
            ):
                detected_types.add("industry source")

            if any(
                term in text
                for term in (
                    "news",
                    "journalism",
                    "newspaper",
                )
            ):
                detected_types.add("news source")

        expected_types = {
            "research paper",
            "technical documentation",
            "industry source",
        }

        return sorted(expected_types - detected_types)

    def _combine_items(self, items: List[Any]) -> str:
        parts = []
        for item in items:
            if isinstance(item, dict):
                for key in (
                    "title",
                    "snippet",
                    "content",
                    "claim",
                    "description",
                ):
                    value = item.get(key)

                    if value:
                        parts.append(str(value))
            else:
                for attribute in (
                    "title",
                    "snippet",
                    "content",
                    "claim",
                    "description",
                ):
                    value = getattr(
                        item,
                        attribute,
                        None,
                    )

                    if value:
                        parts.append(str(value))

                if hasattr(item, "model_dump"):
                    data = item.model_dump()

                    for key in (
                        "text",
                        "statement",
                        "explanation",
                        "summary",
                    ):
                        value = data.get(key)
                        if value:
                            parts.append(str(value))

        return " ".join(parts).lower()

    def _combine_evidence(self, evidence: Any) -> str:
        if evidence is None:
            return ""

        if isinstance(evidence, dict):
            return " ".join(
                str(value)
                for value in evidence.values()
                if value
            ).lower()

        if hasattr(evidence, "model_dump"):
            data = evidence.model_dump()
            parts = []

            for value in data.values():
                if isinstance(value, list):
                    parts.extend(
                        str(item)
                        for item in value
                        if item
                    )
                elif value:
                    parts.append(str(value))
            return " ".join(parts).lower()
        return str(evidence).lower()

    def _extract_keywords(self, text: str) -> set[str]:
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
            "long",
            "term",
        }

        cleaned = (
            text.lower()
            .replace("?", "")
            .replace(",", "")
            .replace(".", "")
            .replace(":", "")
            .replace(";", "")
            .replace("-", " ")
        )
        words = cleaned.split()
        return {
            word
            for word in words
            if len(word) > 2
            and word not in stopwords
        }


if __name__ == "__main__":
    analyzer = CoverageAnalyzer()
    topic = "impact of generative AI on software development"
    sub_questions = [
        "What are the major productivity benefits of generative AI?",
        "What security risks are introduced by generative AI?",
        "What are the long term maintenance implications?",
    ]
    search_results = [
        {
            "title": "Generative AI and Developer Productivity",
            "snippet": "Generative AI can improve developer productivity by automating repetitive software development tasks.",
        },
        {
            "title": "Security Risks of Generative AI",
            "snippet": "Generative AI can introduce security risks when used in software development.",
        },
    ]

    claims = [
        {
            "claim": "Generative AI can improve developer productivity for some software development tasks."
        },
        {
            "claim": "Generative AI can introduce security risks when used in software development."
        },
    ]

    coverage = analyzer.analyze(
        topic=topic,
        sub_questions=sub_questions,
        search_results=search_results,
        claims=claims,
    )

    print("=" * 70)
    print("COVERAGE ANALYZER MODULE TEST")
    print("=" * 70)
    print()
    print("Status:", coverage["status"])
    print("Coverage ratio:", coverage["coverage_ratio"])
    print()
    print("Covered questions:")

    for question in coverage["covered_questions"]:
        print(f"- {question}")
    print()
    print("Partial questions:")
    for question in coverage["partial_questions"]:
        print(f"- {question}")
    print()
    print("Missing questions:")
    for question in coverage["missing_questions"]:
        print(f"- {question}")
    refined_queries = analyzer.generate_gap_queries(
        topic=topic,
        coverage=coverage,
        existing_queries=[
            "generative AI software development",
            "generative AI developer productivity",
        ],
        max_queries=10,
    )

    print()
    print("Gap queries:")
    for query in refined_queries:
        print(f"- {query}")
    assert coverage["status"] in {
        "INSUFFICIENT",
        "PARTIAL",
        "SUFFICIENT",
    }

    assert len(coverage["missing_questions"]) > 0
    assert len(refined_queries) > 0
    assert any(
        "research paper" in query.lower()
        or "peer reviewed" in query.lower()
        for query in refined_queries
    )
    print()
    print("=" * 70)
    print("COVERAGE ANALYZER MODULE TEST PASSED")
    print("=" * 70)