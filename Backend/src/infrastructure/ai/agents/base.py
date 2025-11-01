import time

import tiktoken
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.core.utils.logger import get_logger


class BaseWorkflow:
    def __init__(self, llm_model: str, provider: str):
        self.llm_model = llm_model
        self.provider = provider.lower()
        self._llm = None  # lazy init
        self.logger = get_logger(__name__)

        try:
            self.tokenizer = tiktoken.encoding_for_model(llm_model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    @property
    def llm(self):
        """Lazy initialization of LLM instance"""
        if self._llm is None:
            self._llm = self._get_llm_provider(self.provider, self.llm_model)
            self.logger.info(
                f"Initialized LLM provider: {self.provider} ({self.llm_model})"
            )
        return self._llm

    def _get_llm_provider(self, provider: str, model: str):
        """Return the appropriate LLM instance based on provider."""
        if provider == "openai":
            return ChatOpenAI(model=model)
        elif provider == "anthropic":
            return ChatAnthropic(
                model_name=model,
                temperature=0.7,
                timeout=60,  # default timeout 60 detik
                stop=None,
            )
        elif provider == "google":
            return ChatGoogleGenerativeAI(model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0):
        """Retry function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(
                        f"Max retries ({max_retries}) exceeded. Last error: {str(e)}"
                    )
                    raise
                delay = base_delay * (2**attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using tiktoken"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Error estimating tokens: {str(e)}")
            return len(text) // 4  # fallback

    def estimate_structured_output_tokens(
        self, prompt: str, response_content: str = ""
    ) -> int:
        """Estimate tokens for structured output calls"""
        try:
            input_tokens = self.estimate_tokens(prompt)
            output_tokens = (
                self.estimate_tokens(response_content) if response_content else 50
            )
            return input_tokens + output_tokens + 20
        except Exception as e:
            self.logger.warning(f"Error estimating structured output tokens: {str(e)}")
            return 100

    async def call_llm(self, messages):
        """Generalized method to call LLM (async or sync safe)."""
        try:
            llm = self.llm

            if hasattr(llm, "ainvoke"):
                response = await llm.ainvoke(messages)
            elif hasattr(llm, "invoke"):
                response = llm.invoke(messages)
            else:
                raise TypeError("Provided LLM does not support invoke/ainvoke.")

            return response
        except Exception as e:
            self.logger.error(f"Error while invoking LLM: {e}")
            raise
