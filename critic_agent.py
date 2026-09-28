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
    ResearchCritique,
    ResearchReport,
)

def create_llm(model_name: str):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=GEMINI_TEMPERATURE,
        max_retries=GEMINI_MAX_RETRIES,
    )


primary_llm = create_llm(GEMINI_MODEL)
fallback_llm = create_llm(GEMINI_FALLBACK_MODEL)
critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a rigorous research quality-control agent.

Your job is to review a research report against the
supplied evidence.

Do NOT rewrite the report.

Instead, identify problems that should be fixed before
the report is considered final.

Evaluate:

1. Factual accuracy
2. Unsupported claims
3. Missing citations
4. Contradictions
5. Research-question coverage
6. Clarity and precision
7. Whether conclusions are supported by evidence

Rules:

- Use ONLY the supplied research material.
- Do not introduce outside facts.
- Do not invent problems that are not supported by
  the supplied material.
- If the report is adequately supported, return PASS.
- If meaningful issues require correction, return REVISE.
- Recommendations must be concrete and actionable.

Return structured output only.
""",
        ),
        (
            "human",
            """
RESEARCH QUESTION
-----------------
{topic}


RESEARCH REPORT
---------------
{report}


SOURCE EVALUATIONS
------------------
{source_evaluations}


FACT CHECKS
-----------
{fact_checks}


CONTRADICTIONS
--------------
{contradictions}


CITATIONS
---------
{citations}


Review the report against the evidence and return a
structured research critique.
""",
        ),
    ]
)


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
Source Type: {evaluation.source_type}
Relevance: {evaluation.relevance_score}
Authority: {evaluation.authority_score}
Recency: {evaluation.recency_score}
Evidence Quality: {evaluation.evidence_quality_score}
Overall Score: {evaluation.overall_score}

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
    for index, check in enumerate(
        fact_checks,
        start=1,
    ):

        output.append(
            f"""
FACT CHECK {index}
Claim: {check.claim}
Status: {check.status}
Confidence: {check.confidence}
Explanation: {check.explanation}
Supporting Sources:
{check.supporting_sources}
Contradicting Sources:
{check.contradicting_sources}
"""
        )
    return "\n".join(output)

def format_contradictions(
    contradictions,
) -> str:
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
Claim A:{contradiction.claim_a}
Source A:{contradiction.source_a}
Claim B:{contradiction.claim_b}
Source B:{contradiction.source_b}
Explanation:{contradiction.explanation}
Severity:{contradiction.severity}
"""
        )
    return "\n".join(output)


def format_citations(citations,) -> str:
    if not citations:
        return "No citations available."
    output = []

    for index, citation in enumerate(citations, start=1,):
        output.append(
            f"""
CITATION {index}
Claim:{citation.claim}
Source:{citation.source_title}
URL:{citation.source_url}
Evidence:{citation.supporting_evidence}
"""
        )
    return "\n".join(output)

def invoke_with_fallback(
    primary_callable,
    fallback_callable,
):
    """
    Execute the primary critic model and use the fallback
    model when the failure is retryable.
    """

    try:
        return primary_callable()
    except Exception as primary_error:
        print( "\n[CRITIC] Primary model failed.")
        print(f"[CRITIC] {primary_error}")
        if not is_retryable_error(primary_error):
            raise
        print("\n[CRITIC] Switching to fallback model:")
        print(GEMINI_FALLBACK_MODEL)
        try:
            return fallback_callable()
        except Exception as fallback_error:
            raise RuntimeError(
                "Both Gemini models failed "
                "during report criticism.\n"
                f"Primary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            ) from fallback_error

def critique_report(
    topic: str,
    report: ResearchReport,
    evidence: EvidencePackage,
) -> ResearchCritique:
    """
    Critique a research report against the evidence package.
    """
    primary_chain = (critic_prompt| primary_llm.with_structured_output(ResearchCritique))
    fallback_chain = (critic_prompt | fallback_llm.with_structured_output(ResearchCritique))
    inputs = {
        "topic": topic,
        "report": report.model_dump_json(indent=2),
        "source_evaluations":
            format_source_evaluations(evidence.source_evaluations),
        "fact_checks":
            format_fact_checks(evidence.fact_checks),
        "contradictions":
            format_contradictions(evidence.contradictions),
        "citations":
            format_citations(evidence.citations),
    }

    return invoke_with_fallback(
        primary_callable=lambda:
            primary_chain.invoke(inputs),

        fallback_callable=lambda:
            fallback_chain.invoke(inputs),
    )

def print_critique(critique: ResearchCritique,):
    """
    Display the research critique.
    """
    print("\n" + "=" * 70)
    print("RESEARCH CRITIQUE")
    print("=" * 70)
    print(
        f"\nStatus: "
        f"{critique.overall_status}"
    )
    print("\nFactual Issues:")
    for item in critique.factual_issues:
        print(f"- {item}")
    print("\nUnsupported Claims:")
    for item in critique.unsupported_claims:
        print(f"- {item}")
    print("\nMissing Citations:")
    for item in critique.missing_citations:
        print(f"- {item}")
    print("\nContradiction Issues:")
    for item in critique.contradiction_issues:
        print(f"- {item}")
    print("\nCoverage Issues:")
    for item in critique.coverage_issues:
        print(f"- {item}")

    print("\nClarity Issues:")
    for item in critique.clarity_issues:
        print(f"- {item}")
    print("\nRecommendations:")
    for item in critique.recommendations:
        print(f"- {item}")

if __name__ == "__main__":
    print("=" * 70)
    print("RESEARCH CRITIC MODULE TEST")
    print("=" * 70)
    print("\nPrimary model:")
    print(GEMINI_MODEL)
    print("\nFallback model:")
    print(GEMINI_FALLBACK_MODEL)
    print("\nCritic prompt created successfully.")
    print("Structured ResearchCritique output configured.")
    print("\nResearch Critic loaded successfully.")