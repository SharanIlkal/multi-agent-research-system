from typing import Any
from langchain_core.runnables import RunnableLambda
from llm_factory import (
    get_fallback_llm,
    get_primary_llm,
    is_retryable_error,
)

def _invoke_model(
    primary_llm,
    fallback_llm,
    input_data: Any,
):
    """
    Invoke the primary model.
    If a temporary Gemini/API error occurs, switch to
    the fallback model.
    """
    try:
        return primary_llm.invoke(input_data)
    except Exception as primary_error:
        print("\n[RESILIENT LLM] Primary model failed.")

        print(
            f"[RESILIENT LLM] Error: "
            f"{primary_error}"
        )

        if not is_retryable_error(primary_error):
            raise
        print("[RESILIENT LLM] Switching to fallback model...")

        try:
            return fallback_llm.invoke(input_data)
        except Exception as fallback_error:
            raise RuntimeError(
                "Both Gemini models failed.\n"
                f"Primary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            ) from fallback_error


def create_resilient_llm():
    """
    Create a LangChain Runnable that automatically
    falls back from the primary Gemini model to the
    fallback Gemini model.
    """
    primary_llm = get_primary_llm()
    fallback_llm = get_fallback_llm()
    return RunnableLambda(
        lambda input_data: _invoke_model(
            primary_llm,
            fallback_llm,
            input_data,
        )
    )


if __name__ == "__main__":
    print("Resilient LLM module loaded successfully.")
    resilient_llm = create_resilient_llm()
    print(
        f"Runnable created: "
        f"{type(resilient_llm).__name__}"
    )