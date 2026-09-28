from schemas import ResearchState

from tests.mock_research_data import (
    TEST_TOPIC,
    create_mock_claims,
    create_mock_sources,
)

from evidence import build_evidence_package
from tests.mock_writer import create_mock_report
from tests.mock_critic import create_mock_critique
from tests.mock_refinement_test import (
    revise_mock_report,
    create_mock_pass_critique,
)


def main():

    print("=" * 70)
    print("OFFLINE RESEARCH ORCHESTRATOR TEST")
    print("=" * 70)

    # ========================================================
    # 1. INITIAL STATE
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 1 — INITIAL RESEARCH STATE")
    print("-" * 70)

    state = ResearchState(
        topic=TEST_TOPIC,
        status="initialized",
    )

    print(
        f"\nTopic: {state.topic}"
    )

    print(
        f"Status: {state.status}"
    )

    # ========================================================
    # 2. MOCK SOURCE COLLECTION
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 2 — SOURCE COLLECTION")
    print("-" * 70)

    sources = create_mock_sources()

    state.sources = sources
    state.status = "sources_collected"

    print(
        f"\nSources collected: "
        f"{len(state.sources)}"
    )

    for index, source in enumerate(
        state.sources,
        start=1,
    ):

        print(
            f"{index}. {source.title}"
        )

    # ========================================================
    # 3. MOCK CLAIM EXTRACTION
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 3 — CLAIM EXTRACTION")
    print("-" * 70)

    claims = create_mock_claims()

    state.status = "claims_extracted"

    print(
        f"\nClaims extracted: "
        f"{len(claims)}"
    )

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        print(
            f"{index}. {claim.claim}"
        )

    # ========================================================
    # 4. EVIDENCE ENGINE
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 4 — EVIDENCE ENGINE")
    print("-" * 70)

    evidence = build_evidence_package(
        topic=TEST_TOPIC,
        sources=sources,
        claims=claims,
        use_llm=False,
    )

    state.evidence = evidence
    state.status = "evidence_built"

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

    # ========================================================
    # 5. RESEARCH WRITER
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 5 — RESEARCH WRITER")
    print("-" * 70)

    report = create_mock_report(
        topic=TEST_TOPIC,
        sources=sources,
        claims=claims,
        evidence=evidence,
    )

    state.report = report.model_dump_json(
        indent=2
    )

    state.status = "report_generated"

    print(
        f"\nReport generated:"
        f"\n{report.title}"
    )

    print(
        f"\nKey findings: "
        f"{len(report.key_findings)}"
    )

    print(
        f"References: "
        f"{len(report.references)}"
    )

    # ========================================================
    # 6. RESEARCH CRITIC
    # ========================================================

    print("\n" + "-" * 70)
    print("STAGE 6 — RESEARCH CRITIC")
    print("-" * 70)

    critique = create_mock_critique(
        report_text=state.report
    )

    print(
        f"\nCritic status: "
        f"{critique.overall_status}"
    )

    print(
        f"Recommendations: "
        f"{len(critique.recommendations)}"
    )

    # ========================================================
    # 7. REFINEMENT
    # ========================================================

    if critique.overall_status == "REVISE":

        print("\n" + "-" * 70)
        print("STAGE 7 — REPORT REFINEMENT")
        print("-" * 70)

        revised_report = revise_mock_report(
            report
        )

        state.report = (
            revised_report.model_dump_json(
                indent=2
            )
        )

        print(
            "\nReport revised successfully."
        )

        # ----------------------------------------------------
        # FINAL CRITIC
        # ----------------------------------------------------

        final_critique = create_mock_pass_critique()

    else:

        revised_report = report

        final_critique = critique

    print(
        f"\nFinal critic status: "
        f"{final_critique.overall_status}"
    )

    # ========================================================
    # 8. FINAL STATE
    # ========================================================

    state.feedback = (
        "Final critic status: "
        f"{final_critique.overall_status}"
    )

    state.status = "completed"

    # ========================================================
    # 9. VALIDATION
    # ========================================================

    assert state.topic == TEST_TOPIC

    assert len(state.sources) == 2

    assert len(claims) == 4

    assert len(
        state.evidence.source_evaluations
    ) == 2

    assert len(
        state.evidence.fact_checks
    ) == 4

    assert len(
        state.evidence.citations
    ) == 4

    assert state.report

    assert (
        final_critique.overall_status
        == "PASS"
    )

    assert (
        state.status
        == "completed"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("OFFLINE ORCHESTRATOR TEST PASSED")
    print("=" * 70)

    print(
        "\nComplete pipeline:"
    )

    print(
        "ResearchState"
        " → Sources"
        " → Claims"
        " → Evidence"
        " → Writer"
        " → Critic"
        " → Revision"
        " → PASS"
    )

    print(
        "\nFinal state:"
    )

    print(
        f"Status: {state.status}"
    )

    print(
        f"Sources: {len(state.sources)}"
    )

    print(
        f"Claims: {len(claims)}"
    )

    print(
        f"Evidence citations: "
        f"{len(state.evidence.citations)}"
    )

    print(
        f"Final critique: "
        f"{final_critique.overall_status}"
    )


if __name__ == "__main__":
    main()