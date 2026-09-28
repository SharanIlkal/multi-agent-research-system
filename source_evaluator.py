from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)
from schemas import SourceEvaluation

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=GEMINI_TEMPERATURE,
    max_retries=0,
    timeout=30,
)

source_evaluator_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research source evaluator.

Your job is to evaluate the quality of a web source used
in a research project.

Evaluate the source using these dimensions:

1. Relevance
   - Does the source directly address the research topic?

2. Authority
   - Is the publisher trustworthy?
   - Is the author or organization identifiable?
   - Is it an official, academic, government, professional,
     or otherwise credible source?

3. Recency
   - Is the information recent enough for the research topic?

4. Evidence Quality
   - Does the source provide actual evidence, data,
     references, methodology, or concrete information?

Do NOT invent information that is not present.

Use only the information supplied about the source.

Scores must be between 0 and 1.

Return ONLY the structured SourceEvaluation object.
"""
    ),
    (
        "human",
        """
Research Topic:
{topic}

Source Title:
{title}

Source URL:
{url}

Source Content:
{content}

Evaluate this source.
"""
    )
])

source_evaluator_chain = (source_evaluator_prompt| llm.with_structured_output(SourceEvaluation))

def evaluate_source(
    topic: str,
    title: str,
    url: str,
    content: str
) -> SourceEvaluation:
    result = source_evaluator_chain.invoke({
        "topic": topic,
        "title": title,
        "url": url,
        "content": content[:6000],
    })
    return result

if __name__ == "__main__":
    print("Source evaluator loaded successfully.")