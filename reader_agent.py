import io
from typing import List
import pymupdf
import requests
from bs4 import BeautifulSoup
from schemas import ResearchSource, SearchResult
from tools import scrape_url

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
}


def detect_source_type(url: str, title: str = "") -> str:
    text = f"{url} {title}".lower()
    if "arxiv.org" in text:
        return "research_paper"
    if ".edu" in text:
        return "academic"
    if ".gov" in text:
        return "government"
    if ".org" in text:
        return "research_organization"
    if "github.com" in text:
        return "technical_repository"
    if any(domain in text for domain in ["reuters.com", "bbc.com", "apnews.com", "nytimes.com"]):
        return "news"
    if any(keyword in text for keyword in ["research", "paper", "journal", "conference"]):
        return "research"
    return "web"


def is_pdf_url(url: str) -> bool:
    value = url.lower()
    return ".pdf" in value or "/download" in value or "bitstreams/" in value


def scrape_pdf(url: str, max_length: int = 12000) -> str:
    try:
        response = requests.get(url, timeout=30, headers=REQUEST_HEADERS)
        response.raise_for_status()
        document = pymupdf.open(stream=io.BytesIO(response.content), filetype="pdf")
        pages = []
        total = 0
        for page in document:
            text = page.get_text("text") or ""
            if text:
                pages.append(text)
                total += len(text)
            if total >= max_length:
                break
        document.close()
        return "\n".join(pages).replace("\x00", "").strip()[:max_length]
    except Exception as exc:
        print(f"[PDF READER] Failed: {exc}")
        return ""


def scrape_webpage(url: str) -> str:
    try:
        content = scrape_url.invoke(url)
        if content and not content.startswith("Could not scrape URL") and not content.startswith("Web search failed"):
            return content.strip()
    except Exception as exc:
        print(f"[WEB READER] Tool failed: {exc}")
    try:
        response = requests.get(url, timeout=20, headers=REQUEST_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())
        return text[:12000]
    except Exception as exc:
        print(f"[WEB READER] Direct request failed: {exc}")
        return ""


def read_source(search_result: SearchResult) -> ResearchSource:
    print(f"\n[READER] Reading: {search_result.title}")
    print(f"[READER] URL: {search_result.url}")
    content = scrape_pdf(search_result.url) if is_pdf_url(search_result.url) else scrape_webpage(search_result.url)
    if not content and search_result.snippet:
        content = search_result.snippet.strip()
        print("[READER] Using Tavily result content as fallback evidence.")
    return ResearchSource(
        title=search_result.title,
        url=search_result.url,
        content=content,
        source_type=detect_source_type(search_result.url, search_result.title),
    )


def read_sources(search_results: List[SearchResult], max_sources: int = 8, candidate_multiplier: int = 3) -> List[ResearchSource]:
    if not search_results or max_sources <= 0:
        return []
    candidate_limit = min(len(search_results), max(max_sources + 5, max_sources * candidate_multiplier))
    selected_results = search_results[:candidate_limit]
    sources = []
    seen_urls = set()
    print(f"\n[READER] Target sources: {max_sources}")
    print(f"[READER] Candidates to process: {len(selected_results)}")
    for index, result in enumerate(selected_results, start=1):
        normalized_url = result.url.strip().rstrip("/").lower()
        if not normalized_url or normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)
        print(f"\n[READER] Candidate {index}/{len(selected_results)}")
        source = read_source(result)
        if source.content and len(source.content.strip()) >= 200:
            sources.append(source)
            print(f"[READER] Accepted source {len(sources)}/{max_sources} ({len(source.content)} chars).")
            if len(sources) >= max_sources:
                break
        else:
            print("[READER] Rejected: insufficient readable content.")
    print(f"\n[READER] Successfully read {len(sources)} sources from {len(selected_results)} candidates.")
    return sources


def get_source_statistics(sources: List[ResearchSource]) -> dict:
    if not sources:
        return {"total_sources": 0, "total_characters": 0, "average_characters": 0}
    total_characters = sum(len(source.content) for source in sources)
    return {
        "total_sources": len(sources),
        "total_characters": total_characters,
        "average_characters": round(total_characters / len(sources)),
    }


if __name__ == "__main__":
    from search_service import search_web
    results = search_web("impact of generative AI on software development", max_results=10)
    sources = read_sources(results, max_sources=5)
    print(get_source_statistics(sources))
