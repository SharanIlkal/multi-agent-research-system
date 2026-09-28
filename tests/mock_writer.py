from schemas import (
    EvidencePackage,
    ResearchClaim,
    ResearchPlan,
    ResearchReport,
    ResearchSource,
)


def create_mock_report(
    topic: str,
    research_plan: ResearchPlan | None = None,
    sources: list[ResearchSource] | None = None,
    claims: list[ResearchClaim] | None = None,
    evidence: EvidencePackage | None = None,
) -> ResearchReport:

    return ResearchReport(
        title=(
            "Impact of Generative AI "
            "on Software Development"
        ),

        executive_summary=(
            "Generative AI is influencing software "
            "development by supporting repetitive tasks, "
            "developer productivity, and software "
            "development workflows. At the same time, "
            "its adoption introduces security-related "
            "risks that require consideration."
        ),

        research_question=topic,

        key_findings=[
            (
                "Generative AI can automate repetitive "
                "software development tasks."
            ),
            (
                "Generative AI can improve developer "
                "productivity for some tasks."
            ),
            (
                "Generative AI can introduce security "
                "risks in software development."
            ),
        ],

        evidence_analysis=(
            "The available test evidence supports "
            "claims concerning automation, productivity, "
            "and security risks associated with "
            "generative AI."
        ),

        contradictory_findings=[],

        limitations=[
            (
                "This report uses deterministic mock "
                "evidence for integration testing."
            ),
            (
                "The test dataset contains a limited "
                "number of sources."
            ),
        ],

        conclusion=(
            "The test evidence indicates that "
            "generative AI can provide productivity "
            "opportunities while also introducing "
            "potential risks."
        ),

        references=[
            source.url
            for source in (sources or [])
        ],
    )

def revise_mock_report(report: ResearchReport) -> ResearchReport:
    """
    Deterministically revise the mock report.

    Simulates the Research Writer responding to Critic feedback.
    """

    revised_findings = []

    for finding in report.key_findings:
        if "[Citation:" not in finding:
            finding = finding.rstrip(".") + " [Citation: Source 1]"
        revised_findings.append(finding)

    revised_evidence_analysis = (
        report.evidence_analysis
        + "\n\nRevision: The key findings were reviewed against "
        "the available evidence and citations were added where needed."
    )

    return ResearchReport(
    research_question=report.research_question,
    title=report.title,
    executive_summary=report.executive_summary,
    key_findings=revised_findings,
    evidence_analysis=revised_evidence_analysis,
    limitations=report.limitations,
    conclusion=report.conclusion,
    references=report.references,
)


if __name__ == "__main__":
    print("=" * 70)
    print("MOCK WRITER TEST")
    print("=" * 70)

    from tests.mock_research_data import (
        TEST_TOPIC,
        create_mock_claims,
        create_mock_sources,
    )

    sources = create_mock_sources()
    claims = create_mock_claims()

    report = create_mock_report(
        topic=TEST_TOPIC,
        research_plan=None,
        sources=sources,
        claims=claims,
        evidence=None,
    )

    print(f"Initial report: {report.title}")

    revised_report = revise_mock_report(report)

    print(
        f"Revised findings: "
        f"{len(revised_report.key_findings)}"
    )

    assert revised_report is not None
    assert len(revised_report.key_findings) == len(
        report.key_findings
    )

    print("\n" + "=" * 70)
    print("MOCK WRITER TEST PASSED")
    print("=" * 70)