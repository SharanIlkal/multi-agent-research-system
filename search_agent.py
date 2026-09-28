from typing import Any
from langchain.agents import create_agent
from agents import (
    create_agent_llm,
    invoke_with_model_fallback,
)
from config import (
    GEMINI_FALLBACK_MODEL,
    GEMINI_MODEL,
)
from tools import web_search

def build_search_agent(model=None):
    """
    Build the Search Agent.
    The Search Agent uses Tavily to discover relevant
    web sources.
    """
    return create_agent(
        model=model or create_agent_llm(GEMINI_MODEL),
        tools=[web_search,],
    )


def run_search_agent(
    query: str,
) -> Any:
    """
    Run the Search Agent with automatic Gemini fallback.

    Primary:
        gemini-3.5-flash

    Fallback:
        gemini-3.6-flash
    """

    primary_agent = build_search_agent(create_agent_llm(GEMINI_MODEL))
    fallback_agent = build_search_agent(create_agent_llm(GEMINI_FALLBACK_MODEL))
    prompt = f"""
Search the web for reliable and recent information about:

{query}

Use the web search tool to find relevant sources.

Return the most useful sources with:

1. Source title
2. URL
3. Key finding
4. Why the source is relevant

Prefer:
- Academic research
- Government sources
- Official documentation
- Research organizations
- Industry reports
- Reputable news organizations

Avoid low-quality or irrelevant sources.
"""
    return invoke_with_model_fallback(
        primary_callable=lambda: primary_agent.invoke(
            {
                "messages": [("user", prompt)]
            }
        ),
        fallback_callable=lambda: fallback_agent.invoke(
            {
                "messages": [("user", prompt)]
            }
        ),
    )


if __name__ == "__main__":
    print("Search Agent test")
    query = (
        "impact of generative AI "
        "on software developer productivity"
    )
    result = run_search_agent(query)
    print("\nSearch Agent Result:")
    print("=" * 70)
    messages = result.get("messages", [],)
    if messages:
        print(messages[-1].content)
    else:
        print("No response returned.")