from functools import lru_cache
from ..config import get_settings

class GeminiServiceError(RuntimeError):
    pass

@lru_cache
def get_client():
    try:
        from google import genai
    except ImportError as exc:
        raise GeminiServiceError(
            "The Google GenAI SDK is not installed. Run: pip install -r requirements.txt"
        ) from exc
    key=get_settings().gemini_api_key
    if not key:
        raise GeminiServiceError("GEMINI_API_KEY is not configured. Set it in .env or enable MOCK_AI=true.")
    return genai.Client(api_key=key)

def generate_structured(model, prompt, schema):
    try:
        from google.genai import types
        response=get_client().models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.4,
            ),
        )
        if not response.text:
            raise GeminiServiceError("Gemini returned an empty response.")
        return schema.model_validate_json(response.text)
    except GeminiServiceError:
        raise
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc
