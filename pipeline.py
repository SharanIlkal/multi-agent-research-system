from orchestrator import ResearchOrchestrator
from schemas import ResearchState

def run_research(topic: str, max_sources: int = 8, max_refinement_iterations: int = 3) -> ResearchState:
    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")
    orchestrator = ResearchOrchestrator(
        max_sources=max_sources,
        max_refinement_iterations=max_refinement_iterations,
    )
    return orchestrator.run(topic.strip())


def print_pipeline_summary(state: ResearchState):
    print("\n" + "=" * 70)
    print("RESEARCH PIPELINE SUMMARY")
    print("=" * 70)
    print(f"\nTopic: {state.topic}")
    print(f"Status: {state.status}")
    print(f"Search results: {len(state.search_results)}")
    print(f"Sources: {len(state.sources)}")
    print(f"Claims: {len(state._claims)}")
    print(f"Evidence citations: {len(state.evidence.citations)}")
    if state.report:
        print(f"Report: {state.report.title}")
    print(f"Trace events: {len(state.trace)}")
    if state.errors:
        print(f"Errors: {len(state.errors)}")
        for error in state.errors:
            print(f"- {error}")


if __name__ == "__main__":
    print("Live research pipeline loaded successfully.")
