from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

@dataclass
class TraceEvent:
    timestamp: str
    stage: str
    event: str
    details: Dict[str, Any] = field(default_factory=dict)

class ResearchTrace:
    def __init__(self):
        self.events: List[TraceEvent] = []

    def add(self, stage: str, event: str, details: Dict[str, Any] | None = None) -> TraceEvent:
        trace_event = TraceEvent(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            stage=stage,
            event=event,
            details=details or {},
        )
        self.events.append(trace_event)
        return trace_event

    def count(self) -> int:
        return len(self.events)

    def latest(self) -> TraceEvent | None:
        if not self.events:
            return None
        return self.events[-1]

    def get_events(self) -> List[TraceEvent]:
        return list(self.events)

    def get_events_by_stage(self, stage: str) -> List[TraceEvent]:
        return [
            event
            for event in self.events
            if event.stage == stage
        ]

    def get_stages(self) -> List[str]:
        stages = []
        for event in self.events:
            if event.stage not in stages:
                stages.append(event.stage)
        return stages

    def stage_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self.events:
            counts[event.stage] = counts.get(event.stage, 0) + 1
        return counts

    def event_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self.events:
            counts[event.event] = counts.get(event.event, 0) + 1
        return counts

    def has_event(self, event_name: str) -> bool:
        return any(
            event.event == event_name
            for event in self.events
        )

    def has_stage(self, stage: str) -> bool:
        return any(
            event.stage == stage
            for event in self.events
        )

    def to_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": event.timestamp,
                "stage": event.stage,
                "event": event.event,
                "details": event.details,
            }
            for event in self.events
        ]

    def summary(self) -> Dict[str, Any]:
        return {
            "total_events": self.count(),
            "stages": self.get_stages(),
            "stage_counts": self.stage_counts(),
            "event_counts": self.event_counts(),
            "latest_event": (
                self.latest().event
                if self.latest()
                else None
            ),
        }

    def clear(self):
        self.events.clear()

    def print_trace(self):
        print("\n" + "=" * 70)
        print("RESEARCH TRACE")
        print("=" * 70)

        for index, event in enumerate(self.events, start=1):
            print(f"\n[{index}] {event.timestamp}")
            print(f"Stage: {event.stage}")
            print(f"Event: {event.event}")
            if event.details:
                print(f"Details: {event.details}")

    def print_summary(self):
        summary = self.summary()
        print("\n" + "=" * 70)
        print("RESEARCH TRACE SUMMARY")
        print("=" * 70)
        print(f"Total events: {summary['total_events']}")
        print(f"Stages: {', '.join(summary['stages'])}")
        print("\nEvents by stage:")
        for stage, count in summary["stage_counts"].items():
            print(f"- {stage}: {count}")
        print(f"\nLatest event: {summary['latest_event']}")


if __name__ == "__main__":
    trace = ResearchTrace()
    trace.add("orchestrator", "research_started", {"topic": "generative AI"})
    trace.add("search", "search_started", {"queries": 3})
    trace.add("search", "search_completed", {"results": 10})
    trace.add("evidence", "evidence_created", {"claims": 5})
    trace.add("critic", "research_approved")
    trace.print_summary()
    trace.print_trace()
    assert trace.count() == 5
    assert trace.has_stage("search")
    assert trace.has_event("research_approved")
    assert len(trace.get_events_by_stage("search")) == 2
    assert trace.stage_counts()["search"] == 2
    print("\nRESEARCH TRACE TEST PASSED")