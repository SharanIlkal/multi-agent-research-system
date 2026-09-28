from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_FALLBACK_MODEL,
    GEMINI_MAX_RETRIES,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
)
from llm_factory import is_retryable_error
from schemas import ResearchPlan
from tools import scrape_url, web_search

load_dotenv()

def create_agent_llm(model_name: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=GEMINI_TEMPERATURE,
        max_retries=GEMINI_MAX_RETRIES,
    )
primary_llm = create_agent_llm(GEMINI_MODEL)
fallback_llm = create_agent_llm(GEMINI_FALLBACK_MODEL)

def is_agent_retryable_error(error: Exception) -> bool:
    if is_retryable_error(error):
        return True
    message = str(error).lower()
    transient_markers = (
        "unexpected_eof_while_reading",
        "unexpected eof while reading",
        "ssl error",
        "sslerror",
        "connection reset",
        "connection aborted",
        "connection broken",
        "connection refused",
        "remote disconnected",
        "read timed out",
        "timed out",
        "timeout",
        "temporarily unavailable",
        "service unavailable",
        "bad gateway",
        "gateway timeout",
        "server disconnected",
        "network is unreachable",
    )
    return any(marker in message for marker in transient_markers)

def invoke_with_model_fallback(primary_callable, fallback_callable,):
    try:
        return primary_callable()
    except Exception as primary_error:
        print("\n[AGENT LLM] Primary model failed.")
        print(f"[AGENT LLM] {primary_error}")
        if not is_agent_retryable_error(primary_error):
            raise
        print("\n[AGENT LLM] Switching to fallback model:")
        print(f"[AGENT LLM] {GEMINI_FALLBACK_MODEL}")
        try:
            return fallback_callable()
        except Exception as fallback_error:
            raise RuntimeError(
                "Both primary and fallback Gemini models failed.\n"
                f"Primary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            ) from fallback_error



supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Supervisor Agent of an autonomous research system.

Your responsibility is to analyze the user's research topic
and create a structured research plan.

The plan should:

1. Clearly define the research goal.
2. Identify the major dimensions of the topic.
3. Create 3-6 focused sub-questions.
4. Create targeted search queries.
5. Identify useful source types.

Search queries should be specific enough to retrieve useful
research rather than simply repeating the original question.

Examples of useful source types:

- Government reports
- Academic papers
- Research organizations
- Official documentation
- Industry reports
- Reputable news
- Company reports

Return ONLY the structured ResearchPlan.
""",
        ),
        (
            "human",
            """
Research Topic:

{topic}

Create the research plan.
""",
        ),
    ]
)


def create_research_plan(topic: str,) -> ResearchPlan:
    primary_chain = (supervisor_prompt | primary_llm.with_structured_output(ResearchPlan))
    fallback_chain = (supervisor_prompt | fallback_llm.with_structured_output(ResearchPlan))
    return invoke_with_model_fallback(
        primary_callable=lambda: primary_chain.invoke(
            {
                "topic": topic,
            }
        ),
        fallback_callable=lambda: fallback_chain.invoke(
            {
                "topic": topic,
            }
        ),
    )

def build_search_agent(model=None,):
    return create_agent(
        model=model or primary_llm,
        tools=[web_search,],
    )


def build_reader_agent(model=None,):
    return create_agent(
        model=model or primary_llm,
        tools=[scrape_url,],
    )


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert research writer.

Create a clear, factual and professional research report.

Use ONLY the research evidence supplied to you.

Do not invent:
- Facts
- Statistics
- Sources
- URLs

If the evidence is uncertain or conflicting,
explicitly mention the uncertainty or disagreement.

Structure the report as:

# Introduction

# Research Scope

# Key Findings

Provide at least three well-explained findings.

For each important finding, connect it to available
evidence and citations.

# Evidence and Source Analysis

Explain the quality and limitations of the evidence.

# Contradictory Evidence

Discuss meaningful disagreements between sources.

If no major contradictions were identified,
state that clearly.

# Limitations

Explain important limitations in the research.

# Conclusion

# Sources

List the relevant source titles and URLs.

Be factual, analytical and professional.
""",
        ),
        (
            "human",
            """
Research Topic:

{topic}

Research Plan:

{research_plan}

Research Evidence:

{research}

Fact Checks:

{fact_checks}

Source Evaluations:

{source_evaluations}

Contradictions:

{contradictions}

Citation Mappings:

{citations}

Write the final research report.
""",
        ),
    ]
)


def create_writer_chain():
    return writer_prompt | primary_llm | StrOutputParser()


writer_chain = create_writer_chain()

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a strict research report critic.

Evaluate the research report for:

1. Factual support
2. Source quality
3. Citation quality
4. Coverage of the research question
5. Logical consistency
6. Handling of uncertainty
7. Contradiction handling
8. Writing quality

Do not reward unsupported claims.

Return exactly this format:

Score: X/10

Strengths:
- ...
- ...
- ...

Areas to Improve:
- ...
- ...
- ...

One line verdict:
...
""",
        ),
        (
            "human",
            """
Research Report:

{report}
""",
        ),
    ]
)


def create_critic_chain():
    return critic_prompt | primary_llm | StrOutputParser()

critic_chain = create_critic_chain()

if __name__ == "__main__":
    print("Agents module loaded successfully.")
    print(f"Primary model: {GEMINI_MODEL}")
    print(f"Fallback model: {GEMINI_FALLBACK_MODEL}")
    print("Supervisor: ready")
    print("Search Agent: ready")
    print("Reader Agent: ready")
    print("Writer: ready")
    print("Critic: ready")