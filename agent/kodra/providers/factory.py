from typing import Optional
from kodra.config import settings
from kodra.providers.base import BaseLLMProvider
from kodra.providers.mock_provider import MockProvider
from kodra.providers.openai_provider import OpenAIProvider
from kodra.providers.anthropic_provider import AnthropicProvider
from kodra.providers.gemini_provider import GeminiProvider
from kodra.providers.ollama_provider import OllamaProvider


class ProviderFactory:
    @staticmethod
    def get_provider(
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> BaseLLMProvider:
        name = (provider_name or settings.provider or "mock").lower().strip()

        if name == "mock":
            return MockProvider()

        if name == "openai":
            key = api_key or settings.openai_api_key
            m = model or settings.model or "gpt-4o"
            return OpenAIProvider(api_key=key, model=m)

        if name == "anthropic":
            key = api_key or settings.anthropic_api_key
            m = model or settings.model or "claude-3-5-sonnet-20241022"
            return AnthropicProvider(api_key=key, model=m)

        if name == "gemini":
            key = api_key or settings.gemini_api_key
            m = model or settings.model or "gemini-2.5-flash"
            return GeminiProvider(api_key=key, model=m)

        if name == "ollama":
            m = model or settings.model or "llama3"
            return OllamaProvider(host=settings.ollama_host, model=m)

        if name == "groq":
            key = api_key or settings.groq_api_key
            m = model or settings.model or "llama-3.3-70b-versatile"
            return OpenAIProvider(
                api_key=key,
                model=m,
                base_url="https://api.groq.com/openai/v1",
            )

        # Fallback to MockProvider if unknown
        return MockProvider()
