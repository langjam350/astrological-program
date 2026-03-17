#!/usr/bin/env python3
"""
LLM Enhancement Module for Astrological Reports
Supports multiple AI providers: local (Ollama), OpenAI, Claude, and Gemini.
API keys must be configured in llm_config.json before use.
"""

import json
import requests
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""
    endpoint: str = ""
    model: str = ""
    api_key: str = ""


@dataclass
class LLMConfig:
    """Configuration for LLM connections."""
    default_provider: str = "none"
    timeout: int = 120
    max_tokens: int = 1000
    temperature: float = 0.7
    providers: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get provider config by name."""
        if name in self.providers:
            return ProviderConfig(**self.providers[name])
        return None


class LLMEnhancer:
    """Enhances astrological reports using configurable LLM providers."""

    SUPPORTED_PROVIDERS = ["local", "openai", "claude", "gemini"]

    def __init__(self, config: LLMConfig, provider: str = None):
        """Initialize LLM enhancer with configuration and provider choice."""
        self.config = config
        self.provider_name = provider or config.default_provider
        self.provider = config.get_provider(self.provider_name) if self.provider_name != "none" else None
        self.session = requests.Session()
        self._model_warmed = False

    def is_available(self) -> bool:
        """Check if selected LLM provider is available."""
        if not self.provider or self.provider_name == "none":
            return False

        if self.provider_name == "local":
            return self._check_local()
        else:
            # For cloud providers, verify API key is configured
            if not self.provider.api_key:
                print(f"⚠️  No API key configured for {self.provider_name} in llm_config.json")
                return False
            return True

    def _check_local(self) -> bool:
        """Check if local Ollama instance is responding."""
        try:
            health_url = self.provider.endpoint.replace('/api/generate', '/api/tags')
            response = self.session.get(health_url, timeout=10)
            if response.status_code != 200:
                return False

            response = self.session.post(
                self.provider.endpoint,
                json={
                    "model": self.provider.model,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {"num_predict": 3}
                },
                timeout=300
            )
            if response.status_code == 200:
                self._model_warmed = True
                return True
            return False
        except Exception as e:
            print(f"Local LLM availability check failed: {e}")
            return False

    def warm_model(self) -> bool:
        """Pre-warm the model (only applicable for local provider)."""
        if self._model_warmed or self.provider_name != "local":
            return True

        try:
            print("🔥 Warming up local AI model...")
            response = self.session.post(
                self.provider.endpoint,
                json={
                    "model": self.provider.model,
                    "prompt": "Ready",
                    "stream": False,
                    "keep_alive": "20m",
                    "options": {"num_predict": 1}
                },
                timeout=60
            )
            if response.status_code == 200:
                self._model_warmed = True
                print("✅ AI model ready!")
                return True
            else:
                print("⚠️  Model warm-up failed, continuing anyway")
                return False
        except Exception as e:
            print(f"⚠️  Model warm-up failed: {e}, continuing anyway")
            return False

    def enhance_daily_report(self, technical_report: str, day_name: str) -> str:
        """Convert technical daily report to user-friendly format."""
        if not self.is_available():
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
            print(f"  🤖 Enhancing {day_name} report with {self.provider_name}...")
            response = self._call_llm(prompt)
            if response and len(response.strip()) > 100:
                print(f"  ✅ {day_name} enhancement complete")
                return self._format_enhanced_report(response, "DAILY", day_name)
            else:
                print(f"  ⚠️  {day_name} enhancement returned short response, using technical version")
                return technical_report
        except Exception as e:
            print(f"  ❌ LLM enhancement failed for {day_name}: {e}")
            return technical_report

    def enhance_weekly_summary(self, technical_summary: str) -> str:
        """Convert technical weekly summary to user-friendly format."""
        if not self.is_available():
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
                print("  ⚠️  Weekly enhancement returned short response, using technical version")
                return technical_summary
        except Exception as e:
            print(f"  ❌ LLM enhancement failed for weekly summary: {e}")
            return technical_summary

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Route LLM call to the appropriate provider."""
        if self.provider_name == "local":
            return self._call_local(prompt)
        elif self.provider_name == "openai":
            return self._call_openai(prompt)
        elif self.provider_name == "claude":
            return self._call_claude(prompt)
        elif self.provider_name == "gemini":
            return self._call_gemini(prompt)
        else:
            print(f"Unknown provider: {self.provider_name}")
            return None

    def _call_local(self, prompt: str) -> Optional[str]:
        """Call local Ollama LLM."""
        try:
            payload = {
                "model": self.provider.model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "15m",
                "options": {
                    "num_predict": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "stop": ["Technical Report:", "Enhanced Report:", "Technical Summary:", "Enhanced Summary:"]
                }
            }
            extended_timeout = max(self.config.timeout, 600)
            response = self.session.post(
                self.provider.endpoint,
                json=payload,
                timeout=extended_timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"Local LLM error: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"Local LLM request timed out")
            return None
        except Exception as e:
            print(f"Local LLM request failed: {e}")
            return None

    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.provider.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.provider.model,
                "messages": [
                    {"role": "system", "content": "You are a warm, knowledgeable astrologer who writes engaging horoscopes."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            response = self.session.post(
                self.provider.endpoint,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                print(f"OpenAI API error ({response.status_code}): {error_msg}")
                return None
        except requests.exceptions.Timeout:
            print("OpenAI request timed out")
            return None
        except Exception as e:
            print(f"OpenAI request failed: {e}")
            return None

    def _call_claude(self, prompt: str) -> Optional[str]:
        """Call Anthropic Claude API."""
        try:
            headers = {
                "x-api-key": self.provider.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.provider.model,
                "max_tokens": self.config.max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "system": "You are a warm, knowledgeable astrologer who writes engaging horoscopes.",
                "temperature": self.config.temperature
            }
            response = self.session.post(
                self.provider.endpoint,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"].strip()
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                print(f"Claude API error ({response.status_code}): {error_msg}")
                return None
        except requests.exceptions.Timeout:
            print("Claude request timed out")
            return None
        except Exception as e:
            print(f"Claude request failed: {e}")
            return None

    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API."""
        try:
            url = f"{self.provider.endpoint}/{self.provider.model}:generateContent?key={self.provider.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"You are a warm, knowledgeable astrologer who writes engaging horoscopes.\n\n{prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            }
            response = self.session.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                print(f"Gemini API error ({response.status_code}): {error_msg}")
                return None
        except requests.exceptions.Timeout:
            print("Gemini request timed out")
            return None
        except Exception as e:
            print(f"Gemini request failed: {e}")
            return None

    def _format_enhanced_report(self, enhanced_content: str, report_type: str, day_name: str) -> str:
        """Format the enhanced report with proper headers."""
        header_line = "=" * 60
        provider_label = self.provider_name.capitalize()

        if report_type == "DAILY":
            title = f"DAILY ASTROLOGICAL GUIDANCE - {day_name.upper()}"
        else:
            title = "WEEKLY ASTROLOGICAL GUIDANCE"

        formatted = f"""{header_line}
{title}
{header_line}
✨ Enhanced by {provider_label} AI ✨

{enhanced_content}

{header_line}
Generated with {provider_label} AI enhancement
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
            default_config = LLMConfig()
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: LLMConfig) -> None:
        """Save configuration to file."""
        try:
            data = {
                "default_provider": config.default_provider,
                "timeout": config.timeout,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "providers": config.providers
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving LLM config: {e}")

    def get_config(self) -> LLMConfig:
        """Get current configuration."""
        return self.config

    def get_provider_status(self) -> Dict[str, str]:
        """Get status of all configured providers."""
        status = {}
        for name in LLMEnhancer.SUPPORTED_PROVIDERS:
            provider = self.config.get_provider(name)
            if not provider:
                status[name] = "not configured"
            elif name == "local":
                status[name] = "configured (local)"
            elif provider.api_key:
                # Mask the API key for display
                masked = provider.api_key[:8] + "..." + provider.api_key[-4:] if len(provider.api_key) > 12 else "***"
                status[name] = f"configured (key: {masked})"
            else:
                status[name] = "no API key"
        return status


# Keep backward-compatible aliases
LocalLLMEnhancer = LLMEnhancer


if __name__ == "__main__":
    config_manager = LLMConfigManager()

    print("LLM Enhancer Configuration")
    print("=" * 40)
    print(f"Default provider: {config_manager.config.default_provider}")
    print()
    print("Provider Status:")
    for name, status in config_manager.get_provider_status().items():
        print(f"  {name:10s} : {status}")
    print()
    print("To configure a provider, edit llm_config.json and add your API key.")
    print("Set 'default_provider' to one of: local, openai, claude, gemini, none")
