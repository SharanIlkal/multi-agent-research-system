from search_service import search_web
from reader_agent import read_source
from claim_extractor import extract_claims
from evidence import build_evidence_package


def main():
    topic = "impact of generative AI on software development"

    print("=" * 70)
    print("LIVE EVIDENCE ENGINE TEST")
    print("=" * 70)

    results = search_web(
        query=topic,
        max_results=3,
    )

    if not results:
        raise RuntimeError(
            "No search results found."
        )

    sources = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\n[TEST] Reading source "
            f"{index}/{len(results)}"
        )

        try:
            source = read_source(result)

            if source.content:
                sources.append(source)
                print(
                    f"[TEST] Readable: "
                    f"{source.title}"
                )
            else:
                print(
                    "[TEST] No usable content."
                )

        except Exception as exc:
            print(
                f"[TEST] Reader failed: {exc}"
            )

    if not sources:
        raise RuntimeError(
            "No readable sources found."
        )

    claims = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        print(
            f"\n[TEST] Extracting claims "
            f"from source {index}/{len(sources)}"
        )

        try:
            result = extract_claims(
                topic=topic,
                source=source,
            )

            claims.extend(result.claims)

            print(
                f"[TEST] Extracted "
                f"{len(result.claims)} claims."
            )

        except Exception as exc:
            print(
                f"[TEST] Claim extraction failed: "
                f"{exc}"
            )

    if not claims:
        print(
            "\n" + "=" * 70
        )
        print("LIVE EVIDENCE ENGINE TEST STOPPED")
        print("=" * 70)
        print(
            "No claims were extracted because the Gemini API "
            "was unavailable."
        )
        print(
            "No offline or mock claims were used."
        )
        print(
            "Retry the test when the Gemini API is available."
        )
        return

    print(
        f"\n[TEST] Total claims: "
        f"{len(claims)}"
    )

    package = build_evidence_package(
        topic=topic,
        sources=sources,
        claims=claims,
        use_llm=True,
    )

    print("\n" + "=" * 70)
    print("LIVE EVIDENCE ENGINE TEST COMPLETE")
    print("=" * 70)

    print(
        f"Sources evaluated: "
        f"{len(package.source_evaluations)}"
    )

    print(
        f"Claims fact checked: "
        f"{len(package.fact_checks)}"
    )

    print(
        f"Contradictions: "
        f"{len(package.contradictions)}"
    )

    print(
        f"Citations: "
        f"{len(package.citations)}"
    )


if __name__ == "__main__":
    main()