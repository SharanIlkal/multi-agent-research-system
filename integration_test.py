from search_service import search_web
from reader_agent import read_sources

TEST_QUERY = ("impact of generative AI on software development")
MAX_RESULTS = 3

def test_search():
    print("\n" + "=" * 70)
    print("INTEGRATION TEST — TAVILY SEARCH")
    print("=" * 70)
    results = search_web(
        query=TEST_QUERY,
        max_results=MAX_RESULTS,
    )

    if not results:
        raise RuntimeError("Tavily returned no search results.")

    print(f"\nSearch returned {len(results)} results.")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(f"\n[{index}] {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:300]}")
    return results

def test_reader(search_results):
    print("\n" + "=" * 70)
    print("INTEGRATION TEST — READER AGENT")
    print("=" * 70)
    sources = read_sources(
        search_results,
        max_sources=MAX_RESULTS,
    )

    if not sources:
        raise RuntimeError("Reader returned no sources.")
    print(
        f"\nReader successfully processed "
        f"{len(sources)} sources."
    )

    for index, source in enumerate(
        sources,
        start=1,
    ):

        print(f"\n[{index}] {source.title}")
        print(f"URL: {source.url}")
        print(f"Type: {source.source_type}")
        print(
            f"Content length: "
            f"{len(source.content)} characters"
        )
        print(f"Preview:")
        print(source.content[:500])
    return sources

if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# MULTI-AGENT RESEARCH SYSTEM")
    print("# INTEGRATION TEST")
    print("#" * 70)
    print(f"\nTest query:")
    print(TEST_QUERY)

    try:
        search_results = test_search()
        sources = test_reader(search_results)
        print("\n" + "=" * 70)
        print("INTEGRATION TEST PASSED")
        print("=" * 70)
        print("\nVerified:")
        print("Tavily search")
        print("SearchResult objects")
        print(" Reader Agent")
        print("ResearchSource objects")
        print("Search → Reader data flow")
        print("\nGemini-based stages were intentionally skipped.")

    except Exception as exc:
        print("\n" + "=" * 70)
        print("INTEGRATION TEST FAILED")
        print("=" * 70)
        print(f"\nError: {exc}")
        raise