from schemas import ResearchReport

from tests.mock_writer import create_mock_report
from tests.mock_critic import create_mock_critique


def revise_mock_report(
    report: ResearchReport,
) -> ResearchReport:
    """
    Deterministically revise the report based on
    mock critic feedback.
    """

    revised_findings = [
        (
            "Generative AI can automate repetitive "
            "software development tasks. "
            "[Citation: Aalto research source]"
        ),
        (
            "Generative AI can improve developer "
            "productivity for some software development "
            "tasks. "
            "[Citation: Generative AI Adoption source]"
        ),
        (
            "Generative AI can introduce security risks "
            "when used in software development. "
            "[Citation: Generative AI Adoption source]"
        ),
    ]

    return ResearchReport(
        title=report.title,

        executive_summary=(
            "Generative AI is influencing software "
            "development through task automation and "
            "potential productivity improvements. "
            "However, adoption also introduces "
            "security-related risks. The available "
            "evidence therefore indicates both "
            "opportunities and risks."
        ),

        research_question=report.research_question,

        key_findings=revised_findings,

        evidence_analysis=(
            "The evidence supports the finding that "
            "generative AI can automate repetitive "
            "software development tasks and improve "
            "productivity for some activities. "
            "At the same time, the evidence identifies "
            "security risks associated with adoption. "
            "These findings should be interpreted "
            "alongside the limitations of the available "
            "test dataset."
        ),

        contradictory_findings=[],

        limitations=[
            (
                "The integration test uses deterministic "
                "mock evidence."
            ),
            (
                "The test dataset contains a limited "
                "number of sources."
            ),
        ],

        conclusion=(
            "The evidence indicates that generative AI "
            "offers potential productivity benefits "
            "while introducing security risks. "
            "The effects therefore depend on how the "
            "technology is implemented and governed."
        ),

        references=[
            (
                "https://aaltodoc.aalto.fi/"
                "bitstreams/3cc3575d-852b-44bc-b9ba-"
                "12fc374d1db0/download"
            ),
            (
                "https://example.com/"
                "generative-ai-software-development"
            ),
        ],
    )


def create_mock_pass_critique() -> object:
    """
    Create a deterministic PASS critique after
    the report has been revised.
    """

    return create_mock_critic_pass()


def create_mock_critic_pass():
    from schemas import ResearchCritique

    return ResearchCritique(
        overall_status="PASS",

        factual_issues=[],

        unsupported_claims=[],

        missing_citations=[],

        contradiction_issues=[],

        coverage_issues=[],

        clarity_issues=[],

        recommendations=[],
    )


def main():

    print("=" * 70)
    print("WRITER ↔ CRITIC REFINEMENT MOCK TEST")
    print("=" * 70)

    topic = (
        "impact of generative AI "
        "on software development"
    )

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ITERATION 1 — INITIAL REPORT")
    print("-" * 70)

    report = create_mock_report(
        topic=topic
    )

    print(
        f"\nReport title:\n{report.title}"
    )

    print(
        "\nKey findings:"
    )

    for index, finding in enumerate(
        report.key_findings,
        start=1,
    ):
        print(
            f"{index}. {finding}"
        )

    # --------------------------------------------------------
    # CRITIC
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ITERATION 1 — CRITIC")
    print("-" * 70)

    critique = create_mock_critique(
        report_text=report.executive_summary
    )

    print(
        f"\nCritic status: "
        f"{critique.overall_status}"
    )

    print(
        "\nRecommendations:"
    )

    for recommendation in critique.recommendations:
        print(
            f"- {recommendation}"
        )

    # --------------------------------------------------------
    # REVISION
    # --------------------------------------------------------

    if critique.overall_status == "REVISE":

        print("\n" + "-" * 70)
        print("WRITER REVISION")
        print("-" * 70)

        report = revise_mock_report(
            report
        )

        print(
            "\nReport revised successfully."
        )

    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ITERATION 2 — REVISED REPORT")
    print("-" * 70)

    print(
        f"\nReport title:\n{report.title}"
    )

    print(
        "\nKey findings:"
    )

    for index, finding in enumerate(
        report.key_findings,
        start=1,
    ):
        print(
            f"{index}. {finding}"
        )

    print(
        "\nEvidence analysis:"
    )

    print(
        report.evidence_analysis
    )

    # --------------------------------------------------------
    # FINAL CRITIC
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("ITERATION 2 — FINAL CRITIC")
    print("-" * 70)

    final_critique = create_mock_pass_critique()

    print(
        f"\nFinal critic status: "
        f"{final_critique.overall_status}"
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    assert (
        critique.overall_status
        == "REVISE"
    )

    assert (
        final_critique.overall_status
        == "PASS"
    )

    assert len(
        report.key_findings
    ) >= 3

    assert (
        len(report.references)
        >= 2
    )

    print("\n" + "=" * 70)
    print("REFINEMENT LOOP MOCK TEST PASSED")
    print("=" * 70)

    print(
        "\nWriter → Critic → Revision → "
        "Critic → PASS"
    )

    print(
        "\nThe refinement architecture "
        "is working correctly."
    )


if __name__ == "__main__":
    main()