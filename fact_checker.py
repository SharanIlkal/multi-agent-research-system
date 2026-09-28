from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (GEMINI_MODEL,GEMINI_TEMPERATURE,)
from schemas import FactCheck

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    max_retries=0,
    timeout=30,
)

fact_checker_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research fact-checking agent.

Your job is to verify a factual claim using ONLY the
research evidence supplied to you.

Possible verification statuses:

SUPPORTED
The evidence directly supports the claim.

PARTIALLY_SUPPORTED
The evidence supports only part of the claim or
provides qualified or limited support.

CONTRADICTED
The evidence directly conflicts with the claim.

UNVERIFIED
The supplied evidence is insufficient to verify
or contradict the claim.

Rules:

1. Do not use information that is not present in the evidence.
2. Do not invent sources.
3. Do not assume that a claim is true merely because it sounds reasonable.
4. Distinguish direct evidence from inference.
5. If sources disagree, mention the disagreement.
6. Provide the URLs of supporting sources.
7. Provide the URLs of contradicting sources when applicable.
8. Confidence must be between 0 and 1.

Return ONLY the structured FactCheck object.
"""
    ),
    (
        "human",
        """
Research Topic:
{topic}

Claim to Verify:
{claim}

Research Evidence:
{evidence}

Verify the claim against the supplied evidence.
"""
    )
])

fact_checker_chain = (
    fact_checker_prompt
    | llm.with_structured_output(FactCheck)
)

def fact_check_claim(
    topic: str,
    claim: str,
    evidence: str
) -> FactCheck:
    result = fact_checker_chain.invoke({
        "topic": topic,
        "claim": claim,
        "evidence": evidence[:12000],
    })
    return result

if __name__ == "__main__":
    print("Fact checker loaded successfully.")