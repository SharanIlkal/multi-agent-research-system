import os
from typing import List
from dotenv import load_dotenv
from tavily import TavilyClient
from config import TAVILY_MAX_RESULTS
from schemas import SearchResult

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(
    query: str,
    max_results: int | None = None,
) -> List[SearchResult]:
    """
    Search the web directly using Tavily.
    Gemini is NOT used here.
    Returns:
        List[SearchResult]
    """

    if not query or not query.strip():
        return []
    limit = max_results or TAVILY_MAX_RESULTS
    try:
        response = tavily.search(
            query=query.strip(),
            max_results=limit,
            search_depth="advanced",
        )
        results = []
        for item in response.get("results", []):
            title = item.get("title", "Untitled Source",)
            url = item.get("url", "",)
            content = item.get("content", "",)
            if not url:
                continue
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=content[:1000],
                )
            )

        return _deduplicate_results(results)
    except Exception as exc:
        raise RuntimeError(f"Tavily search failed: {exc}") from exc


def search_multiple_queries(
    queries: List[str],
    max_results_per_query: int | None = None,
) -> List[SearchResult]:
    """
    Execute multiple Tavily searches and combine the results.
    Duplicate URLs are removed.
    """
    all_results = []
    for index, query in enumerate(queries, start=1,):
        if not query.strip():
            continue

        print(
            f"\nSearching query "
            f"{index}/{len(queries)}:"
        )
        print(query)
        try:
            results = search_web(
                query=query,
                max_results=max_results_per_query,
            )
            print(f"Found {len(results)} sources.")
            all_results.extend(results)
        except Exception as exc:
            print(f"Search failed: {exc}")
    return _deduplicate_results(all_results)

def _deduplicate_results(results: List[SearchResult],) -> List[SearchResult]:
    """
    Remove duplicate URLs while preserving order.
    """
    unique_results = []
    seen_urls = set()
    for result in results:
        normalized_url = (
            result.url
            .strip()
            .rstrip("/")
            .lower()
        )

        if not normalized_url:
            continue

        if normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)
        unique_results.append(result)
    return unique_results

def print_search_results(results: List[SearchResult],):
    """
    Print search results in a readable format.
    """
    print("\n" + "=" * 70)
    print(f"SEARCH RESULTS: {len(results)}")
    print("=" * 70)
    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"\n[{index}] {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:500]}")


if __name__ == "__main__":
    print("Tavily Search Service")
    query = (
        "impact of generative AI "
        "on software development"
    )
    results = search_web(
        query=query,
        max_results=5,
    )
    print_search_results(results)