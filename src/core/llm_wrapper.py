"""
Unified LLM wrapper supporting multiple backends via LiteLLM.
Enables easy switching between local models and cloud APIs.
"""

import os
from typing import List, Dict, Optional, Iterator, Any
from pathlib import Path
import yaml


class LLMWrapper:
    """Universal LLM wrapper with multi-backend support."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize LLM wrapper.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.backend = self.config.get("model", {}).get("backend", "local")
        self.model_name = self.config.get("model", {}).get("name")

        # Try to use LiteLLM if available, fallback to transformers
        self.use_litellm = self._check_litellm()

        if self.use_litellm and self.backend != "local":
            self._init_litellm()
        else:
            # Use existing local transformers setup
            from src.models.model_manager import ModelManager

            self.model_manager = ModelManager(config_path)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML."""
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _check_litellm(self) -> bool:
        """Check if LiteLLM is available."""
        try:
            import litellm

            return True
        except ImportError:
            return False

    def _init_litellm(self):
        """Initialize LiteLLM configuration."""
        import litellm

        # Set API keys from environment or config
        backend_config = self.config.get("model", {}).get("backend_config", {})

        if self.backend == "openai":
            litellm.openai_key = backend_config.get("api_key") or os.getenv(
                "OPENAI_API_KEY"
            )
        elif self.backend == "anthropic":
            litellm.anthropic_key = backend_config.get("api_key") or os.getenv(
                "ANTHROPIC_API_KEY"
            )
        elif self.backend == "cohere":
            litellm.cohere_key = backend_config.get("api_key") or os.getenv(
                "COHERE_API_KEY"
            )

        # Enable streaming and logging
        litellm.set_verbose = backend_config.get("verbose", False)

    def load_model(self, progress_callback=None):
        """Load model (only needed for local models).

        Args:
            progress_callback: Optional progress callback

        Returns:
            True if successful
        """
        if self.use_litellm and self.backend != "local":
            if progress_callback:
                progress_callback(
                    f"✅ Using {self.backend} backend - no local model needed"
                )
            return True
        else:
            # Load local model via transformers
            return self.model_manager.load_model(progress_callback)

    def generate(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Iterator[str] | str:
        """Generate response from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream response
            **kwargs: Additional generation parameters

        Returns:
            Generated response (string or iterator)
        """
        # Merge config parameters with kwargs
        gen_config = self.config.get("generation", {})
        params = {**gen_config, **kwargs}

        if self.use_litellm and self.backend != "local":
            return self._generate_litellm(messages, stream, **params)
        else:
            return self._generate_local(messages, stream, **params)

    def _generate_litellm(
        self, messages: List[Dict[str, str]], stream: bool, **params
    ) -> Iterator[str] | str:
        """Generate using LiteLLM (cloud APIs).

        Args:
            messages: Message list
            stream: Stream response
            **params: Generation parameters

        Returns:
            Response text or iterator
        """
        import litellm

        # Map parameters to LiteLLM format
        litellm_params = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_new_tokens", 512),
            "top_p": params.get("top_p", 0.9),
        }

        response = litellm.completion(**litellm_params)

        if stream:
            # Return iterator of content chunks
            def stream_generator():
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            return stream_generator()
        else:
            return response.choices[0].message.content

    def _generate_local(
        self, messages: List[Dict[str, str]], stream: bool, **params
    ) -> Iterator[str] | str:
        """Generate using local transformers model.

        Args:
            messages: Message list
            stream: Stream response
            **params: Generation parameters

        Returns:
            Response text or iterator
        """
        if stream:
            # Use streaming generator
            from transformers import TextIteratorStreamer
            import threading

            device = self.model_manager.device
            inputs = self.model_manager.tokenizer.apply_chat_template(
                messages, return_tensors="pt", add_generation_prompt=True
            ).to(device)

            streamer = TextIteratorStreamer(
                self.model_manager.tokenizer, skip_prompt=True, skip_special_tokens=True
            )

            generation_kwargs = {
                "inputs": inputs,
                "streamer": streamer,
                "max_new_tokens": params.get("max_new_tokens", 512),
                "do_sample": params.get("do_sample", True),
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.9),
                "top_k": params.get("top_k", 50),
            }

            thread = threading.Thread(
                target=self.model_manager.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Return iterator
            return streamer
        else:
            # Non-streaming generation
            device = self.model_manager.device
            inputs = self.model_manager.tokenizer.apply_chat_template(
                messages, return_tensors="pt", add_generation_prompt=True
            ).to(device)

            outputs = self.model_manager.model.generate(
                inputs,
                max_new_tokens=params.get("max_new_tokens", 512),
                do_sample=params.get("do_sample", True),
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.9),
                top_k=params.get("top_k", 50),
            )

            response = self.model_manager.tokenizer.decode(
                outputs[0][inputs.shape[1] :], skip_special_tokens=True
            )

            return response

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        if self.use_litellm and self.backend != "local":
            return True  # API backends don't need loading
        return self.model_manager.is_loaded

    @property
    def device(self) -> str:
        """Get device (for local models)."""
        if self.use_litellm and self.backend != "local":
            return "cloud"
        return self.model_manager.device

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information.

        Returns:
            Model info dictionary
        """
        return {
            "backend": self.backend,
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "uses_litellm": self.use_litellm and self.backend != "local",
        }
