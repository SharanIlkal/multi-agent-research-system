from citation_mapper import map_citations


topic = "Impact of AI on the IT industry"

evidence = """
Source 1:
Title: AI in Software Development

URL:
https://example.com/software-ai

Evidence:
AI coding assistants are increasingly being used to
generate code, write tests, and assist developers with
debugging.


Source 2:
Title: AI in Cybersecurity

URL:
https://example.com/ai-security

Evidence:
Cybersecurity teams are using AI to detect anomalies,
analyze security logs, and identify potential threats.


Source 3:
Title: AI and IT Operations

URL:
https://example.com/ai-operations

Evidence:
AI-powered IT operations tools can identify infrastructure
anomalies and help organizations detect potential failures
before they cause service interruptions.
"""


citations = map_citations(
    topic=topic,
    evidence=evidence
)


print("\n================ CITATION MAPPING ================\n")


for index, citation in enumerate(citations, start=1):

    print(f"Citation {index}")
    print("-" * 50)

    print("Claim:")
    print(citation.claim)

    print("\nSource:")
    print(citation.source_title)

    print("\nURL:")
    print(citation.source_url)

    print("\nSupporting Evidence:")
    print(citation.supporting_evidence)

    print("\n")