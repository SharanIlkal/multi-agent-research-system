import os
from dotenv import load_dotenv
load_dotenv()

try:
    import streamlit as st

    for key in [
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "TAVILY_API_KEY",
        "GEMINI_MODEL",
        "GEMINI_FALLBACK_MODEL",
        "GEMINI_TEMPERATURE",
        "GEMINI_MAX_RETRIES",
        "TAVILY_MAX_RESULTS",
        "MAX_SEARCH_CONTENT_LENGTH",
        "MAX_SCRAPED_CONTENT_LENGTH",
        "MAX_EVIDENCE_LENGTH",
    ]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])

except Exception:
    pass

GOOGLE_API_KEY = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0"))
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
MAX_SEARCH_CONTENT_LENGTH = int(os.getenv("MAX_SEARCH_CONTENT_LENGTH", "12000"))
MAX_SCRAPED_CONTENT_LENGTH = int(os.getenv("MAX_SCRAPED_CONTENT_LENGTH", "6000"))
MAX_EVIDENCE_LENGTH = int(os.getenv("MAX_EVIDENCE_LENGTH", "15000"))


def validate_config():
    missing = []
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY or GEMINI_API_KEY")

    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")

    if missing:
        raise RuntimeError(
            "Missing required environment variables:\n"
            + "\n".join(
                f"- {item}"
                for item in missing
            )
        )


if __name__ == "__main__":
    validate_config()
    print("Configuration loaded successfully.")
    print(f"Primary Gemini model: {GEMINI_MODEL}")
    print(f"Fallback Gemini model: {GEMINI_FALLBACK_MODEL}")
    print(f"Tavily max results: {TAVILY_MAX_RESULTS}")