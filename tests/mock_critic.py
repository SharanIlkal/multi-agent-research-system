from schemas import ResearchCritique


def create_mock_critique(
    report_text: str = "",
) -> ResearchCritique:

    return ResearchCritique(
        overall_status="REVISE",

        factual_issues=[],

        unsupported_claims=[
            (
                "The report should explicitly connect "
                "each key finding to its supporting citation."
            )
        ],

        missing_citations=[
            (
                "The productivity finding should include "
                "an explicit source reference."
            )
        ],

        contradiction_issues=[],

        coverage_issues=[
            (
                "The report could provide more detail "
                "about the relationship between "
                "productivity benefits and security risks."
            )
        ],

        clarity_issues=[],

        recommendations=[
            (
                "Add explicit citations to the key findings."
            ),
            (
                "Strengthen the evidence analysis."
            ),
            (
                "Explain the balance between benefits "
                "and risks more clearly."
            ),
        ],
    )


if __name__ == "__main__":

    print("=" * 70)
    print("MOCK RESEARCH CRITIC TEST")
    print("=" * 70)

    critique = create_mock_critique()

    print(
        f"\nOverall Status: "
        f"{critique.overall_status}"
    )

    print(
        "\nFactual Issues:"
    )

    for issue in critique.factual_issues:
        print(f"- {issue}")

    print(
        "\nUnsupported Claims:"
    )

    for issue in critique.unsupported_claims:
        print(f"- {issue}")

    print(
        "\nMissing Citations:"
    )

    for issue in critique.missing_citations:
        print(f"- {issue}")

    print(
        "\nContradiction Issues:"
    )

    for issue in critique.contradiction_issues:
        print(f"- {issue}")

    print(
        "\nCoverage Issues:"
    )

    for issue in critique.coverage_issues:
        print(f"- {issue}")

    print(
        "\nRecommendations:"
    )

    for recommendation in critique.recommendations:
        print(
            f"- {recommendation}"
        )

    print(
        "\nMock ResearchCritique created successfully."
    )