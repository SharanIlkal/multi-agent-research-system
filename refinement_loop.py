from typing import List
from schemas import (
    EvidencePackage,
    ResearchClaim,
    ResearchCritique,
    ResearchPlan,
    ResearchReport,
    ResearchSource,
)
from writer_agent import generate_report
from critic_agent import critique_report

DEFAULT_MAX_ITERATIONS = 3

def format_critique_feedback(critique: ResearchCritique,) -> str:
    """
    Convert structured critic output into explicit
    writer instructions.
    """
    sections = []
    sections.append(f"Overall status: {critique.overall_status}")
    if critique.factual_issues:
        sections.append("\nFactual issues:")
        for issue in critique.factual_issues:
            sections.append(f"- {issue}")

    if critique.unsupported_claims:
        sections.append("\nUnsupported claims:")
        for issue in critique.unsupported_claims:
            sections.append(f"- {issue}")

    if critique.missing_citations:
        sections.append("\nMissing citations:")

        for issue in critique.missing_citations:
            sections.append(f"- {issue}")

    if critique.contradiction_issues:
        sections.append("\nContradiction issues:")

        for issue in critique.contradiction_issues:
            sections.append(f"- {issue}")

    if critique.coverage_issues:
        sections.append("\nCoverage issues:")

        for issue in critique.coverage_issues:
            sections.append(f"- {issue}")

    if critique.clarity_issues:
        sections.append("\nClarity issues:")

        for issue in critique.clarity_issues:
            sections.append(f"- {issue}")

    if critique.recommendations:
        sections.append("\nRecommendations:")

        for recommendation in critique.recommendations:
            sections.append(f"- {recommendation}")
    return "\n".join(sections)

def revise_report(
    topic: str,
    research_plan: ResearchPlan | None,
    sources: List[ResearchSource],
    claims: List[ResearchClaim],
    evidence: EvidencePackage,
    previous_report: ResearchReport,
    critic_feedback: str,
) -> ResearchReport:
    """
    Generate a revised report using the previous report
    and structured critic feedback.
    """
    print("\n[REFINEMENT] Generating revised report...")
    return generate_report(
        topic=topic,
        research_plan=research_plan,
        sources=sources,
        claims=claims,
        evidence=evidence,
        previous_report=previous_report,
        critic_feedback=critic_feedback,
    )


def refine_report(
    topic: str,
    research_plan: ResearchPlan | None,
    sources: List[ResearchSource],
    claims: List[ResearchClaim],
    evidence: EvidencePackage,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> ResearchReport:

    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1.")

    print("\n" + "=" * 70)
    print("RESEARCH REFINEMENT LOOP")
    print("=" * 70)
    print("\n[REFINEMENT] Generating initial report...")
    report = generate_report(
        topic=topic,
        research_plan=research_plan,
        sources=sources,
        claims=claims,
        evidence=evidence,
    )

    for iteration in range(1,max_iterations + 1,):
        print("\n" + "-" * 70)
        print(
            f"REFINEMENT ITERATION "
            f"{iteration}/{max_iterations}"
        )
        print("-" * 70)
        print("\n[REFINEMENT] Running Research Critic...")

        critique = critique_report(
            topic=topic,
            report=report,
            evidence=evidence,
        )
        print(
            f"[REFINEMENT] Critic status: "
            f"{critique.overall_status}"
        )

        if critique.overall_status == "PASS":
            print("\n[REFINEMENT] " "Research report approved.")
            print(
                f"[REFINEMENT] Completed after "
                f"{iteration} critic iteration(s)."
            )
            return report
        if iteration == max_iterations:
            print("\n[REFINEMENT] Maximum iterations reached.")
            print("[REFINEMENT] Returning the latest report.")
            return report


        critic_feedback = format_critique_feedback(critique)
        print("\n[REFINEMENT] Critic feedback:")
        print(critic_feedback)
        report = revise_report(
            topic=topic,
            research_plan=research_plan,
            sources=sources,
            claims=claims,
            evidence=evidence,
            previous_report=report,
            critic_feedback=critic_feedback,
        )
        print("\n[REFINEMENT] Report revision completed.")
    return report

def get_refinement_status(
    critique: ResearchCritique,
    iteration: int,
    max_iterations: int,
) -> str:
    """
    Return a human-readable refinement status.
    """
    if critique.overall_status == "PASS":
        return ("approved")

    if iteration >= max_iterations:
        return ("maximum_iterations_reached")
    return ("revision_required")


if __name__ == "__main__":
    print("=" * 70)
    print("REFINEMENT LOOP MODULE TEST")
    print("=" * 70)
    print(
        f"\nDefault maximum iterations: "
        f"{DEFAULT_MAX_ITERATIONS}"
    )

    print("\nCritique formatter loaded successfully.")
    print("Report revision function loaded successfully.")
    print("Live refinement loop loaded successfully.")
    print("\nGemini invocation intentionally skipped.")
    print("\nRefinement loop module test passed.")