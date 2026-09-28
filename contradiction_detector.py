from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (GEMINI_MODEL, GEMINI_TEMPERATURE,)
from schemas import Contradiction

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    max_retries=0,
    timeout=30,
)

contradiction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research contradiction detection agent.

Your task is to identify meaningful contradictions between
claims or sources in the supplied research evidence.

Rules:

1. Use ONLY the supplied evidence.
2. Do not invent facts or sources.
3. Ignore minor wording differences.
4. Identify contradictions involving facts, statistics,
   conclusions, dates, measurements, or other substantive claims.
5. If there is no meaningful contradiction, return
   NO_CONTRADICTION.
6. If a contradiction exists, identify the conflicting claims
   and the relevant source URLs.
7. Explain the contradiction clearly.
"""
    ),
    (
        "human",
        """
Research Topic:
{topic}

Research Evidence:
{evidence}

Analyze the evidence for meaningful contradictions.
"""
    )
])

def detect_contradiction(topic: str, evidence: str):
    chain = (contradiction_prompt| llm.with_structured_output(Contradiction))
    try:
        result = chain.invoke({
            "topic": topic,
            "evidence": evidence[:15000],
        })
        return result
    except Exception as error:
        if "NO_CONTRADICTION" in str(error).upper():
            return None
        raise

if __name__ == "__main__":
    print("Contradiction detector loaded successfully.")