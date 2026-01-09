#!/usr/bin/env python3
"""
LLM Enhancement Module for Astrological Reports
Translates technical astrological analysis into user-friendly, conversational reports.
Works with local LLMs only - maintains privacy and offline operation.
"""

import json
import requests
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Configuration for local LLM connection."""
    enabled: bool = False
    endpoint: str = "http://localhost:11434/api/generate"  # Default Ollama endpoint
    model: str = "llama2"
    timeout: int = 60
    max_tokens: int = 1000
    temperature: float = 0.7

class LocalLLMEnhancer:
    """Enhances astrological reports using local LLM."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM enhancer with configuration."""
        self.config = config
        self.session = requests.Session()
        self._model_warmed = False

    def is_available(self) -> bool:
        """Check if local LLM is available and responding."""
        if not self.config.enabled:
            return False

        try:
            # First check if Ollama is responding at all
            health_response = self.session.get(
                self.config.endpoint.replace('/api/generate', '/api/tags'),
                timeout=10
            )

            if health_response.status_code != 200:
                return False

            # Test with a simple request and set keep-alive
            response = self.session.post(
                self.config.endpoint,
                json={
                    "model": self.config.model,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "10m",  # Keep model loaded for 10 minutes
                    "options": {"num_predict": 3}
                },
                timeout=300  # Allow 5 minutes for model to load and respond
            )
            if response.status_code == 200:
                self._model_warmed = True
                return True
            return False
        except Exception as e:
            print(f"LLM availability check failed: {e}")
            return False

    def warm_model(self) -> bool:
        """Pre-warm the model to reduce first-request latency."""
        if self._model_warmed:
            return True

        try:
            print("🔥 Warming up AI model...")
            response = self.session.post(
                self.config.endpoint,
                json={
                    "model": self.config.model,
                    "prompt": "Ready",
                    "stream": False,
                    "keep_alive": "20m",  # Keep loaded for processing session
                    "options": {"num_predict": 1}
                },
                timeout=60
            )

            if response.status_code == 200:
                self._model_warmed = True
                print("✅ AI model ready!")
                return True
            else:
                print("⚠️ Model warm-up failed, continuing anyway")
                return False

        except Exception as e:
            print(f"⚠️ Model warm-up failed: {e}, continuing anyway")
            return False

    def enhance_daily_report(self, technical_report: str, day_name: str) -> str:
        """Convert technical daily report to user-friendly format."""
        if not self.config.enabled or not self.is_available():
            return technical_report

        prompt = f"""Please rewrite this astrological analysis for {day_name} in a warm, conversational, and encouraging tone. Make it feel like friendly advice from a knowledgeable astrologer. Keep all the important astrological information but make it more accessible and engaging.

Technical Report:
{technical_report}

Please rewrite this as a friendly, encouraging daily horoscope that:
1. Uses everyday language instead of technical jargon
2. Focuses on practical guidance and opportunities
3. Maintains an optimistic but realistic tone
4. Keeps the specific astrological details but explains them simply
5. Feels personal and supportive

Enhanced Report:"""

        try:
            print(f"  🤖 Enhancing {day_name} report with AI...")
            response = self._call_llm(prompt)
            if response and len(response.strip()) > 100:  # Ensure we got a substantial response
                print(f"  ✅ {day_name} enhancement complete")
                return self._format_enhanced_report(response, "DAILY", day_name)
            else:
                print(f"  ⚠️ {day_name} enhancement returned short response, using technical version")
                return technical_report
        except Exception as e:
            print(f"  ❌ LLM enhancement failed for {day_name}: {e}")
            return technical_report

    def enhance_weekly_summary(self, technical_summary: str) -> str:
        """Convert technical weekly summary to user-friendly format."""
        if not self.config.enabled or not self.is_available():
            return technical_summary

        prompt = f"""Please rewrite this weekly astrological summary in a warm, conversational, and inspiring tone. Make it feel like guidance from a trusted astrologer friend who wants to help navigate the week ahead.

Technical Summary:
{technical_summary}

Please rewrite this as an encouraging weekly overview that:
1. Uses accessible language while keeping astrological accuracy
2. Emphasizes opportunities for growth and positive action
3. Provides practical weekly planning advice
4. Maintains an uplifting but honest perspective
5. Feels like personal guidance tailored to the reader
6. Includes the key dates and themes but explains their significance clearly

Enhanced Summary:"""

        try:
            print("  🤖 Enhancing weekly summary with AI...")
            response = self._call_llm(prompt)
            if response and len(response.strip()) > 100:
                print("  ✅ Weekly summary enhancement complete")
                return self._format_enhanced_report(response, "WEEKLY", "Summary")
            else:
                print("  ⚠️ Weekly enhancement returned short response, using technical version")
                return technical_summary
        except Exception as e:
            print(f"  ❌ LLM enhancement failed for weekly summary: {e}")
            return technical_summary

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Make API call to local LLM with keep-alive and extended timeout."""
        try:
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "15m",  # Keep model loaded during processing
                "options": {
                    "num_predict": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "stop": ["Technical Report:", "Enhanced Report:", "Technical Summary:", "Enhanced Summary:"]
                }
            }

            # Use extended timeout for slow systems
            extended_timeout = max(self.config.timeout, 600)  # Minimum 10 minutes

            response = self.session.post(
                self.config.endpoint,
                json=payload,
                timeout=extended_timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"LLM API error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"LLM request timed out after {extended_timeout} seconds")
            return None
        except Exception as e:
            print(f"LLM request failed: {e}")
            return None

    def _format_enhanced_report(self, enhanced_content: str, report_type: str, day_name: str) -> str:
        """Format the enhanced report with proper headers."""
        header_line = "=" * 60

        if report_type == "DAILY":
            title = f"DAILY ASTROLOGICAL GUIDANCE - {day_name.upper()}"
        else:
            title = "WEEKLY ASTROLOGICAL GUIDANCE"

        formatted = f"""{header_line}
{title}
{header_line}
✨ Enhanced by Local AI Assistant ✨

{enhanced_content}

{header_line}
Generated with local processing - your privacy protected
{header_line}"""

        return formatted

class LLMConfigManager:
    """Manages LLM configuration settings."""

    def __init__(self, config_file: str = "llm_config.json"):
        """Initialize config manager."""
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> LLMConfig:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return LLMConfig(**data)
            except Exception as e:
                print(f"Error loading LLM config: {e}")
                return LLMConfig()
        else:
            # Create default config file
            default_config = LLMConfig()
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: LLMConfig) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config.__dict__, f, indent=2)
        except Exception as e:
            print(f"Error saving LLM config: {e}")

    def get_config(self) -> LLMConfig:
        """Get current configuration."""
        return self.config

    def update_config(self, **kwargs) -> None:
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._save_config(self.config)

    def enable_llm(self, endpoint: str = None, model: str = None) -> None:
        """Enable LLM with optional endpoint and model."""
        updates = {"enabled": True}
        if endpoint:
            updates["endpoint"] = endpoint
        if model:
            updates["model"] = model
        self.update_config(**updates)

    def disable_llm(self) -> None:
        """Disable LLM enhancement."""
        self.update_config(enabled=False)

    def test_connection(self) -> bool:
        """Test LLM connection and return status."""
        enhancer = LocalLLMEnhancer(self.config)
        return enhancer.is_available()

def create_sample_config():
    """Create a sample configuration file with common LLM setups."""
    sample_configs = {
        "ollama_llama2": {
            "enabled": False,
            "endpoint": "http://localhost:11434/api/generate",
            "model": "llama2",
            "timeout": 60,
            "max_tokens": 1000,
            "temperature": 0.7
        },
        "ollama_mistral": {
            "enabled": False,
            "endpoint": "http://localhost:11434/api/generate",
            "model": "mistral",
            "timeout": 60,
            "max_tokens": 1000,
            "temperature": 0.7
        },
        "lm_studio": {
            "enabled": False,
            "endpoint": "http://localhost:1234/v1/chat/completions",
            "model": "local-model",
            "timeout": 60,
            "max_tokens": 1000,
            "temperature": 0.7
        }
    }

    with open("llm_config_examples.json", 'w') as f:
        json.dump(sample_configs, f, indent=2)

    print("Created llm_config_examples.json with sample configurations")

if __name__ == "__main__":
    # Test the LLM enhancer
    config_manager = LLMConfigManager()

    print("LLM Enhancer Test")
    print("=" * 30)
    print(f"Config loaded: {config_manager.config}")
    print(f"LLM Available: {config_manager.test_connection()}")

    if config_manager.test_connection():
        enhancer = LocalLLMEnhancer(config_manager.config)
        test_report = """Today's planetary positions show strong Mercury influence in communication.
        Transit aspects include challenging squares requiring patience."""

        enhanced = enhancer.enhance_daily_report(test_report, "Monday")
        print("\nEnhanced Report:")
        print(enhanced)
    else:
        print("\nTo use LLM enhancement:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Run: ollama run llama2")
        print("3. Update llm_config.json to enable LLM")
        create_sample_config()