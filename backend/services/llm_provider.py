import abc
from typing import NamedTuple


class TokenUsage(NamedTuple):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def complete(self, system_prompt: str, user_message: str) -> tuple[str, TokenUsage]:
        """Sendet einen System+User-Turn und gibt (Rohtext, TokenUsage) zurück."""
        ...


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        from groq import Groq
        self._client = Groq(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def complete(self, system_prompt: str, user_message: str) -> tuple[str, TokenUsage]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        u = response.usage
        usage = TokenUsage(
            prompt_tokens=u.prompt_tokens if u else 0,
            completion_tokens=u.completion_tokens if u else 0,
            total_tokens=u.total_tokens if u else 0,
        )
        return response.choices[0].message.content.strip(), usage
