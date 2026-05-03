"""
AI Configuration
================
Central config for AI provider.
To switch from Ollama to OpenAI/Anthropic later,
only change this file.
"""

class AIConfig:
    # ── Provider ──────────────────────────────────────────────
    PROVIDER = 'ollama'

    # ── Ollama (local) ────────────────────────────────────────
    OLLAMA_BASE_URL = 'http://localhost:11434'
    OLLAMA_MODEL    = 'qwen3:8b' # Tool Calling Model
    
    # ── Agent settings ────────────────────────────────────────
    MAX_RESULTS      = 50           # max rows shown in chat
    MAX_RETRIES      = 2            # SQL retry attempts on error
    MEMORY_WINDOW    = 3            # last N exchanges to remember
    TEMPERATURE      = 0            # 0 = deterministic SQL generation
    MAX_ITERATIONS   = 5           # max agent reasoning steps
    VERBOSE          = True

    @staticmethod
    def get_llm():
        """
        Returns the configured LLM instance.
        Switch provider here — processors don't need to change.
        """
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model       = AIConfig.OLLAMA_MODEL,
            base_url    = AIConfig.OLLAMA_BASE_URL,
            temperature = AIConfig.TEMPERATURE,
        )