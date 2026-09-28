from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import MAX_EVIDENCE_LENGTH
from llm_factory import get_fallback_llm, get_primary_llm, invoke_with_fallback
from schemas import Citation, Contradiction, EvidencePackage, FactCheck, ResearchClaim, ResearchSource, SourceEvaluation

class EvidenceAnalysis(BaseModel):
    source_evaluations: List[SourceEvaluation] = Field(default_factory=list)
    fact_checks: List[FactCheck] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)

evidence_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are the Evidence Engine of an autonomous AI research system.
Analyze only the supplied sources and extracted claims.
Return structured output only.
For every source evaluate relevance, authority, recency, evidence quality and overall quality with scores from 0 to 1.
For every claim determine SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED or UNVERIFIED, with confidence and evidence-based reasoning.
Identify substantive contradictions between claims or sources.
Map important claims to supporting sources. Every citation URL must appear in the supplied sources.
Do not use outside knowledge or invent authors, dates, sources, URLs, evidence or methodology.
"""),
    ("human", """
Research Topic:
{topic}

Research Sources:
{sources}

Extracted Claims:
{claims}

Perform the complete Evidence Engine analysis.
""")
])


def build_evidence_text(sources: List[ResearchSource], claims: List[ResearchClaim]) -> tuple[str, str]:
    source_parts = []
    for index, source in enumerate(sources, 1):
        source_parts.append(
            f"SOURCE {index}\nTitle: {source.title}\nURL: {source.url}\nType: {source.source_type}\nContent:\n{source.content}"
        )
    claim_parts = []
    for index, claim in enumerate(claims, 1):
        claim_parts.append(
            f"CLAIM {index}\nClaim: {claim.claim}\nType: {claim.claim_type}\nImportance: {claim.importance}\nSource: {claim.source_title}\nURL: {claim.source_url}\nEvidence: {claim.evidence}"
        )
    sources_text = "\n\n".join(source_parts)
    claims_text = "\n\n".join(claim_parts)
    if len(sources_text) + len(claims_text) > MAX_EVIDENCE_LENGTH:
        remaining = max(1000, MAX_EVIDENCE_LENGTH - len(claims_text))
        sources_text = sources_text[:remaining]
        claims_text = claims_text[:MAX_EVIDENCE_LENGTH - len(sources_text)]
    return sources_text, claims_text


def build_evidence_package(topic: str, sources: List[ResearchSource], claims: List[ResearchClaim]) -> EvidencePackage:
    if not sources:
        raise ValueError("Evidence Engine requires at least one research source.")
    if not claims:
        raise ValueError("Evidence Engine requires at least one extracted claim.")
    sources_text, claims_text = build_evidence_text(sources, claims)
    primary = get_primary_llm().with_structured_output(EvidenceAnalysis)
    fallback = get_fallback_llm().with_structured_output(EvidenceAnalysis)
    result = invoke_with_fallback(
        primary_callable=lambda: (evidence_prompt | primary).invoke({"topic": topic, "sources": sources_text, "claims": claims_text}),
        fallback_callable=lambda: (evidence_prompt | fallback).invoke({"topic": topic, "sources": sources_text, "claims": claims_text}),
    )
    return EvidencePackage(
        source_evaluations=result.source_evaluations,
        fact_checks=result.fact_checks,
        contradictions=result.contradictions,
        citations=result.citations,
    )


if __name__ == "__main__":
    print("Evidence Engine loaded successfully.")
