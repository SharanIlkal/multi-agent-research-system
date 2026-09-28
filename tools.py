# import os
# import requests
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from langchain.tools import tool
# from tavily import TavilyClient
# from config import (
#     MAX_SCRAPED_CONTENT_LENGTH,
#     TAVILY_MAX_RESULTS,
# )

# load_dotenv()
# tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# @tool
# def web_search(query: str) -> str:
#     """
#     Search the web for recent and reliable information.
#     Returns titles, URLs and snippets.
#     """
#     try:

#         results = tavily.search(
#             query=query,
#             max_results=TAVILY_MAX_RESULTS
#         )
#         output = []
#         for result in results.get("results", []):
#             title = result.get("title", "Untitled")
#             url = result.get( "url","")
#             content = result.get("content","")
#             output.append(
#                 f"Title: {title}\n"
#                 f"URL: {url}\n"
#                 f"Snippet: {content[:500]}"
#             )
#         if not output:
#             return "No search results found."
#         return "\n\n----\n\n".join(output)
#     except Exception as exc:
#         return (
#             "Web search failed.\n"
#             f"Error: {str(exc)}"
#         )


# @tool
# def scrape_url(url: str) -> str:
#     """
#     Scrape readable text from a URL using BeautifulSoup.
#     """
#     try:
#         response = requests.get(
#             url,
#             timeout=15,
#             headers={
#                 "User-Agent": (
#                     "Mozilla/5.0 "
#                     "(Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 "
#                     "(KHTML, like Gecko) "
#                     "Chrome/131.0 Safari/537.36"
#                 )
#             }
#         )
#         response.raise_for_status()
#         soup = BeautifulSoup(
#             response.text,
#             "html.parser"
#         )

#         for tag in soup([
#             "script",
#             "style",
#             "nav",
#             "footer",
#             "header",
#             "noscript",
#             "svg"
#         ]):

#             tag.decompose()

#         text = soup.get_text(
#             separator=" ",
#             strip=True
#         )

#         text = " ".join(text.split())
#         return text[:MAX_SCRAPED_CONTENT_LENGTH]
#     except requests.RequestException as exc:
#         return (
#             "Could not scrape URL.\n"
#             f"Request error: {str(exc)}"
#         )
#     except Exception as exc:
#         return (
#             "Could not scrape URL.\n"
#             f"Error: {str(exc)}"
#         )


import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from tavily import TavilyClient
from config import (
    TAVILY_API_KEY,
    TAVILY_MAX_RESULTS,
    MAX_SCRAPED_CONTENT_LENGTH,
)

tavily = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a topic.
    Returns titles, URLs and snippets from multiple results.
    """

    try:
        results = tavily.search(
            query=query,
            max_results=TAVILY_MAX_RESULTS,
        )
        output = []
        for result in results.get("results", []):
            output.append(
                f"Title: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Snippet: "
                f"{result.get('content', '')[:500]}"
            )
        if not output:
            return "No search results found."
        return "\n\n----\n\n".join(output)
    except Exception as exc:
        return (
            "Web search failed.\n"
            f"Error: {str(exc)}"
        )


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and return clean text content from a given URL
    for deeper reading.
    """
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                    "Mozilla/5.0 (ResearchBot/1.0)"
            },
        )

        response.raise_for_status()
        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        return text[:MAX_SCRAPED_CONTENT_LENGTH]
    except Exception as exc:
        return (
            "Could not scrape URL.\n"
            f"Error: {str(exc)}"
        )