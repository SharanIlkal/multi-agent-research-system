from source_evaluator import evaluate_source

topic = "Impact of AI on the IT industry"
title = "Artificial Intelligence in the Workplace"
url = "https://example.com/ai-it"

content = """
Artificial intelligence is increasingly being used in
software development, cybersecurity, cloud computing,
and IT operations. Organizations are using AI tools
to automate repetitive tasks and improve productivity.
"""
result = evaluate_source(
    topic=topic,
    title=title,
    url=url,
    content=content
)

print("\n================ SOURCE EVALUATION ================\n")
print("Title:", result.title)
print("URL:", result.url)
print("Source Type:", result.source_type)
print("\nScores:")
print("Relevance:", result.relevance_score)
print("Authority:", result.authority_score)
print("Recency:", result.recency_score)
print("Evidence Quality:", result.evidence_quality_score)
print("Overall:", result.overall_score)
print("\nStrengths:")
for item in result.strengths:
    print("-", item)
print("\nWeaknesses:")
for item in result.weaknesses:
    print("-", item)