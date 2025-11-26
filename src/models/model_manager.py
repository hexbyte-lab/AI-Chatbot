"""
Model loading and management.
"""

import yaml
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


class ModelManager:
    """Manages model loading and configuration."""

    def __init__(self, config_path="config/config.yaml"):
        """Initialize model manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = self._get_device()

    def _load_config(self):
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def _get_device(self):
        """Detect available device (CUDA, MPS, or CPU).
        
        Returns:
            Device string
        """
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def load_model(self, progress_callback=None):
        """Load model and tokenizer.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful
        """
        try:
            model_config = self.config["model"]
            model_name = model_config["name"]
            
            if progress_callback:
                progress_callback(f"Loading tokenizer: {model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            if progress_callback:
                progress_callback(f"Loading model: {model_name} (this may take a while...)")
            
            # Configure quantization if enabled
            quantization_config = None
            if model_config.get("load_in_4bit", False):
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Determine dtype
            dtype_str = model_config.get("torch_dtype", "float16")
            dtype = getattr(torch, dtype_str) if dtype_str != "auto" else "auto"
            
            # Load model with device detection
            device_map = self.device if self.device == "cpu" else "auto"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map=device_map,
                torch_dtype=dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            self.is_loaded = True
            
            if progress_callback:
                progress_callback(f"Model loaded successfully on {self.device}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e

    def get_generation_config(self):
        """Get generation configuration.
        
        Returns:
            Dictionary of generation parameters
        """
        return self.config.get("generation", {})

    def get_ui_config(self):
        """Get UI configuration.
        
        Returns:
            Dictionary of UI parameters
        """
        return self.config.get("ui", {})

    def get_logging_config(self):
        """Get logging configuration.
        
        Returns:
            Dictionary of logging parameters
        """
        return self.config.get("logging", {})

    def unload_model(self):
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        self.is_loaded = False
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

