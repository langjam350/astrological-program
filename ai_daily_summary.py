#!/usr/bin/env python3
"""
AI Daily Summary Generator for Astrological Reports
Generates insightful summaries with positives and negatives to anticipate.
Supports both cloud AI (Anthropic Claude) and local AI (Ollama) providers.
"""

import json
import os
import requests
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class AISummaryConfig:
    """Configuration for AI summary generation."""
    provider: str = "local"  # "anthropic" or "local"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    local_endpoint: str = "http://localhost:11434/api/generate"
    local_model: str = "llama3.1:latest"
    timeout: int = 120
    max_tokens: int = 1500
    temperature: float = 0.7

class AIDailySummaryGenerator:
    """Generates AI-powered daily summaries for astrological charts."""

    def __init__(self, config: AISummaryConfig):
        """Initialize with configuration."""
        self.config = config
        self.session = requests.Session()

    def generate_daily_anticipation_summary(
        self,
        technical_report: str,
        date_str: str,
        birth_data: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Generate an AI summary highlighting what to anticipate for the day.

        Args:
            technical_report: The raw astrological analysis
            date_str: Date string for the report
            birth_data: Optional birth information for personalization

        Returns:
            AI-generated summary or None if generation fails
        """
        prompt = self._build_anticipation_prompt(technical_report, date_str, birth_data)

        # Try cloud AI first if configured
        if self.config.provider == "anthropic" and self.config.anthropic_api_key:
            print(f"  [Cloud AI] Generating AI summary for {date_str} (Anthropic Claude)...")
            result = self._call_anthropic(prompt)
            if result:
                print(f"  [OK] Cloud AI summary generated for {date_str}")
                return self._format_summary(result, date_str, "Anthropic Claude")

        # Fall back to local AI
        print(f"  [Local AI] Generating AI summary for {date_str}...")
        result = self._call_local_ai(prompt)
        if result:
            print(f"  [OK] Local AI summary generated for {date_str}")
            return self._format_summary(result, date_str, "Local AI")

        print(f"  [WARNING] AI summary generation failed for {date_str}")
        return None

    def _build_anticipation_prompt(
        self,
        technical_report: str,
        date_str: str,
        birth_data: Optional[Dict[str, str]] = None
    ) -> str:
        """Build the prompt for AI summary generation."""

        context = ""
        if birth_data:
            context = f"\nBirth Information: {birth_data.get('birth_date', 'N/A')} at {birth_data.get('birth_time', 'N/A')}, {birth_data.get('birth_location', 'N/A')}"

        prompt = f"""You are an expert astrologer providing daily guidance. Based on the following astrological analysis for {date_str}, create a thoughtful, insightful summary that helps the person prepare for and navigate their day.{context}

ASTROLOGICAL ANALYSIS:
{technical_report}

Please create a daily anticipation summary that includes:

1. OVERVIEW: A brief overview of the day's overall energy and themes (2-3 sentences)

2. POSITIVES TO EMBRACE: List 3-5 positive opportunities, favorable energies, or beneficial aspects to take advantage of today. Be specific about:
   - What areas of life are supported
   - What activities or interactions are favored
   - What personal strengths are highlighted

3. CHALLENGES TO NAVIGATE: List 3-5 potential difficulties, tensions, or areas requiring caution. Be helpful and constructive by:
   - Identifying specific challenges or sensitive areas
   - Explaining why these tensions exist astrologically
   - Offering practical strategies to navigate them

4. PRACTICAL GUIDANCE: Provide 2-3 actionable suggestions for making the most of the day's energies

5. TIMING NOTES: If relevant, mention any particularly favorable or challenging times of day

Keep the tone professional yet warm, empowering rather than fatalistic, and focused on practical application. Balance realism with optimism. Make the guidance specific enough to be useful but flexible enough to apply to various life situations.

Format your response with clear sections using the headings above."""

        return prompt

    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic Claude API."""
        try:
            headers = {
                "x-api-key": self.config.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            payload = {
                "model": self.config.anthropic_model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = self.session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                print(f"  Anthropic API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"  Anthropic API call failed: {e}")
            return None

    def _call_local_ai(self, prompt: str) -> Optional[str]:
        """Call local AI (Ollama) API."""
        try:
            payload = {
                "model": self.config.local_model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "15m",
                "options": {
                    "num_predict": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            }

            response = self.session.post(
                self.config.local_endpoint,
                json=payload,
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"  Local AI error {response.status_code}")
                return None

        except requests.exceptions.ConnectionError:
            print("  Local AI not available (connection refused)")
            return None
        except requests.exceptions.Timeout:
            print(f"  Local AI timed out after {self.config.timeout} seconds")
            return None
        except Exception as e:
            print(f"  Local AI call failed: {e}")
            return None

    def _format_summary(self, summary_content: str, date_str: str, provider: str) -> str:
        """Format the AI summary with headers."""
        header_line = "=" * 70

        formatted = f"""{header_line}
AI DAILY ANTICIPATION SUMMARY - {date_str}
{header_line}
Generated by {provider}

{summary_content}

{header_line}
This AI summary is intended as guidance and inspiration.
Use your own judgment and intuition in all decisions.
{header_line}"""

        return formatted

class AISummaryConfigManager:
    """Manages AI summary configuration."""

    def __init__(self, config_file: str = "ai_summary_config.json"):
        """Initialize config manager."""
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> AISummaryConfig:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return AISummaryConfig(**data)
            except Exception as e:
                print(f"Error loading AI summary config: {e}")
                return AISummaryConfig()
        else:
            default_config = AISummaryConfig()
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: AISummaryConfig) -> None:
        """Save configuration to file."""
        try:
            config_dict = {
                "provider": config.provider,
                "anthropic_api_key": config.anthropic_api_key,
                "anthropic_model": config.anthropic_model,
                "local_endpoint": config.local_endpoint,
                "local_model": config.local_model,
                "timeout": config.timeout,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving AI summary config: {e}")

    def get_config(self) -> AISummaryConfig:
        """Get current configuration."""
        return self.config

    def set_anthropic_key(self, api_key: str) -> None:
        """Set Anthropic API key and switch to Anthropic provider."""
        self.config.anthropic_api_key = api_key
        self.config.provider = "anthropic"
        self._save_config(self.config)

    def set_local_provider(self) -> None:
        """Switch to local AI provider."""
        self.config.provider = "local"
        self._save_config(self.config)

    def test_provider(self) -> Tuple[bool, str]:
        """Test the configured AI provider."""
        generator = AIDailySummaryGenerator(self.config)

        test_report = """Sun conjunct Mercury in analytical Virgo.
        Moon trine Venus brings emotional harmony.
        Mars square Saturn suggests potential frustration with delays."""

        result = generator.generate_daily_anticipation_summary(
            test_report,
            "2024-01-15"
        )

        if result:
            return True, f"Successfully connected to {self.config.provider} AI"
        else:
            return False, f"Failed to connect to {self.config.provider} AI"

if __name__ == "__main__":
    # Test the AI summary generator
    config_manager = AISummaryConfigManager()

    print("AI Daily Summary Generator Test")
    print("=" * 40)
    print(f"Provider: {config_manager.config.provider}")
    print(f"Anthropic Key Set: {'Yes' if config_manager.config.anthropic_api_key else 'No'}")
    print(f"Local Model: {config_manager.config.local_model}")
    print()

    success, message = config_manager.test_provider()
    print(f"Test Result: {message}")

    if success:
        print("\n[SUCCESS] AI summary generation is working!")
    else:
        print("\n[FAILED] AI summary generation failed")
        print("\nTo enable AI summaries:")
        print("1. For cloud AI: Set your Anthropic API key in ai_summary_config.json")
        print("2. For local AI: Install Ollama and run: ollama pull llama3.1")
