from search_service import search_web
from reader_agent import read_sources
from claim_extractor import extract_claims
from evidence import build_evidence_package


# ============================================================
# CONFIGURATION
# ============================================================

TEST_QUERY = (
    "impact of generative AI on software development"
)

MAX_RESULTS = 1


# ============================================================
# STEP 1 — SEARCH
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
# STEP 2 — READER
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
# STEP 3 — CLAIM EXTRACTION
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

        result = extract_claims(
            TEST_QUERY,
            source,
        )

        claims = result.claims

        all_claims.extend(
            claims
        )

        print(
            f"Extracted "
            f"{len(claims)} claims."
        )

    if not all_claims:

        raise RuntimeError(
            "No claims were extracted."
        )

    print(
        f"\nTotal claims: "
        f"{len(all_claims)}"
    )

    return all_claims


# ============================================================
# STEP 4 — EVIDENCE ENGINE
# ============================================================

def run_evidence_engine(
    sources,
    claims,
):

    print("\n" + "=" * 70)
    print("STEP 4 — EVIDENCE ENGINE")
    print("=" * 70)

    print(
        "\nBuilding evidence package..."
    )

    evidence = build_evidence_package(
        topic=TEST_QUERY,
        sources=sources,
        claims=claims,
    )

    if evidence is None:

        raise RuntimeError(
            "Evidence engine returned None."
        )

    print(
        "\nEvidence package created successfully."
    )

    print(
        f"\nSource evaluations: "
        f"{len(evidence.source_evaluations)}"
    )

    print(
        f"Fact checks: "
        f"{len(evidence.fact_checks)}"
    )

    print(
        f"Contradictions: "
        f"{len(evidence.contradictions)}"
    )

    print(
        f"Citations: "
        f"{len(evidence.citations)}"
    )

    return evidence


# ============================================================
# DISPLAY EVIDENCE
# ============================================================

def display_evidence(
    evidence,
):

    print("\n" + "=" * 70)
    print("EVIDENCE ENGINE OUTPUT")
    print("=" * 70)

    # --------------------------------------------------------
    # Source evaluations
    # --------------------------------------------------------

    print(
        "\nSOURCE EVALUATIONS"
    )

    for index, evaluation in enumerate(
        evidence.source_evaluations,
        start=1,
    ):

        print(
            f"\n[{index}] {evaluation.title}"
        )

        print(
            f"Type: {evaluation.source_type}"
        )

        print(
            f"Relevance: "
            f"{evaluation.relevance_score}"
        )

        print(
            f"Authority: "
            f"{evaluation.authority_score}"
        )

        print(
            f"Recency: "
            f"{evaluation.recency_score}"
        )

        print(
            f"Evidence quality: "
            f"{evaluation.evidence_quality_score}"
        )

        print(
            f"Overall: "
            f"{evaluation.overall_score}"
        )

    # --------------------------------------------------------
    # Fact checks
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "FACT CHECKS"
    )

    for index, fact_check in enumerate(
        evidence.fact_checks,
        start=1,
    ):

        print(
            f"\n[{index}] "
            f"{fact_check.claim}"
        )

        print(
            f"Status: "
            f"{fact_check.status}"
        )

        print(
            f"Confidence: "
            f"{fact_check.confidence}"
        )

        print(
            f"Explanation: "
            f"{fact_check.explanation}"
        )

    # --------------------------------------------------------
    # Contradictions
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "CONTRADICTIONS"
    )

    if not evidence.contradictions:

        print(
            "No contradictions detected."
        )

    else:

        for index, contradiction in enumerate(
            evidence.contradictions,
            start=1,
        ):

            print(
                f"\n[{index}] "
                f"{contradiction.topic}"
            )

            print(
                f"Severity: "
                f"{contradiction.severity}"
            )

            print(
                f"Explanation: "
                f"{contradiction.explanation}"
            )

    # --------------------------------------------------------
    # Citations
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "CITATIONS"
    )

    for index, citation in enumerate(
        evidence.citations,
        start=1,
    ):

        print(
            f"\n[{index}] "
            f"{citation.claim}"
        )

        print(
            f"Source: "
            f"{citation.source_title}"
        )

        print(
            f"URL: "
            f"{citation.source_url}"
        )

        print(
            f"Evidence: "
            f"{citation.supporting_evidence[:300]}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "#" * 70
    )

    print(
        "# SEARCH → READER → CLAIMS → EVIDENCE"
    )

    print(
        "#" * 70
    )

    try:

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        results = run_search()

        # ----------------------------------------------------
        # Read
        # ----------------------------------------------------

        sources = run_reader(
            results
        )

        # ----------------------------------------------------
        # Claims
        # ----------------------------------------------------

        claims = run_claim_extraction(
            sources
        )

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        evidence = run_evidence_engine(
            sources,
            claims,
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        display_evidence(
            evidence
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "EVIDENCE INTEGRATION TEST PASSED"
        )

        print(
            "=" * 70
        )

        print(
            "\nVerified:"
        )

        print(
            "✓ Tavily Search"
        )

        print(
            "✓ Reader Agent"
        )

        print(
            "✓ Gemini Claim Extraction"
        )

        print(
            "✓ Source Evaluation"
        )

        print(
            "✓ Fact Checking"
        )

        print(
            "✓ Contradiction Detection"
        )

        print(
            "✓ Citation Mapping"
        )

        print(
            "✓ EvidencePackage"
        )

    except Exception as exc:

        print(
            "\n" + "=" * 70
        )

        print(
            "EVIDENCE INTEGRATION TEST FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"\nError: {exc}"
        )

        raise