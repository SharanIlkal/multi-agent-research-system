from tests.mock_research_data import (
    TEST_TOPIC,
    create_mock_claims,
    create_mock_sources,
)

from evidence import build_evidence_package


def main():
    print("=" * 70)
    print("EVIDENCE ENGINE MOCK INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Load deterministic mock research data
    # --------------------------------------------------------

    sources = create_mock_sources()
    claims = create_mock_claims()

    print(f"\nTopic: {TEST_TOPIC}")
    print(f"Sources: {len(sources)}")
    print(f"Claims: {len(claims)}")

    # --------------------------------------------------------
    # 2. Build Evidence Package
    # --------------------------------------------------------

    print("\nBuilding Evidence Package...")

    evidence = build_evidence_package(
        topic=TEST_TOPIC,
        sources=sources,
        claims=claims,
        use_llm=False,
        
    )

    # --------------------------------------------------------
    # 3. Display results
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("EVIDENCE ENGINE RESULTS")
    print("=" * 70)

    print(
        f"\nSource evaluations: "
        f"{len(evidence.source_evaluations)}"
    )

    print(
        f"Fact checks: "
        f"{len(evidence.fact_checks)}"
    )

    print(
        f"Contradictions: "
        f"{len(evidence.contradictions)}"
    )

    print(
        f"Citations: "
        f"{len(evidence.citations)}"
    )

    # --------------------------------------------------------
    # 4. Print source evaluations
    # --------------------------------------------------------

    if evidence.source_evaluations:

        print("\n" + "-" * 70)
        print("SOURCE EVALUATIONS")
        print("-" * 70)

        for index, evaluation in enumerate(
            evidence.source_evaluations,
            start=1,
        ):
            print(f"\n[{index}] {evaluation.title}")
            print(
                f"Relevance: "
                f"{evaluation.relevance_score}"
            )
            print(
                f"Authority: "
                f"{evaluation.authority_score}"
            )
            print(
                f"Recency: "
                f"{evaluation.recency_score}"
            )
            print(
                f"Evidence Quality: "
                f"{evaluation.evidence_quality_score}"
            )
            print(
                f"Overall: "
                f"{evaluation.overall_score}"
            )

    # --------------------------------------------------------
    # 5. Print fact checks
    # --------------------------------------------------------

    if evidence.fact_checks:

        print("\n" + "-" * 70)
        print("FACT CHECKS")
        print("-" * 70)

        for index, fact_check in enumerate(
            evidence.fact_checks,
            start=1,
        ):
            print(
                f"\n[{index}] {fact_check.claim}"
            )

            print(
                f"Status: "
                f"{fact_check.status}"
            )

            print(
                f"Confidence: "
                f"{fact_check.confidence}"
            )

            print(
                f"Explanation: "
                f"{fact_check.explanation}"
            )

    # --------------------------------------------------------
    # 6. Print contradictions
    # --------------------------------------------------------

    if evidence.contradictions:

        print("\n" + "-" * 70)
        print("CONTRADICTIONS")
        print("-" * 70)

        for index, contradiction in enumerate(
            evidence.contradictions,
            start=1,
        ):
            print(
                f"\n[{index}] "
                f"{contradiction.topic}"
            )

            print(
                f"Claim A: "
                f"{contradiction.claim_a}"
            )

            print(
                f"Source A: "
                f"{contradiction.source_a}"
            )

            print(
                f"Claim B: "
                f"{contradiction.claim_b}"
            )

            print(
                f"Source B: "
                f"{contradiction.source_b}"
            )

            print(
                f"Severity: "
                f"{contradiction.severity}"
            )

            print(
                f"Explanation: "
                f"{contradiction.explanation}"
            )

    # --------------------------------------------------------
    # 7. Print citations
    # --------------------------------------------------------

    if evidence.citations:

        print("\n" + "-" * 70)
        print("CITATIONS")
        print("-" * 70)

        for index, citation in enumerate(
            evidence.citations,
            start=1,
        ):
            print(
                f"\n[{index}] "
                f"{citation.claim}"
            )

            print(
                f"Source: "
                f"{citation.source_title}"
            )

            print(
                f"URL: "
                f"{citation.source_url}"
            )

            print(
                f"Evidence: "
                f"{citation.supporting_evidence}"
            )

    # --------------------------------------------------------
    # 8. Validate output
    # --------------------------------------------------------

    assert evidence is not None

    assert hasattr(
        evidence,
        "source_evaluations",
    )

    assert hasattr(
        evidence,
        "fact_checks",
    )

    assert hasattr(
        evidence,
        "contradictions",
    )

    assert hasattr(
        evidence,
        "citations",
    )

    print("\n" + "=" * 70)
    print("EVIDENCE ENGINE MOCK TEST COMPLETED")
    print("=" * 70)

    print(
        "\nEvidencePackage structure is valid."
    )


if __name__ == "__main__":
    main()