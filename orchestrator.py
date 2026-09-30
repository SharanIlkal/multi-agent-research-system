from typing import Any
from schemas import ResearchState, ResearchTraceEvent
from research_trace import ResearchTrace
from research_memory import ResearchMemory
from query_refiner import QueryRefiner
from coverage_analyzer import CoverageAnalyzer
class ResearchOrchestrator:
    def __init__(
        self,
        max_sources: int = 8,
        max_refinement_iterations: int = 3,
    ):
        self.max_sources = max_sources
        self.max_refinement_iterations = max_refinement_iterations
        self.query_refiner = QueryRefiner(max_refined_queries=5)
        self.max_query_refinement_rounds = 2
        self.trace = ResearchTrace()
        self.memory = ResearchMemory()
        self.current_run_id: str | None = None
        self.coverage_analyzer = CoverageAnalyzer()
        self.max_coverage_rounds = 2
        self.memory_retrieval_limit = 5

    def _analyze_research_coverage(self, state):
        claims = getattr(state, "_claims", [])
        coverage = self.coverage_analyzer.analyze(
            topic=state.topic,
            sub_questions=state.research_plan.sub_questions,
            search_results=state.search_results,
            claims=claims,
            evidence=state.evidence,
        )
        state._coverage = coverage
        self._trace(
            state,
            "coverage",
            "research_coverage_analyzed",
            {
                "status": coverage["status"],
                "coverage_ratio": coverage["coverage_ratio"],
                "covered": coverage["covered_count"],
                "partial": coverage["partial_count"],
                "missing": coverage["missing_count"],
                "missing_questions": coverage["missing_questions"],
                "weak_evidence_areas": coverage["weak_evidence_areas"],
                "missing_source_types": coverage["missing_source_types"],
            },
        )
        return state

    def _run_query_refinement(self, state: ResearchState) -> ResearchState:
        if not state.research_plan:
            return state
        for refinement_round in range(self.max_query_refinement_rounds):
            self._trace(state, "query_refiner", "refinement_round_started", {"round": refinement_round + 1, "max_rounds": self.max_query_refinement_rounds, "current_results": len(state.search_results)})
            refinement_result = self.query_refiner.refine(
                topic=state.topic,
                sub_questions=state.research_plan.sub_questions,
                existing_queries=state.research_plan.search_queries,
                search_results=state.search_results,
            )
            missing_areas = refinement_result["missing_areas"]
            refined_queries = refinement_result["refined_queries"]
            coverage_complete = refinement_result["coverage_complete"]
            self._trace(state, "query_refiner", "coverage_analyzed", {"round": refinement_round + 1, "missing_areas": missing_areas, "refined_queries": refined_queries, "coverage_complete": coverage_complete})
            if coverage_complete:
                self._trace(state, "query_refiner", "coverage_complete", {"round": refinement_round + 1})
                break
            if not refined_queries:
                self._trace(state, "query_refiner", "no_new_queries", {"round": refinement_round + 1})
                break
            try:
                self._trace(state, "query_refiner", "additional_search_started", {"queries": refined_queries})
                from parallel_search import parallel_search
                additional_results = parallel_search(refined_queries, max_results_per_query=5, max_workers=3)
                existing_urls = {result.url for result in state.search_results if getattr(result, "url", None)}
                new_results = []
                for result in additional_results:
                    result_url = getattr(result, "url", None)
                    if result_url and result_url in existing_urls:
                        continue
                    new_results.append(result)
                    if result_url:
                        existing_urls.add(result_url)
                state.search_results.extend(new_results)
                for query in refined_queries:
                    if query not in state.research_plan.search_queries:
                        state.research_plan.search_queries.append(query)
                self._trace(state, "query_refiner", "additional_search_completed", {"queries_added": len(refined_queries), "new_results": len(new_results), "total_results": len(state.search_results)})
                if not new_results:
                    self._trace(state, "query_refiner", "no_new_results", {})
                    break
            except Exception as exc:
                self._add_error(state, exc, "query_refiner")
                break
        return state
    
    def _trace(
        self,
        state: ResearchState,
        stage: str,
        event: str,
        details: dict[str, Any] | None = None,
    ):
        trace_event = self.trace.add(
            stage=stage,
            event=event,
            details=details or {},
        )
        state.trace.append(
            ResearchTraceEvent(
                timestamp=trace_event.timestamp,
                stage=trace_event.stage,
                event=trace_event.event,
                details=trace_event.details,
            )
        )

    def _create_initial_state(
        self,
        topic: str,
    ) -> ResearchState:
        state = ResearchState(
            topic=topic,
            status="initialized",
        )
        self._trace(
            state,
            "orchestrator",
            "research_started",
            {
                "topic": topic,
                "mode": "live",
            },
        )
        state = self._retrieve_research_memory(state)
        memory_context = self._build_memory_context(state)
        state._memory_context = memory_context

        self._trace(
            state,
            "memory",
            "memory_context_built",
            {
                "items": len(getattr(state, "_memory_results", [])),
                "context_length": len(memory_context),
            },
        )
        self.current_run_id = (
            self.memory.create_research_run(
                topic
            )
        )
        self._trace(
            state,
            "memory",
            "research_memory_created",
            {
                "run_id": self.current_run_id,
            },
        )
        return state
    def _update_status(
        self,
        state: ResearchState,
        status: str,
    ):
        state.status = status
        self._trace(
            state,
            "orchestrator",
            "status_updated",
            {
                "status": status,
            },
        )
    def _add_error(
        self,
        state: ResearchState,
        error: Exception,
        stage: str = "orchestrator",
    ):
        message = str(error)
        state.errors.append(message)
        state.status = "failed"
        self._trace(
            state,
            stage,
            "error",
            {
                "error": message,
            },
        )
    def _store_source_in_memory(
        self,
        source,
    ):
        if not self.current_run_id:
            return False
        if hasattr(source, "model_dump"):
            source_data = source.model_dump()
        elif isinstance(source, dict):
            source_data = source
        else:
            source_data = {
                "title": getattr(source, "title","",),
                "url": getattr(source, "url", "",),
                "source_type": getattr(source, "source_type", "",),
                "content": getattr(source,"content", "",),
            }
        return self.memory.add_source(self.current_run_id,source_data,)

    
    def _store_claims_in_memory(self,claims,):
        if not self.current_run_id:
            return 0
        stored = 0
        for claim in claims:
            if hasattr(claim, "model_dump"):
                claim_data = claim.model_dump()
            elif isinstance(claim, dict):
                claim_data = claim
            else:
                claim_data = {"claim": str(claim),}
            if self.memory.add_claim(
                self.current_run_id,
                claim_data,
            ):
                stored += 1
        return stored

    
    def _store_evidence_in_memory(self, evidence,):
        if not self.current_run_id:
            return 0
        stored = 0
        if hasattr(evidence, "model_dump"):
            evidence_data = evidence.model_dump()
            if isinstance(evidence_data, dict):
                for key, value in evidence_data.items():
                    if self.memory.add_evidence(
                        self.current_run_id,
                        {
                            "type": key,
                            "data": value,
                        },
                    ):
                        stored += 1
        return stored
    
    def _store_report_in_memory(self,report,):
        if not self.current_run_id:
            return False
        if hasattr(report, "model_dump"):
            report_data = report.model_dump()
        elif isinstance(report, dict):
            report_data = report
        else:
            report_data = {
                "title": getattr(report,"title","",)
            }
        return self.memory.store_report( self.current_run_id,report_data,)

    
    def _apply_memory_to_plan(self, state: ResearchState) -> ResearchState:
        if not state.research_plan:
            return state
        memory_results = getattr(state, "_memory_results", [])
        if not memory_results:
            self._trace(
                state,
                "memory",
                "memory_plan_enrichment_skipped",
                {"reason": "no_memory_matches"},
            )
            return state
        added_queries = []
        for item in memory_results:
            if not isinstance(item, dict):
                continue
            claim = str(item.get("claim", "")).strip()
            title = str(item.get("title", "")).strip()
            candidate = claim or title
            if not candidate:
                continue
            query = f"{state.topic} {candidate}"
            if query not in state.research_plan.search_queries:
                state.research_plan.search_queries.append(query)
                added_queries.append(query)
            if len(added_queries) >= 2:
                break
        self._trace(
            state,
            "memory",
            "memory_plan_enriched",
            {
                "memory_items": len(memory_results),
                "queries_added": len(added_queries),
            },
        )
        return state

    def create_plan(self, state: ResearchState,) -> ResearchState:
        self._update_status(state, "creating_research_plan",)
        memory_context = getattr(state, "_memory_context", "")
        self._trace(
            state,
            "supervisor",
            "research_plan_started",
        )
        self._trace(
            state,
            "memory",
            "memory_context_attached_to_planner",
            {
                "context_length": len(memory_context),
                "has_memory": bool(memory_context),
            },
        )
        from agents import create_research_plan
        state.research_plan = create_research_plan(
            state.topic
        )
        state = self._apply_memory_to_plan(state)
        self._trace(
            state,
            "supervisor",
            "research_plan_created",
            {
                "sub_questions": len(
                    state.research_plan.sub_questions
                ),
                "search_queries": len(
                    state.research_plan.search_queries
                ),
                "source_types": len(
                    state.research_plan.source_types
                ),
            },
        )
        self._update_status(
            state,
            "research_plan_created",
        )
        return state


    def search(self, state: ResearchState) -> ResearchState:
        self._update_status(state, "searching")
        queries = state.research_plan.search_queries
        self._trace(
            state,
            "search",
            "parallel_search_started",
            {
                "queries": len(queries),
                "max_sources_per_query": 5,
            },
        )
        from parallel_search import parallel_search
        state.search_results = parallel_search(
            queries,
            max_results_per_query=5,
            max_workers=3,
        )
        if not state.search_results:
            raise RuntimeError("Live web search returned no usable sources.")
        self._trace(
            state,
            "search",
            "parallel_search_completed",
            {
                "queries": len(queries),
                "search_results": len(state.search_results),
            },
        )
        self._update_status(state, "search_completed")
        return state

    
    def read_sources(self, state: ResearchState,) -> ResearchState:
        self._update_status(state, "reading_sources",)
        self._trace(
            state,
            "reader",
            "source_reading_started",
            {
                "mode": "live",
            },
        )
        from reader_agent import read_sources
        state.sources = read_sources(
            state.search_results,
            max_sources=self.max_sources,
        )
        if not state.sources:
            raise RuntimeError("No research sources could be read from the live search results.")
        stored_sources = 0
        duplicate_sources = 0
        for source in state.sources:
            url = getattr(
                source,
                "url",
                "",
            )
            if (
                url
                and self.memory.source_exists(url)
            ):
                duplicate_sources += 1
            if self._store_source_in_memory(
                source
            ):
                stored_sources += 1
        self._trace(
            state,
            "memory",
            "sources_persisted",
            {
                "stored": stored_sources,
                "duplicates_detected": duplicate_sources,
            },
        )
        self._trace(
            state,
            "reader",
            "source_reading_completed",
            {
                "sources_read": len(
                    state.sources
                ),
            },
        )
        self._update_status(
            state,
            "sources_read",
        )
        return state

    
    def extract_claims(self, state: ResearchState) -> ResearchState:
        self._update_status(state, "extracting_claims")
        self._trace(
            state,
            "claims",
            "claim_extraction_started",
            {
                "sources": len(state.sources),
            },
        )

        from claim_extractor import extract_claims
        claims = []
        successful_sources = 0
        failed_sources = 0
        for index, source in enumerate(state.sources, start=1):
            try:
                self._trace(
                    state,
                    "claims",
                    "source_claim_extraction_started",
                    {
                        "source_index": index,
                        "source_title": source.title,
                        "source_url": source.url,
                    },
                )

                result = extract_claims(state.topic, source,)
                source_claims = result.claims
                claims.extend(source_claims)
                successful_sources += 1
                self._trace(
                    state,
                    "claims",
                    "source_claim_extraction_completed",
                    {
                        "source_index": index,
                        "source_title": source.title,
                        "claims": len(source_claims),
                    },
                )

            except Exception as exc:
                failed_sources += 1
                self._trace(
                    state,
                    "claims",
                    "source_claim_extraction_failed",
                    {
                        "source_index": index,
                        "source_title": source.title,
                        "error": str(exc),
                    },
                )
                print(
                    f"[ORCHESTRATOR] Claim extraction failed for source "
                    f"{index}: {exc}"
                )
                continue
        state._claims = claims

        if not claims:
            raise RuntimeError("No research claims could be extracted from any live source.")
        stored_claims = self._store_claims_in_memory(claims)
        self._trace(
            state,
            "memory",
            "claims_persisted",
            {
                "claims": stored_claims,
            },
        )

        self._trace(
            state,
            "claims",
            "claims_extracted",
            {
                "claims": len(claims),
                "successful_sources": successful_sources,
                "failed_sources": failed_sources,
            },
        )

        if failed_sources > 0:
            self._trace(
                state,
                "claims",
                "partial_claim_extraction",
                {
                    "successful_sources": successful_sources,
                    "failed_sources": failed_sources,
                },
            )

        self._update_status(state, "claims_extracted",)
        return state
    
    def build_evidence(self, state: ResearchState,) -> ResearchState:
        self._update_status(state, "building_evidence",)
        claims = getattr(
            state,
            "_claims",
            [],
        )
        self._trace(
            state,
            "evidence",
            "evidence_engine_started",
            {
                "sources": len(
                    state.sources
                ),
                "claims": len(claims),
                "mode": "live",
            },
        )
        from evidence import build_evidence_package
        state.evidence = build_evidence_package(
            topic=state.topic,
            sources=state.sources,
            claims=claims,
        )
        stored_evidence = (self._store_evidence_in_memory(state.evidence))
        self._trace(
            state,
            "memory",
            "evidence_persisted",
            {
                "items": stored_evidence,
            },
        )
        self._trace(
            state,
            "evidence",
            "evidence_package_created",
            {
                "source_evaluations": len(
                    state.evidence.source_evaluations
                ),
                "fact_checks": len(
                    state.evidence.fact_checks
                ),
                "contradictions": len(
                    state.evidence.contradictions
                ),
                "citations": len(
                    state.evidence.citations
                ),
            },
        )
        self._update_status(
            state,
            "evidence_created",
        )
        return state

    
    def generate_final_report(self,state: ResearchState,) -> ResearchState:
        self._update_status(state, "generating_report",)
        claims = getattr(
            state,
            "_claims",
            [],
        )
        self._trace(
            state,
            "writer",
            "report_generation_started",
            {
                "claims": len(claims),
                "sources": len(
                    state.sources
                ),
            },
        )
        from refinement_loop import refine_report
        state.report = refine_report(
            topic=state.topic,
            research_plan=state.research_plan,
            sources=state.sources,
            claims=claims,
            evidence=state.evidence,
            max_iterations=self.max_refinement_iterations,
        )
        report_stored = (
            self._store_report_in_memory(
                state.report
            )
        )
        self._trace(
            state,
            "memory",
            "report_persisted",
            {
                "stored": report_stored,
            },
        )
        self._trace(
            state,
            "writer",
            "report_generated",
            {
                "title": state.report.title,
                "research_question": (
                    state.report.research_question
                ),
                "key_findings": len(
                    state.report.key_findings
                ),
                "references": len(
                    state.report.references
                ),
            },
        )
        self._update_status(
            state,
            "report_generated",
        )
        return state

    
    def _run_coverage_loop(self, state: ResearchState) -> ResearchState:
        if not state.research_plan:
            return state
        claims = getattr(state, "_claims", [])
        for round_number in range(self.max_coverage_rounds):
            self._trace(
                state,
                "coverage",
                "coverage_analysis_started",
                {
                    "round": round_number + 1,
                    "max_rounds": self.max_coverage_rounds,
                },
            )
            coverage = self.coverage_analyzer.analyze(
                topic=state.topic,
                sub_questions=state.research_plan.sub_questions,
                search_results=state.search_results,
                claims=claims,
                evidence=state.evidence,
            )
            state._coverage = coverage
            self._trace(
                state,
                "coverage",
                "coverage_gaps_detected",
                {
                    "round": round_number + 1,
                    "status": coverage["status"],
                    "coverage_ratio": coverage["coverage_ratio"],
                    "covered": coverage["covered_count"],
                    "partial": coverage["partial_count"],
                    "missing": coverage["missing_count"],
                    "missing_questions": coverage["missing_questions"],
                    "weak_evidence_areas": coverage["weak_evidence_areas"],
                    "missing_source_types": coverage["missing_source_types"],
                },
            )

            if coverage["status"] == "SUFFICIENT":
                self._trace(
                    state,
                    "coverage",
                    "coverage_complete",
                    {
                        "round": round_number + 1,
                        "coverage_ratio": coverage["coverage_ratio"],
                    },
                )
                break

            gap_queries = self.coverage_analyzer.generate_gap_queries(
                topic=state.topic,
                coverage=coverage,
                existing_queries=state.research_plan.search_queries,
                max_queries=5,
            )

            self._trace(
                state,
                "coverage",
                "gap_queries_generated",
                {
                    "round": round_number + 1,
                    "queries": gap_queries,
                },
            )

            if not gap_queries:
                self._trace(
                    state,
                    "coverage",
                    "no_gap_queries",
                    {
                        "round": round_number + 1,
                    },
                )
                break

            try:
                self._trace(
                    state,
                    "coverage",
                    "additional_search_started",
                    {
                        "queries": gap_queries,
                    },
                )

                from parallel_search import parallel_search
                additional_results = parallel_search(
                    gap_queries,
                    max_results_per_query=5,
                    max_workers=3,
                )
                existing_urls = {
                    getattr(result, "url", "")
                    for result in state.search_results
                    if getattr(result, "url", "")
                }
                new_results = []
                for result in additional_results:
                    result_url = getattr(result, "url", "")
                    if result_url and result_url in existing_urls:
                        continue
                    new_results.append(result)
                    if result_url:
                        existing_urls.add(result_url)
                state.search_results.extend(new_results)
                for query in gap_queries:
                    if query not in state.research_plan.search_queries:
                        state.research_plan.search_queries.append(query)

                self._trace(
                    state,
                    "coverage",
                    "additional_search_completed",
                    {
                        "queries": len(gap_queries),
                        "new_results": len(new_results),
                        "total_results": len(state.search_results),
                    },
                )

                if not new_results:
                    self._trace(
                        state,
                        "coverage",
                        "no_new_results",
                        {
                            "round": round_number + 1,
                        },
                    )
                    break

            except Exception as exc:
                self._add_error(
                    state,
                    exc,
                    "coverage",
                )
                break
        return state

    def get_trace(self):
        return self.trace.get_events()

    def get_trace_summary(self):
        return self.trace.summary()

    def get_trace_dict(self):
        return self.trace.to_dict()

    def _retrieve_research_memory(self, state: ResearchState) -> ResearchState:
        self._trace(
            state,
            "memory",
            "memory_retrieval_started",
            {
                "topic": state.topic,
                "limit": self.memory_retrieval_limit,
            },
        )

        try:
            results = self.memory.search_memory(state.topic)
            results = results[:self.memory_retrieval_limit]
            state._memory_results = results
            self._trace(
                state,
                "memory",
                "memory_retrieval_completed",
                {
                    "matches": len(results),
                },
            )
            return state
        except Exception as exc:
            self._add_error(
                state,
                exc,
                "memory",
            )
            state._memory_results = []
            return state
        
    def _build_memory_context(self, state: ResearchState) -> str:
        memory_results = getattr(state, "_memory_results", [])
        if not memory_results:
            return ""
        lines = []

        for index, item in enumerate(memory_results, start=1):
            if isinstance(item, dict):
                topic = item.get("topic", "")
                claim = item.get("claim", "")
                title = item.get("title", "")
                url = item.get("url", "")
                lines.append(
                    f"Memory Item {index}\n"
                    f"Topic: {topic}\n"
                    f"Title: {title}\n"
                    f"Claim: {claim}\n"
                    f"URL: {url}"
                )
            else:
                lines.append(f"Memory Item {index}\n{item}")
        return "\n\n".join(lines)

    def run(self, topic: str,) -> ResearchState:
        self.trace.clear()
        state = self._create_initial_state(topic)
        try:
            state = self.create_plan(state)
            state = self.search(state)
            state = self._run_query_refinement(state)
            state = self.read_sources(state)
            state = self.extract_claims(state)
            state = self.build_evidence(state)
            state = self._run_coverage_loop(state)
            state = self.generate_final_report(state)
            self._trace(
                state,
                "orchestrator",
                "live_refinement_completed",
                {"status": state.status},
            )
            state.status = "completed"
            self._trace(
                state,
                "orchestrator",
                "research_completed",
                {"status": state.status},
            )
            return state
        except Exception as error:
            self._add_error(state, error, "orchestrator")
            return state
        
def print_pipeline_summary(state: ResearchState,):
    print("\n" + "=" * 70)
    print("RESEARCH PIPELINE SUMMARY")
    print("=" * 70)
    print(f"\nTopic: {state.topic}")
    print(f"Status: {state.status}")
    if state.research_plan:
        print("Sub-questions: " f"{len(state.research_plan.sub_questions)}")
        print("Search queries: " f"{len(state.research_plan.search_queries)}")
    print("Search results: " f"{len(state.search_results)}")
    print("Sources: " f"{len(state.sources)}")
    print("Evidence citations: " f"{len(state.evidence.citations)}")
    if state.report:
        print("Report: " f"{state.report.title}")
    print("Trace events: " f"{len(state.trace)}")
    print("\nMemory statistics:")
    memory = ResearchMemory()
    print(memory.statistics())
    if state.errors:
        print(f"\nErrors: {len(state.errors)}")
        for error in state.errors:
            print(f"- {error}")
    print("\n" + "=" * 70)
    print("TRACE"  )
    print("=" * 70)
    for index, event in enumerate(
        state.trace,
        start=1,
    ):
        print(
            f"\n[{index}] "
            f"{event.timestamp}"
        )
        print(
            f"Stage: {event.stage}"
        )
        print(
            f"Event: {event.event}"
        )
        if event.details:
            print(
                f"Details: {event.details}"
            )
if __name__ == "__main__":
    print("Live Research Orchestrator loaded successfully.")
