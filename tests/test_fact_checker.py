from fact_checker import fact_check_claim


topic = "Impact of AI on the IT industry"

claim = (
    "Artificial intelligence is being used to automate "
    "repetitive tasks in the IT industry."
)

evidence = """
Source 1:
Title: AI in IT Operations

URL: https://example.com/ai-it

Content:
Organizations are increasingly using artificial intelligence
to automate repetitive IT tasks, including monitoring,
incident detection, log analysis, and routine support
operations.

Source 2:
Title: AI and Software Development

URL: https://example.com/software-ai

Content:
AI-assisted development tools can automate parts of the
software development workflow, including code generation,
testing, and debugging.
"""


result = fact_check_claim(
    topic=topic,
    claim=claim,
    evidence=evidence
)


print("\n================ FACT CHECK ================\n")

print("Claim:")
print(result.claim)

print("\nStatus:")
print(result.status)

print("\nConfidence:")
print(result.confidence)

print("\nExplanation:")
print(result.explanation)

print("\nSupporting Sources:")
for source in result.supporting_sources:
    print("-", source)

print("\nContradicting Sources:")
for source in result.contradicting_sources:
    print("-", source)