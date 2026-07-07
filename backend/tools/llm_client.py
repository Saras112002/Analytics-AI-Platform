from openai import OpenAI
from backend.config import get_settings

settings = get_settings()


class LLMClient:
    """
    A wrapper around OpenRouter API
    Uses the openai library because OpenRouter is OpenAI-compatible
    """

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY
        )
        self.model = "poolside/laguna-xs-2.1:free"
        self.max_tokens = 2000

    def ask(self, prompt: str, system_prompt: str = None) -> str:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            for attempt in range(2):   # try twice before giving up
                try:
                    response = self.client.chat.completions.create(
                        model=self.model, messages=messages, max_tokens=self.max_tokens,
                    )
                except Exception as e:
                    if attempt == 0:
                        continue
                    return f'{{"error": "LLM request failed: {str(e)}"}}'
                content = response.choices[0].message.content if response.choices else None
                if content and content.strip():
                    return content
            return '{"error": "LLM returned empty response after retry"}'


# Create one shared instance the whole app can use
llm = LLMClient()