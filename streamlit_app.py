import streamlit as st
from orchestrator import ResearchOrchestrator

st.set_page_config(
    page_title="AI Research Analyst",
    page_icon="" ,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#000;color:#f5f5f5}.block-container{max-width:1450px;padding-top:2.4rem;padding-bottom:4rem}html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}h1,h2,h3,h4{color:#fff!important;letter-spacing:-.02em}p,label,.stMarkdown,.stCaption{color:#d4d4d4}.research-title{font-size:2.7rem;line-height:1.1;font-weight:700;color:#fff;margin-bottom:.45rem}.research-subtitle{color:#8f8f8f;font-size:1rem;line-height:1.6;max-width:900px;margin-bottom:2.2rem}[data-testid="stSidebar"],[data-testid="stSidebar"]>div:first-child{background:#050505;border-right:1px solid #1a1a1a}[data-testid="stSidebar"] .stTextArea textarea,[data-testid="stSidebar"] input,.stTextArea textarea,.stTextInput input{background:#070707!important;color:#eee!important;border:1px solid #242424!important;border-radius:8px!important}.stButton>button{border-radius:8px;min-height:42px;font-weight:600;border:1px solid #2a2a2a;background:#0b0b0b;color:#f5f5f5}.stButton>button:hover{border-color:#35c759;color:#35c759;background:#0e0e0e}.stButton>button[kind="primary"]{background:#35c759!important;border-color:#35c759!important;color:#000!important}[data-testid="stMetric"]{background:#080808;border:1px solid #1c1c1c;border-radius:10px;padding:1rem 1.1rem}[data-testid="stMetricLabel"]{color:#8f8f8f!important}[data-testid="stMetricValue"]{color:#fff!important}.stTabs [data-baseweb="tab-list"]{gap:0;background:#050505;border-bottom:1px solid #202020}.stTabs [data-baseweb="tab"]{color:#8f8f8f;background:transparent;border:none;padding:.85rem 1rem}.stTabs [aria-selected="true"]{color:#35c759!important;border-bottom:2px solid #35c759!important}[data-testid="stExpander"],div[data-testid="stVerticalBlockBorderWrapper"]{background:#070707;border:1px solid #1c1c1c;border-radius:9px;overflow:hidden}a{color:#35c759!important;text-decoration:none}hr{border-color:#1b1b1b!important}[data-testid="stAlert"]{background:#080808;border:1px solid #202020;color:#d8d8d8;border-radius:8px}.stProgress>div>div>div>div{background:#35c759}.stProgress>div>div{background:#181818}[data-testid="stCodeBlock"]{border:1px solid #1d1d1d;border-radius:8px}::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-track{background:#000}::-webkit-scrollbar-thumb{background:#242424;border-radius:8px}
</style>
""", unsafe_allow_html=True)

if "research_state" not in st.session_state:
    st.session_state.research_state = None

if "research_trace" not in st.session_state:
    st.session_state.research_trace = []

st.markdown(
    '<div class="research-title"> AI Research Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="research-subtitle">Autonomous live web research powered by Gemini, Tavily, evidence analysis, research memory and iterative critique.</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Research Configuration")
    topic = st.text_area(
        "Research Question",
        placeholder="Enter your Question",
        height=130
    )

    max_sources = st.slider(
        "Maximum Sources",
        min_value=2,
        max_value=20,
        value=8
    )

    max_refinement_iterations = st.slider(
        "Critic Refinement Iterations",
        min_value=1,
        max_value=5,
        value=2
    )
    st.divider()
    st.caption("Live mode only")
    st.caption("Gemini and Tavily are used for every research run.")
    run_research = st.button(
        " Start Live Research",
        type="primary",
        use_container_width=True
    )

    clear_results = st.button(
        "Clear Results",
        use_container_width=True
    )

if clear_results:
    st.session_state.research_state = None
    st.session_state.research_trace = []
    st.rerun()

if run_research:
    if not topic.strip():
        st.warning("Please enter a research question.")
    else:
        progress = st.progress(0)
        status_box = st.empty()

        try:
            status_box.info("Initializing live research orchestrator...")
            progress.progress(5)
            orchestrator = ResearchOrchestrator(
                max_sources=max_sources,
                max_refinement_iterations=max_refinement_iterations
            )

            status_box.info("Gemini is creating the research plan...")
            progress.progress(15)
            state = orchestrator.run(topic.strip())
            progress.progress(100)
            if state.status == "completed":
                status_box.success("Live research completed successfully.")
            else:
                status_box.warning(f"Research finished with status: {state.status}")
            st.session_state.research_state = state
            st.session_state.research_trace = orchestrator.get_trace_dict()
        except Exception as exc:
            progress.empty()
            status_box.empty()
            st.error(f"Live research failed: {exc}")

state = st.session_state.research_state

if state is None:
    st.info("Enter a research question and click **Start Live Research**.")
    st.stop()
st.divider()
st.header("Research Overview")
col1, col2, col3, col4, col5 = st.columns(5)
claims = getattr(state, "_claims", [])
coverage = getattr(state, "_coverage", None)
memory_results = getattr(state, "_memory_results", [])
search_queries = state.research_plan.search_queries if state.research_plan else []
with col1:
    st.metric("Status", state.status.upper())
with col2:
    st.metric("Search Results", len(state.search_results))
with col3:
    st.metric("Sources", len(state.sources))
with col4:
    st.metric("Claims", len(claims))
with col5:
    st.metric("Trace Events", len(state.trace))
metric_cols = st.columns(5)
with metric_cols[0]:
    st.metric("Search Queries", len(search_queries))
with metric_cols[1]:
    st.metric("Fact Checks", len(state.evidence.fact_checks))
with metric_cols[2]:
    st.metric("Contradictions", len(state.evidence.contradictions))
with metric_cols[3]:
    st.metric("Citations", len(state.evidence.citations))
with metric_cols[4]:
    coverage_value = coverage.get("coverage_ratio", 0) if coverage else 0
    st.metric("Coverage", f"{coverage_value * 100:.1f}%")
st.divider()

tabs = st.tabs([
    " Research Plan",
    " Sources",
    " Claims",
    " Evidence",
    " Coverage",
    " Final Report",
    " Research Trace",
    " Memory"
])

with tabs[0]:
    st.subheader("Research Plan")
    if state.research_plan:
        st.markdown("### Research Goal")
        st.write(state.research_plan.research_goal)
        st.markdown("### Sub-Questions")
        for index, question in enumerate(
            state.research_plan.sub_questions,
            start=1
        ):
            st.markdown(f"**{index}.** {question}")
        st.markdown("### Search Queries")
        for query in state.research_plan.search_queries:
            st.code(query)
        st.markdown("### Target Source Types")
        for source_type in state.research_plan.source_types:
            st.markdown(f"- {source_type}")

with tabs[1]:
    st.subheader("Collected Sources")
    evaluations = {
        evaluation.url: evaluation
        for evaluation in state.evidence.source_evaluations
    }

    if not state.sources:
        st.info("No sources available.")
    else:
        for index, source in enumerate(state.sources, start=1):
            title = getattr(source, "title", "Untitled Source")
            url = getattr(source, "url", "")
            source_type = getattr(source, "source_type", "")
            content = getattr(source, "content", "")
            evaluation = evaluations.get(url)

            with st.expander(f"{index}. {title}"):
                source_cols = st.columns(5)

                if evaluation:
                    source_cols[0].metric("Overall", f"{evaluation.overall_score:.2f}")
                    source_cols[1].metric("Relevance", f"{evaluation.relevance_score:.2f}")
                    source_cols[2].metric("Authority", f"{evaluation.authority_score:.2f}")
                    source_cols[3].metric("Recency", f"{evaluation.recency_score:.2f}")
                    source_cols[4].metric("Evidence", f"{evaluation.evidence_quality_score:.2f}")
                if source_type:
                    st.caption(f"Source type: {source_type}")
                if url:
                    st.markdown(f"[Open Source ↗]({url})")
                if evaluation:
                    left, right = st.columns(2)
                    with left:
                        st.markdown("**Strengths**")
                        for item in evaluation.strengths:
                            st.success(item)
                    with right:
                        st.markdown("**Weaknesses**")
                        for item in evaluation.weaknesses:
                            st.warning(item)

                if content:
                    st.text_area(
                        "Extracted Content",
                        content,
                        height=220,
                        key=f"source_content_{index}"
                    )

with tabs[2]:
    st.subheader("Extracted Research Claims")
    claims = getattr(state, "_claims", [])
    if not claims:
        st.info("No claims were extracted.")
    else:
        for index, claim in enumerate(claims, start=1):
            if hasattr(claim, "model_dump"):
                claim_data = claim.model_dump()
            elif isinstance(claim, dict):
                claim_data = claim
            else:
                claim_data = {"claim": str(claim)}
            with st.container(border=True):
                st.markdown(f"### Claim {index}")
                for key, value in claim_data.items():
                    if isinstance(value, list):
                        st.markdown(f"**{key.replace('_', ' ').title()}**")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

with tabs[3]:
    st.subheader("Evidence Engine")
    evidence = state.evidence
    if evidence.fact_checks:
        st.markdown("### Fact-Check Confidence")
        for index, fact_check in enumerate(evidence.fact_checks, start=1):
            label = f"{index}. {fact_check.status.replace('_', ' ').title()} — {fact_check.confidence:.0%}"
            st.progress(
                max(0.0, min(float(fact_check.confidence), 1.0)),
                text=label
            )
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Source Evaluations", len(evidence.source_evaluations))
    with col2:
        st.metric("Fact Checks", len(evidence.fact_checks))
    with col3:
        st.metric("Contradictions", len(evidence.contradictions))
    with col4:
        st.metric("Citations", len(evidence.citations))
    st.divider()
    st.markdown("### Source Evaluations")
    for index, evaluation in enumerate(
        evidence.source_evaluations,
        start=1
    ):
        with st.expander(f"Source Evaluation {index}"):
            data = (
                evaluation.model_dump()
                if hasattr(evaluation, "model_dump")
                else evaluation
            )
            st.json(data)

    st.markdown("### Fact Checks")
    for index, fact_check in enumerate(
        evidence.fact_checks,
        start=1
    ):
        with st.expander(f"Fact Check {index}"):
            data = (
                fact_check.model_dump()
                if hasattr(fact_check, "model_dump")
                else fact_check
            )
            st.json(data)
    st.markdown("### Contradictions")
    if evidence.contradictions:
        for index, contradiction in enumerate(
            evidence.contradictions,
            start=1
        ):
            with st.expander(f"Contradiction {index}"):
                data = (
                    contradiction.model_dump()
                    if hasattr(contradiction, "model_dump")
                    else contradiction
                )
                st.json(data)
    else:
        st.success("No contradictions detected.")
    st.markdown("### Citation Mapping")

    for index, citation in enumerate(
        evidence.citations,
        start=1
    ):
        with st.expander(f"Citation {index}"):
            data = (
                citation.model_dump()
                if hasattr(citation, "model_dump")
                else citation
            )
            st.json(data)

with tabs[4]:
    st.subheader("Research Coverage")
    coverage = getattr(state, "_coverage", None)
    if not coverage:
        st.info("Coverage analysis is not available.")
    else:
        status = coverage.get("status", "UNKNOWN")
        ratio = coverage.get("coverage_ratio", 0)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Status", status)
        with col2:
            st.metric("Coverage", f"{ratio * 100:.1f}%")
        with col3:
            st.metric("Covered", coverage.get("covered_count", 0))
        with col4:
            st.metric("Missing", coverage.get("missing_count", 0))
        st.progress(min(max(ratio, 0.0), 1.0))
        st.markdown("### Covered Questions")
        for question in coverage.get("covered_questions", []):
            st.success(question)
        st.markdown("### Partial Questions")
        for question in coverage.get("partial_questions", []):
            st.warning(question)
        st.markdown("### Missing Questions")
        for question in coverage.get("missing_questions", []):
            st.error(question)
        st.markdown("### Weak Evidence Areas")
        for area in coverage.get("weak_evidence_areas", []):
            st.warning(area)
        st.markdown("### Missing Source Types")
        for source_type in coverage.get("missing_source_types", []):
            st.info(source_type)

with tabs[5]:
    st.subheader("Final Research Report")
    if state.report:
        report = state.report
        report_cols = st.columns(3)
        with report_cols[0]:
            st.metric("Findings", len(report.key_findings))
        with report_cols[1]:
            st.metric("Limitations", len(report.limitations))
        with report_cols[2]:
            st.metric("References", len(report.references))
        report = state.report
        st.title(report.title)
        st.markdown("### Research Question")
        st.write(report.research_question)
        st.markdown("### Executive Summary")
        st.write(report.executive_summary)
        st.markdown("### Key Findings")
        for index, finding in enumerate(
            report.key_findings,
            start=1
        ):
            st.markdown(f"**{index}.** {finding}")
        st.markdown("### Evidence Analysis")
        st.write(report.evidence_analysis)
        st.markdown("### Limitations")

        for limitation in report.limitations:
            st.markdown(f"- {limitation}")
        st.markdown("### Conclusion")
        st.write(report.conclusion)
        st.markdown("### References")
        for index, reference in enumerate(
            report.references,
            start=1
        ):
            st.markdown(f"{index}. {reference}")
    else:
        st.warning("No final report generated.")
with tabs[6]:
    st.subheader("Research Trace")
    trace = st.session_state.research_trace
    if not trace:
        trace = [
            {
                "timestamp": event.timestamp,
                "stage": event.stage,
                "event": event.event,
                "details": event.details
            }
            for event in state.trace
        ]

    if trace:
        st.caption(f"{len(trace)} pipeline events captured.")
    if not trace:
        st.info("No trace events available.")
    else:
        for index, event in enumerate(trace, start=1):
            stage = event.get("stage", "")
            event_name = event.get("event", "")
            timestamp = event.get("timestamp", "")
            details = event.get("details", {})

            with st.container(border=True):
                st.markdown(f"**{index}. {event_name}**")
                st.caption(f"{timestamp} · Stage: {stage}")
                if details:
                    st.json(details)

with tabs[7]:
    st.subheader("Research Memory")
    memory_results = getattr(state, "_memory_results",[])
    memory_context = getattr(state, "_memory_context","")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Retrieved Memory Items", len(memory_results))
    with col2:
        st.metric("Memory Context", f"{len(memory_context)} chars")
    if memory_results:
        st.markdown("### Retrieved Previous Research")
        for index, item in enumerate(
            memory_results,
            start=1
        ):
            with st.expander(f"Memory Item {index}"):
                if isinstance(item, dict):
                    st.json(item)
                else:
                    st.write(item)
    else:
        st.info("No previous research memory matched this topic.")
st.divider()
if state.errors:
    st.error("The pipeline reported errors.")
    for error in state.errors:
        st.code(error)

if state.status == "completed":
    st.success("Live research pipeline completed successfully.")
elif state.status == "failed":
    st.error("Live research pipeline failed.")
