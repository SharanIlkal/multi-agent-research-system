from schemas import (
    ResearchClaim,
    ResearchSource,
)


# ============================================================
# MOCK RESEARCH DATA
# ============================================================

TEST_TOPIC = (
    "impact of generative AI on software development"
)


def create_mock_sources():
    """
    Create deterministic research sources for testing.

    These are test fixtures only. They are not intended to
    represent a complete real-world research dataset.
    """

    return [
        ResearchSource(
            title=(
                "Generative AI in Software Development: "
                "A Multiple Case Study on Process Transformation"
            ),
            url=(
                "https://aaltodoc.aalto.fi/"
                "bitstreams/3cc3575d-852b-44bc-b9ba-12fc374d1db0/"
                "download"
            ),
            content=(
                "This is a test representation of an academic "
                "source discussing the use of generative AI "
                "in software development and process "
                "transformation."
            ),
            source_type="research_paper",
        ),
        ResearchSource(
            title=(
                "Generative AI Adoption in Software Development"
            ),
            url=(
                "https://example.com/"
                "generative-ai-software-development"
            ),
            content=(
                "This test source discusses generative AI "
                "adoption, productivity, software development "
                "workflows, and potential security concerns."
            ),
            source_type="research",
        ),
    ]


def create_mock_claims():
    """
    Create deterministic research claims for testing.
    """

    return [
        ResearchClaim(
            claim=(
                "Generative AI can automate repetitive "
                "software development tasks."
            ),
            source_title=(
                "Generative AI in Software Development: "
                "A Multiple Case Study on Process Transformation"
            ),
            source_url=(
                "https://aaltodoc.aalto.fi/"
                "bitstreams/3cc3575d-852b-44bc-b9ba-12fc374d1db0/"
                "download"
            ),
            evidence=(
                "The source discusses the transformation of "
                "software development processes through "
                "generative AI."
            ),
            importance="HIGH",
            claim_type="FINDING",
        ),
        ResearchClaim(
            claim=(
                "Generative AI can improve developer "
                "productivity for some software development tasks."
            ),
            source_title=(
                "Generative AI Adoption in Software Development"
            ),
            source_url=(
                "https://example.com/"
                "generative-ai-software-development"
            ),
            evidence=(
                "The source describes productivity-related "
                "benefits associated with generative AI."
            ),
            importance="HIGH",
            claim_type="FINDING",
        ),
        ResearchClaim(
            claim=(
                "Generative AI can introduce security risks "
                "when used in software development."
            ),
            source_title=(
                "Generative AI Adoption in Software Development"
            ),
            source_url=(
                "https://example.com/"
                "generative-ai-software-development"
            ),
            evidence=(
                "The source discusses potential security "
                "concerns associated with generative AI."
            ),
            importance="HIGH",
            claim_type="FINDING",
        ),
        ResearchClaim(
            claim=(
                "The impact of generative AI on software "
                "development includes both productivity "
                "opportunities and new risks."
            ),
            source_title=(
                "Generative AI in Software Development: "
                "A Multiple Case Study on Process Transformation"
            ),
            source_url=(
                "https://aaltodoc.aalto.fi/"
                "bitstreams/3cc3575d-852b-44bc-b9ba-12fc374d1db0/"
                "download"
            ),
            evidence=(
                "The test source covers both process "
                "transformation and implications of "
                "generative AI adoption."
            ),
            importance="MEDIUM",
            claim_type="FINDING",
        ),
    ]


if __name__ == "__main__":

    sources = create_mock_sources()
    claims = create_mock_claims()

    print("=" * 70)
    print("MOCK RESEARCH DATA TEST")
    print("=" * 70)

    print(
        f"\nTopic:\n{TEST_TOPIC}"
    )

    print(
        f"\nSources: {len(sources)}"
    )

    print(
        f"Claims: {len(claims)}"
    )

    for index, source in enumerate(
        sources,
        start=1,
    ):
        print(
            f"\nSOURCE {index}: {source.title}"
        )

    for index, claim in enumerate(
        claims,
        start=1,
    ):
        print(
            f"\nCLAIM {index}: {claim.claim}"
        )

    print(
        "\nMock research data loaded successfully."
    )