from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from schemas import SearchResult
from search_service import search_web
DEFAULT_MAX_WORKERS = 3

def parallel_search(
    queries: List[str],
    max_results_per_query: int = 5,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> List[SearchResult]:
    """
    Execute multiple search queries concurrently.
    Results from all queries are merged and deduplicated.
    """
    if not queries:
        return []

    clean_queries = [
        query.strip()
        for query in queries
        if query and query.strip()
    ]

    if not clean_queries:
        return []

    max_workers = min(
        max_workers,
        len(clean_queries),
    )
    all_results: List[SearchResult] = []
    print("\n" + "=" * 70)
    print("PARALLEL RESEARCH SEARCH")
    print("=" * 70)
    print(f"\nQueries: {len(clean_queries)}")
    print(f"Workers: {max_workers}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_query = {
            executor.submit(
                search_web,
                query,
                max_results_per_query,
            ): query
            for query in clean_queries
        }

        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                results = future.result()
                print(
                    f"\nCompleted query:"
                    f"\n{query}"
                )
                print(f"Results: {len(results)}")
                all_results.extend(results)
            except Exception as exc:
                print(f"\nSearch failed:" f"\n{query}")
                print(f"Error: {exc}")
    return deduplicate_results(all_results)


def deduplicate_results(results: List[SearchResult],) -> List[SearchResult]:
    """
    Remove duplicate URLs while preserving
    the first occurrence.
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


def print_parallel_results(results: List[SearchResult],):
    print("\n" + "=" * 70)
    print("PARALLEL SEARCH RESULTS")
    print("=" * 70)
    print(
        f"\nUnique sources: "
        f"{len(results)}"
    )
    for index, result in enumerate(results, start=1,):
        print(f"\n[{index}] {result.title}")
        print(f"URL: {result.url}")
        print(
            f"Snippet: "
            f"{result.snippet[:300]}"
        )


if __name__ == "__main__":
    print("=" * 70)
    print("PARALLEL SEARCH MODULE TEST")
    print("=" * 70)
    test_queries = [
        "generative AI software development",
        "generative AI developer productivity",
        "generative AI software security risks",
    ]

    results = parallel_search(
        queries=test_queries,
        max_results_per_query=3,
        max_workers=3,
    )
    print_parallel_results(results)
    print("\nParallel search completed successfully.")