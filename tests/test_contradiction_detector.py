from contradiction_detector import detect_contradiction


topic = "Impact of AI on software development"

evidence = """
Source 1

Title:
AI-Assisted Software Development

URL:
https://example.com/source-1

Content:
AI coding assistants can significantly improve developer
productivity by reducing the amount of time required for
routine programming tasks.


Source 2

Title:
Risks of AI Coding Assistants

URL:
https://example.com/source-2

Content:
Organizations using AI coding assistants have reported
that developers sometimes spend additional time reviewing
and correcting AI-generated code, which can reduce the
productivity benefit in certain development tasks.
"""


result = detect_contradiction(
    topic=topic,
    evidence=evidence
)


print("\n================ CONTRADICTION DETECTION ================\n")


if result is None:

    print("No meaningful contradiction detected.")

else:

    print("Topic:")
    print(result.topic)

    print("\nClaim A:")
    print(result.claim_a)

    print("\nSource A:")
    print(result.source_a)

    print("\nClaim B:")
    print(result.claim_b)

    print("\nSource B:")
    print(result.source_b)

    print("\nExplanation:")
    print(result.explanation)

    print("\nSeverity:")
    print(result.severity)