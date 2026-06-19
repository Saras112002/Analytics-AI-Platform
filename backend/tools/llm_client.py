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
        self.model = "openrouter/free"
        self.max_tokens = 2000

    def ask(self, prompt: str, system_prompt: str = None) -> str:
        """
        Send a message to the LLM and get a response back

        prompt:        The actual question or task
        system_prompt: Optional - tells the AI what role to play
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content


# Create one shared instance the whole app can use
llm = LLMClient()