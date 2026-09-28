from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_FALLBACK_MODEL,
    GEMINI_MAX_RETRIES,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)
from llm_factory import is_retryable_error
from schemas import (
    EvidencePackage,
    ResearchClaim,
    ResearchPlan,
    ResearchReport,
    ResearchSource,
)

def create_llm(model_name: str):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=GEMINI_TEMPERATURE,
        max_retries=GEMINI_MAX_RETRIES,
    )
primary_llm = create_llm(GEMINI_MODEL)
fallback_llm = create_llm(GEMINI_FALLBACK_MODEL)
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research report writer.

Your task is to create an evidence-grounded research report
from the supplied research material.

Follow these rules strictly:

1. Use only the supplied research evidence.
2. Do not invent facts, statistics, sources or citations.
3. Clearly distinguish findings from opinions and predictions.
4. Address the research question directly.
5. Include important contradictory findings.
6. Mention important research limitations.
7. Every important factual claim must be supported by the
   supplied evidence.
8. Use the supplied references.
9. Keep the report precise and professional.
10. Do not hide uncertainty.
11. If evidence is insufficient, explicitly state that.

If a previous report and critic feedback are supplied:

- Improve the previous report.
- Fix the issues identified by the critic.
- Preserve valid information from the previous report.
- Do not introduce unsupported information.
- Do not blindly follow critic feedback if it conflicts with
  the supplied evidence.

Return a structured ResearchReport.
""",
        ),
        (
            "human",
            """
RESEARCH QUESTION
=================
{topic}


RESEARCH PLAN
=============
{research_plan}


SOURCES
=======
{sources}


CLAIMS
======
{claims}


EVIDENCE PACKAGE
================
{evidence}


PREVIOUS REPORT
===============
{previous_report}


CRITIC FEEDBACK
===============
{critic_feedback}


Write the final research report.

If this is a revision, improve the previous report using the
critic feedback while remaining strictly grounded in the
evidence.
""",
        ),
    ]
)

def format_sources(sources: List[ResearchSource],) -> str:
    if not sources:
        return "No sources available."
    output = []
    for index, source in enumerate(
        sources,
        start=1,
    ):
        output.append(
            f"""
SOURCE {index}
Title: {source.title}
URL: {source.url}
Type: {source.source_type}

Content:
{source.content}
"""
        )
    return "\n".join(output)


def format_claims(claims: List[ResearchClaim],) -> str:
    if not claims:
        return "No extracted claims available."
    output = []
    for index, claim in enumerate(
        claims,
        start=1,
    ):
        output.append(
            f"""
CLAIM {index}
Claim: {claim.claim}
Source: {claim.source_title}
URL: {claim.source_url}
Evidence: {claim.evidence}
Importance: {claim.importance}
Type: {claim.claim_type}
"""
        )
    return "\n".join(output)

def format_source_evaluations(evaluations,) -> str:
    if not evaluations:
        return "No source evaluations available."
    output = []
    for index, evaluation in enumerate(
        evaluations,
        start=1,
    ):
        output.append(
            f"""
SOURCE EVALUATION {index}
Title: {evaluation.title}
URL: {evaluation.url}
Type: {evaluation.source_type}
Relevance: {evaluation.relevance_score}
Authority: {evaluation.authority_score}
Recency: {evaluation.recency_score}
Evidence Quality: {evaluation.evidence_quality_score}
Overall: {evaluation.overall_score}
Strengths:
{evaluation.strengths}
Weaknesses:
{evaluation.weaknesses}
"""
        )
    return "\n".join(output)

def format_fact_checks(fact_checks,) -> str:
    if not fact_checks:
        return "No fact checks available."
    output = []

    for index, fact_check in enumerate(
        fact_checks,
        start=1,
    ):
        output.append(
            f"""
FACT CHECK {index}
Claim: {fact_check.claim}
Status: {fact_check.status}
Confidence: {fact_check.confidence}
Explanation: {fact_check.explanation}
Supporting Sources:
{fact_check.supporting_sources}
Contradicting Sources:
{fact_check.contradicting_sources}
"""
        )
    return "\n".join(output)


def format_contradictions(contradictions,) -> str:
    if not contradictions:
        return "No contradictions identified."
    output = []
    for index, contradiction in enumerate(
        contradictions,
        start=1,
    ):
        output.append(
            f"""
CONTRADICTION {index}
Topic: {contradiction.topic}
Claim A:
{contradiction.claim_a}
Source A:
{contradiction.source_a}
Claim B:
{contradiction.claim_b}
Source B:
{contradiction.source_b}
Explanation:
{contradiction.explanation}
Severity:
{contradiction.severity}
"""
        )
    return "\n".join(output)


def format_citations(citations,) -> str:
    if not citations:
        return "No citations available."
    output = []
    for index, citation in enumerate(
        citations,
        start=1,
    ):
        output.append(
            f"""
CITATION {index}
Claim:
{citation.claim}
Source:
{citation.source_title}
URL:
{citation.source_url}
Evidence:
{citation.supporting_evidence}
"""
        )
    return "\n".join(output)

def format_evidence(evidence: EvidencePackage,) -> str:
    return f"""
SOURCE EVALUATIONS
------------------
{format_source_evaluations(evidence.source_evaluations)}
FACT CHECKS
-----------
{format_fact_checks(evidence.fact_checks)}
CONTRADICTIONS
--------------
{format_contradictions(evidence.contradictions)}
CITATIONS
---------
{format_citations(evidence.citations)}
"""

def invoke_with_fallback(
    primary_callable,
    fallback_callable,
):
    try:
        return primary_callable()
    except Exception as primary_error:
        print("\n[WRITER] Primary model failed.")
        print(f"[WRITER] {primary_error}")
        if not is_retryable_error(primary_error):
            raise
        print("\n[WRITER] Switching to fallback model:")
        print(GEMINI_FALLBACK_MODEL)
        try:
            return fallback_callable()
        except Exception as fallback_error:
            raise RuntimeError(
                "Both Gemini models failed "
                "during report generation.\n"
                f"Primary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            ) from fallback_error


def generate_report(
    topic: str,
    research_plan: ResearchPlan,
    sources: List[ResearchSource],
    claims: List[ResearchClaim],
    evidence: EvidencePackage,
    previous_report: Optional[ResearchReport] = None,
    critic_feedback: str = "",
) -> ResearchReport:
    """
    Generate a new research report or revise an existing report.
    """
    primary_chain = (writer_prompt| primary_llm.with_structured_output(ResearchReport))
    fallback_chain = (writer_prompt| fallback_llm.with_structured_output(ResearchReport))
    if previous_report:
        previous_report_text = (previous_report.model_dump_json(indent=2))

    else:
        previous_report_text = (
            "No previous report exists. "
            "Generate the initial report."
        )

    if not critic_feedback:
        critic_feedback = (
            "No critic feedback available. "
            "Generate the initial report."
        )

    inputs = {
        "topic": topic,
        "research_plan":
            research_plan.model_dump_json(indent=2),
        "sources":
            format_sources(sources),
        "claims":
            format_claims(claims),
        "evidence":
            format_evidence(evidence),
        "previous_report":
            previous_report_text,
        "critic_feedback":
            critic_feedback,
    }

    return invoke_with_fallback(
        primary_callable=lambda:
            primary_chain.invoke(inputs),

        fallback_callable=lambda:
            fallback_chain.invoke(inputs),
    )


def print_report(report: ResearchReport,):
    print("\n" + "=" * 70)
    print("RESEARCH REPORT")
    print("=" * 70)
    print(f"\nTitle:\n{report.title}")
    print(
        f"\nExecutive Summary:\n"
        f"{report.executive_summary}"
    )
    print(
        f"\nResearch Question:\n"
        f"{report.research_question}"
    )
    print("\nKey Findings:")
    for item in report.key_findings:
        print(f"- {item}")

    print("\nEvidence Analysis:")
    print(report.evidence_analysis)
    print("\nContradictory Findings:")

    for item in report.contradictory_findings:
        print(f"- {item}")

    print("\nLimitations:")
    for item in report.limitations:
        print(f"- {item}")
    print(
        f"\nConclusion:\n"
        f"{report.conclusion}"
    )
    print("\nReferences:")

    for reference in report.references:
        print(f"- {reference}")

if __name__ == "__main__":
    print("=" * 70)
    print("# RESEARCH WRITER MODULE TEST")
    print("=" * 70 )
    print("\nPrimary model:")
    print(GEMINI_MODEL)
    print("\nFallback model:")
    print(GEMINI_FALLBACK_MODEL)
    print("\nWriter prompt created successfully.")
    print("Structured ResearchReport output configured.")
    print("Revision support:")
    print("Previous report")
    print("Critic feedback")
    print("Evidence-grounded revision")
    print("\nResearch Writer loaded successfully.")
    print("\nGemini invocation intentionally skipped.")