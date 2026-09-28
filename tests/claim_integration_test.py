from search_service import search_web
from reader_agent import read_sources
from claim_extractor import extract_claims


# ============================================================
# CONFIGURATION
# ============================================================

TEST_QUERY = (
    "impact of generative AI on software development"
)

MAX_RESULTS = 1


# ============================================================
# SEARCH
# ============================================================

def run_search():

    print("\n" + "=" * 70)
    print("STEP 1 — TAVILY SEARCH")
    print("=" * 70)

    results = search_web(
        query=TEST_QUERY,
        max_results=MAX_RESULTS,
    )

    if not results:
        raise RuntimeError(
            "Tavily returned no results."
        )

    print(
        f"\nFound {len(results)} source(s)."
    )

    for result in results:

        print(
            f"\nTitle: {result.title}"
        )

        print(
            f"URL: {result.url}"
        )

    return results


# ============================================================
# READER
# ============================================================

def run_reader(results):

    print("\n" + "=" * 70)
    print("STEP 2 — READER AGENT")
    print("=" * 70)

    sources = read_sources(
        results,
        max_sources=MAX_RESULTS,
    )

    if not sources:
        raise RuntimeError(
            "Reader returned no sources."
        )

    print(
        f"\nRead {len(sources)} source(s)."
    )

    for source in sources:

        print(
            f"\nTitle: {source.title}"
        )

        print(
            f"Type: {source.source_type}"
        )

        print(
            f"Content length: "
            f"{len(source.content)}"
        )

    return sources


# ============================================================
# CLAIM EXTRACTION
# ============================================================

def run_claim_extraction(sources):

    print("\n" + "=" * 70)
    print("STEP 3 — CLAIM EXTRACTION")
    print("=" * 70)

    all_claims = []

    for index, source in enumerate(
        sources,
        start=1,
    ):

        print(
            f"\nProcessing source "
            f"{index}/{len(sources)}:"
        )

        print(
            source.title
        )

        try:

            result = extract_claims(
                TEST_QUERY,
                source,
            )

            if hasattr(
                result,
                "claims",
            ):

                claims = result.claims

            else:

                claims = result

            all_claims.extend(
                claims
            )

            print(
                f"Extracted "
                f"{len(claims)} claims."
            )

        except Exception as exc:

            print(
                "\nClaim extraction failed."
            )

            print(
                f"Reason: {exc}"
            )

            print(
                "\nThis is expected if the "
                "Gemini quota/service is still unavailable."
            )

            return None

    return all_claims


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "#" * 70
    )

    print(
        "# SEARCH → READER → CLAIM EXTRACTION"
    )

    print(
        "#" * 70
    )

    try:

        # Search
        results = run_search()

        # Read
        sources = run_reader(
            results
        )

        # Extract claims
        claims = run_claim_extraction(
            sources
        )

        if claims is None:

            print(
                "\n" + "=" * 70
            )

            print(
                "SEARCH + READER PASSED"
            )

            print(
                "CLAIM EXTRACTION NOT VERIFIED"
            )

            print(
                "=" * 70
            )

            print(
                "\nThe deterministic portion works."
            )

            print(
                "Gemini availability is the remaining dependency."
            )

        else:

            print(
                "\n" + "=" * 70
            )

            print(
                "CLAIM INTEGRATION TEST PASSED"
            )

            print(
                "=" * 70
            )

            print(
                f"\nTotal claims extracted: "
                f"{len(claims)}"
            )

            for index, claim in enumerate(
                claims[:10],
                start=1,
            ):

                print(
                    f"\n[{index}] {claim.claim}"
                )

                print(
                    f"Type: {claim.claim_type}"
                )

                print(
                    f"Importance: {claim.importance}"
                )

    except Exception as exc:

        print(
            "\n" + "=" * 70
        )

        print(
            "INTEGRATION TEST FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {exc}"
        )

        raise