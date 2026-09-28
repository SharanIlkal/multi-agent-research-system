from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)
from schemas import Citation

class CitationMapping(BaseModel):
    citations: List[Citation] = Field(default_factory=list)

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    max_retries=0,
    timeout=30,
)

citation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research citation mapping agent.

Your task is to map important research claims to the sources
that support them.

Rules:

1. Use ONLY the supplied research evidence.
2. Do not invent sources or URLs.
3. Every citation must correspond to a source present in the evidence.
4. Prefer direct evidence over weak or indirect evidence.
5. Include the source URL.
6. Clearly identify the claim supported by each citation.
7. Do not create citations when the evidence does not support them.

Return ONLY the structured CitationMapping object.
"""
    ),
    (
        "human",
        """
Research Topic:
{topic}

Research Evidence:
{evidence}

Create citation mappings for the important claims.
"""
    )
])

citation_chain = (citation_prompt| llm.with_structured_output(CitationMapping))

def map_citations(topic: str, evidence: str) -> List[Citation]:
    result = citation_chain.invoke({
        "topic": topic,
        "evidence": evidence[:15000],
    })
    return result.citations

if __name__ == "__main__":
    print("Citation mapper loaded successfully.")