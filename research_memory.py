import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class ResearchMemory:
    """
    Persistent memory for previous research runs.
    Memory is stored locally as JSON so the system can later
    be upgraded to ChromaDB / FAISS / another vector database.
    """

    def __init__(self, memory_file: str = "data/research_memory.json",):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.memory: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """
        Load existing research memory from disk.
        """
        if not self.memory_file.exists():
            self.memory = []
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8",) as file:
                data = json.load(file)
            if isinstance(data, list):
                self.memory = data
            else:
                self.memory = []

        except (json.JSONDecodeError, OSError,):
            self.memory = []

    def _save(self):
        """
        Persist memory to disk.
        """

        with open(
            self.memory_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.memory,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def create_research_run(self, topic: str,) -> str:
        """
        Create a new research run.

        Returns:
            Unique research run ID.
        """

        run_id = (datetime.now().strftime("%Y%m%d%H%M%S%f"))

        research_run = {
            "run_id": run_id,
            "topic": topic,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "sources": [],
            "claims": [],
            "evidence": [],
            "report": None,
        }

        self.memory.append(research_run)
        self._save()
        return run_id


    def get_research_run(self,run_id: str,) -> Optional[Dict[str, Any]]:
        """
        Retrieve a research run by ID.
        """
        for run in self.memory:
            if run.get("run_id") == run_id:
                return run

        return None


    def find_by_topic(self, topic: str,) -> List[Dict[str, Any]]:
        """
        Find previous research runs containing
        the supplied topic text.
        """
        query = topic.lower().strip()
        if not query:
            return []
        matches = []
        for run in self.memory:
            stored_topic = (run.get("topic", "").lower())
            if query in stored_topic:
                matches.append(run)
        return matches


    def add_source(
        self,
        run_id: str,
        source: Dict[str, Any],
    ) -> bool:
        """
        Add a source to a research run.
        Duplicate URLs are ignored.
        """
        run = self.get_research_run(run_id)
        if run is None:
            return False
        source_url = source.get("url", "",)
        for existing in run["sources"]:
            if (source_url and existing.get("url")== source_url):
                return False

        run["sources"].append(source)
        self._touch(run)
        self._save()
        return True

    def add_claim(
        self,
        run_id: str,
        claim: Dict[str, Any],
    ) -> bool:
        """
        Add a research claim.
        """
        run = self.get_research_run(run_id)
        if run is None:
            return False
        run["claims"].append(claim)
        self._touch(run)
        self._save()
        return True


    def add_evidence(
        self,
        run_id: str,
        evidence: Dict[str, Any],
    ) -> bool:
        """
        Add evidence information.
        """
        run = self.get_research_run(run_id)
        if run is None:
            return False
        run["evidence"].append(evidence)
        self._touch(run)
        self._save()
        return True


    def store_report(
        self,
        run_id: str,
        report: Dict[str, Any],
    ) -> bool:
        """
        Store the final research report.
        """
        run = self.get_research_run(run_id)
        if run is None:
            return False
        run["report"] = report
        self._touch(run)
        self._save()
        return True

    def source_exists(
        self,
        url: str,
    ) -> bool:
        """
        Check whether a URL already exists
        anywhere in research memory.
        """
        if not url:
            return False
        for run in self.memory:
            for source in run.get("sources", [],):
                if source.get("url") == url:
                    return True
        return False


    def get_all_sources(self,) -> List[Dict[str, Any]]:
        """
        Return all previously stored sources.
        """
        sources = []
        for run in self.memory:
            sources.extend(run.get("sources", [],))
        return sources


    def get_all_claims(self,) -> List[Dict[str, Any]]:
        """
        Return all previously stored claims.
        """
        claims = []
        for run in self.memory:
            claims.extend(run.get("claims", [],))
        return claims


    def search_memory(
        self,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Perform simple keyword-based retrieval
        across topics, claims and source metadata.
        This is intentionally deterministic.
        Later this can be replaced by semantic/vector
        retrieval.
        """
        query = query.lower().strip()
        if not query:
            return []
        results = []
        for run in self.memory:
            searchable_parts = [run.get("topic", ""),]
            for claim in run.get("claims",[],):
                searchable_parts.extend(
                    [
                        str(claim.get("claim","",)),
                        str(claim.get("text", "",)),
                    ]
                )

            for source in run.get("sources",[],):
                searchable_parts.extend(
                    [
                        str(source.get("title", "",)),
                        str(source.get("url", "",)),
                        str(source.get("content", "",)),
                    ]
                )

            searchable_text = " ".join(searchable_parts).lower()
            if query in searchable_text:
                results.append(run)
        return results

    def statistics(self,) -> Dict[str, int]:
        """
        Return basic memory statistics.
        """
        source_count = 0
        claim_count = 0
        evidence_count = 0
        reports = 0
        for run in self.memory:
            source_count += len(run.get("sources", [],))
            claim_count += len(run.get("claims", [],))
            evidence_count += len(run.get("evidence", [],))
            if run.get("report") is not None:
                reports += 1

        return {
            "research_runs": len(self.memory),
            "sources": source_count,
            "claims": claim_count,
            "evidence": evidence_count,
            "reports": reports,
        }


    def to_dict(self,) -> List[Dict[str, Any]]:
        """
        Return a copy of the complete memory.
        """
        return json.loads(json.dumps(self.memory))

    def clear(self):
        """
        Delete all research memory.
        """
        self.memory = []
        self._save()


    def _touch(self,run: Dict[str, Any],):
        run["updated_at"] = (datetime.now().isoformat(timespec="seconds"))



if __name__ == "__main__":
    print("=" * 70)
    print("RESEARCH MEMORY MODULE TEST")
    print("=" * 70)
    test_memory_file = ("data/test_research_memory.json")
    memory = ResearchMemory(memory_file=test_memory_file)
    memory.clear()
    run_id = memory.create_research_run("impact of generative AI on software development")
    print(f"\nResearch run created: {run_id}")
    assert run_id
    source_1 = {
        "title": "Generative AI Research Paper",
        "url": "https://example.com/research-paper",
        "source_type": "research",
        "content": (
            "Generative AI can improve "
            "software development productivity."
        ),
    }

    source_2 = {
        "title": "AI Security Article",
        "url": "https://example.com/security",
        "source_type": "technical",
        "content": (
            "Generative AI can introduce "
            "security risks."
        ),
    }

    assert memory.add_source(run_id, source_1,)
    assert memory.add_source(run_id, source_2,)
    duplicate_added = memory.add_source(run_id,source_1,)
    assert duplicate_added is False
    print("Source storage test passed.")
    claim_1 = {
        "claim": (
            "Generative AI can improve "
            "developer productivity."
        ),
        "source_url": (
            "https://example.com/research-paper"
        ),
    }

    claim_2 = {
        "claim": (
            "Generative AI can introduce "
            "security risks."
        ),
        "source_url": (
            "https://example.com/security"
        ),
    }

    assert memory.add_claim(run_id,claim_1,)
    assert memory.add_claim(run_id,claim_2,)
    print("Claim storage test passed.")
    evidence = {
        "claim": claim_1["claim"],
        "support_level": "SUPPORTED",
        "source_count": 1,
    }
    assert memory.add_evidence(
        run_id,
        evidence,
    )
    print("Evidence storage test passed.")

    report = {
        "title": (
            "Impact of Generative AI "
            "on Software Development"
        ),
        "summary": (
            "Generative AI provides "
            "productivity opportunities "
            "while introducing new risks."
        ),
    }

    assert memory.store_report(run_id,report,)
    print("Report storage test passed.")
    retrieved = memory.get_research_run(run_id)
    assert retrieved is not None
    assert (retrieved["topic"]== "impact of generative AI on software development")
    assert len(retrieved["sources"]) == 2
    assert len(retrieved["claims"]) == 2
    assert len(retrieved["evidence"]) == 1
    assert (retrieved["report"] is not None)
    print("Research retrieval test passed.")

    topic_results = memory.find_by_topic("generative AI")
    assert len(topic_results) == 1
    print("Topic search test passed." )
    assert memory.source_exists("https://example.com/research-paper")
    assert not memory.source_exists("https://example.com/not-found" )
    print("Source existence test passed.")
    search_results = memory.search_memory("security")
    assert len(search_results) == 1
    print("Keyword memory search test passed.")
    stats = memory.statistics()
    print(f"\nMemory statistics: {stats}")
    assert stats["research_runs"] == 1
    assert stats["sources"] == 2
    assert stats["claims"] == 2
    assert stats["evidence"] == 1
    assert stats["reports"] == 1
    print("Memory statistics test passed.")

    new_memory = ResearchMemory(memory_file=test_memory_file)
    persisted_run = (new_memory.get_research_run(run_id))
    assert persisted_run is not None
    assert len(persisted_run["sources"]) == 2
    print("Persistence test passed.")
    exported = new_memory.to_dict()
    assert isinstance(exported,list,)
    assert len(exported) == 1
    print("Memory export test passed.")
    new_memory.clear()
    assert new_memory.statistics()["research_runs"] == 0
    if new_memory.memory_file.exists():
        new_memory.memory_file.unlink()
    print("\n" + "=" * 70)
    print("RESEARCH MEMORY MODULE TEST PASSED")
    print("=" * 70)