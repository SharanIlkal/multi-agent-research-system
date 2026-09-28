from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_FALLBACK_MODEL,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)
from llm_factory import is_retryable_error
from schemas import (
    ClaimExtractionResult,
    ResearchClaim,
    ResearchSource,
)

def create_llm(model_name: str):
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=GEMINI_TEMPERATURE,
        max_retries=0,
        timeout=30,
    )

primary_llm = create_llm(GEMINI_MODEL)
fallback_llm = (
    create_llm(GEMINI_FALLBACK_MODEL)
    if GEMINI_FALLBACK_MODEL != GEMINI_MODEL
    else None
)

claim_extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research claim extraction agent.

Your task is to extract important, verifiable claims
from the supplied research source.

Rules:

1. Extract only claims supported by the provided text.
2. Do not invent information.
3. Do not add outside knowledge.
4. Preserve the meaning of the original source.
5. Prefer concrete and useful claims.
6. Extract statistics separately when appropriate.
7. Clearly distinguish facts, findings, opinions,
   predictions and recommendations.
8. Every claim must include supporting evidence copied
   or closely summarized from the provided source.
9. Do not treat navigation text, advertisements,
   unrelated website content, or metadata as claims.
10. Do not extract duplicate claims.
11. Prefer claims useful for answering the research topic.

Return structured output only.
"""
    ),
    (
        "human",
        """
Research topic:
{topic}

Source title:
{source_title}

Source URL:
{source_url}

Source type:
{source_type}

Source content:
{content}

Extract the most important research claims from this source.
"""
    ),
])

def invoke_model(chain, payload, model_name: str):
    print(
        f"[CLAIM EXTRACTOR] Sending source to Gemini "
        f"({model_name})..."
    )
    return chain.invoke(payload)

def extract_claims(topic: str, source: ResearchSource,) -> ClaimExtractionResult:
    payload = {
        "topic": topic,
        "source_title": source.title,
        "source_url": source.url,
        "source_type": source.source_type,
        "content": source.content,
    }
    primary_chain = (claim_extraction_prompt| primary_llm.with_structured_output(ClaimExtractionResult))

    try:
        result = invoke_model(
            primary_chain,
            payload,
            GEMINI_MODEL,
        )
        print("[CLAIM EXTRACTOR] Gemini claim extraction completed.")
        return result

    except Exception as primary_error:
        print("[CLAIM EXTRACTOR] Primary model failed.")
        print(f"[CLAIM EXTRACTOR] {primary_error}")
        if not is_retryable_error(primary_error):
            raise
        if fallback_llm is None:
            raise RuntimeError(
                "Gemini claim extraction failed and no distinct "
                "fallback model is configured."
            ) from primary_error

        print("[CLAIM EXTRACTOR] Switching to fallback model:")
        print(GEMINI_FALLBACK_MODEL)
        fallback_chain = (claim_extraction_prompt| fallback_llm.with_structured_output(ClaimExtractionResult)
        )

        try:
            result = invoke_model(
                fallback_chain,
                payload,
                GEMINI_FALLBACK_MODEL,
            )
            print("[CLAIM EXTRACTOR] Gemini fallback extraction completed.")
            return result

        except Exception as fallback_error:
            raise RuntimeError(
                "Both Gemini models failed during claim extraction.\n"
                f"Primary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            ) from fallback_error

def extract_claims_from_sources(
    topic: str,
    sources: List[ResearchSource],
    max_sources: int = 5,
) -> List[ResearchClaim]:
    all_claims = []
    selected_sources = sources[:max_sources]
    print("\n[CLAIM EXTRACTOR] " f"Processing {len(selected_sources)} sources.")
    for index, source in enumerate(selected_sources, start=1,):
        print(f"\n[CLAIM EXTRACTOR] " f"Source {index}/{len(selected_sources)}")
        print(f"Title: {source.title}")
        if not source.content:
            print("[CLAIM EXTRACTOR] Skipping empty source.")
            continue

        try:
            result = extract_claims(
                topic=topic,
                source=source,
            )
            claims = result.claims
            all_claims.extend(claims)
            print("[CLAIM EXTRACTOR] " f"Extracted {len(claims)} claims.")
        except Exception as exc:
            print("[CLAIM EXTRACTOR] " f"Failed: {exc}")

    print("\n[CLAIM EXTRACTOR] " f"Total claims: {len(all_claims)}")
    return all_claims

def print_claims(claims: List[ResearchClaim],):
    print("\n" + "=" * 70)
    print(f"EXTRACTED CLAIMS: {len(claims)}")
    print("=" * 70)
    for index, claim in enumerate(claims, start=1,):
        print(f"\n[{index}] {claim.claim}")
        print(f"Type: {claim.claim_type}")
        print(f"Importance: {claim.importance}")
        print(f"Source: {claim.source_title}")
        print(f"URL: {claim.source_url}")
        print(f"Evidence: {claim.evidence}")

if __name__ == "__main__":
    print("Claim extractor loaded successfully.")