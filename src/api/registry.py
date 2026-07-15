"""ProviderRegistry - Multi-model registration and selection."""
class ProviderRegistry:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._default_provider_id = "deepseek"
        return cls._instance

    def register(self, provider):
        self._providers[provider.provider_id] = provider

    def get(self, provider_id):
        return self._providers.get(provider_id)

    def get_default(self):
        return self._providers.get(self._default_provider_id)

    def list_providers(self):
        return [{"id":p.provider_id,"default_model":p.default_model} for p in self._providers.values()]

    @classmethod
    def from_settings(cls, storage):
        registry = cls()
        from src.api.deepseek import DeepSeekProvider
        from src.api.openai_compat import OpenAICompatProvider
        has_any = False
        deepseek_key = storage.get_credential("deepseek_api_key")
        if deepseek_key:
            url = storage.get_config("deepseek_base_url","https://api.deepseek.com/v1")
            registry.register(DeepSeekProvider(api_key=deepseek_key, base_url=url))
            has_any = True
        openai_key = storage.get_credential("openai_api_key")
        if openai_key:
            url = storage.get_config("openai_base_url","https://api.openai.com/v1")
            registry.register(OpenAICompatProvider("openai", openai_key, url))
            has_any = True
        groq_key = storage.get_credential("groq_api_key")
        if groq_key:
            registry.register(OpenAICompatProvider("groq", groq_key, "https://api.groq.com/openai/v1"))
            has_any = True
        ollama_url = storage.get_config("ollama_base_url","")
        if ollama_url:
            registry.register(OpenAICompatProvider("ollama","ollama",ollama_url))
            has_any = True
        # Always register a fallback DeepSeek provider (will prompt for API key in UI)
        if not has_any:
            registry.register(DeepSeekProvider(api_key="", base_url="https://api.deepseek.com/v1"))
        return registry
