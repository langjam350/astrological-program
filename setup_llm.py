#!/usr/bin/env python3
"""
LLM Setup Utility for Astrological Program
Helps configure and test local LLM integration.
"""

import json
import sys
from llm_enhancer import LLMConfigManager, LocalLLMEnhancer, LLMConfig

def main():
    """Main setup interface."""
    print("🔮 Astrological Program - LLM Setup")
    print("=" * 50)

    config_manager = LLMConfigManager()
    current_config = config_manager.get_config()

    print(f"Current Configuration:")
    print(f"  Enabled: {current_config.enabled}")
    print(f"  Endpoint: {current_config.endpoint}")
    print(f"  Model: {current_config.model}")
    print()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "enable":
            enable_llm(config_manager)
        elif command == "disable":
            disable_llm(config_manager)
        elif command == "test":
            test_llm(config_manager)
        elif command == "config":
            configure_llm(config_manager)
        else:
            show_help()
    else:
        interactive_setup(config_manager)

def interactive_setup(config_manager: LLMConfigManager):
    """Interactive setup process."""
    print("Would you like to enable LLM enhancement? (y/n): ", end="")
    response = input().lower().strip()

    if response in ['y', 'yes']:
        print("\nSelect your local LLM setup:")
        print("1. Ollama (recommended)")
        print("2. LM Studio")
        print("3. Custom endpoint")
        print("Choice (1-3): ", end="")

        choice = input().strip()

        if choice == "1":
            setup_ollama(config_manager)
        elif choice == "2":
            setup_lm_studio(config_manager)
        elif choice == "3":
            setup_custom(config_manager)
        else:
            print("Invalid choice")
            return

        # Test the configuration
        if test_llm(config_manager):
            print("\n✅ LLM setup complete! Your reports will now be enhanced.")
        else:
            print("\n❌ Setup failed. Check your LLM server and try again.")
    else:
        print("LLM enhancement disabled. You'll receive standard technical reports.")
        config_manager.disable_llm()

def setup_ollama(config_manager: LLMConfigManager):
    """Setup for Ollama."""
    print("\nSetting up Ollama integration...")
    print("Make sure you have:")
    print("1. Installed Ollama: https://ollama.ai")
    print("2. Downloaded a model: ollama pull llama2")
    print("3. Ollama is running")

    print("\nAvailable models (enter model name or press Enter for llama2): ", end="")
    model = input().strip() or "llama2"

    config_manager.update_config(
        enabled=True,
        endpoint="http://localhost:11434/api/generate",
        model=model
    )
    print(f"Configured for Ollama with {model} model")

def setup_lm_studio(config_manager: LLMConfigManager):
    """Setup for LM Studio."""
    print("\nSetting up LM Studio integration...")
    print("Make sure you have:")
    print("1. LM Studio installed and running")
    print("2. A model loaded")
    print("3. Local server started on port 1234")

    print("\nModel name (or press Enter for default): ", end="")
    model = input().strip() or "local-model"

    config_manager.update_config(
        enabled=True,
        endpoint="http://localhost:1234/v1/chat/completions",
        model=model
    )
    print(f"Configured for LM Studio with {model}")

def setup_custom(config_manager: LLMConfigManager):
    """Setup for custom endpoint."""
    print("\nCustom LLM endpoint setup...")

    print("Endpoint URL: ", end="")
    endpoint = input().strip()

    print("Model name: ", end="")
    model = input().strip()

    if endpoint and model:
        config_manager.update_config(
            enabled=True,
            endpoint=endpoint,
            model=model
        )
        print(f"Configured custom endpoint: {endpoint}")
    else:
        print("Invalid configuration")

def enable_llm(config_manager: LLMConfigManager):
    """Enable LLM with current settings."""
    config_manager.update_config(enabled=True)
    print("✅ LLM enhancement enabled")

def disable_llm(config_manager: LLMConfigManager):
    """Disable LLM enhancement."""
    config_manager.disable_llm()
    print("❌ LLM enhancement disabled")

def test_llm(config_manager: LLMConfigManager) -> bool:
    """Test LLM connection."""
    print("Testing LLM connection...")

    config = config_manager.get_config()
    if not config.enabled:
        print("❌ LLM is disabled in configuration")
        return False

    enhancer = LocalLLMEnhancer(config)

    if enhancer.is_available():
        print("✅ LLM connection successful!")
        print(f"Endpoint: {config.endpoint}")
        print(f"Model: {config.model}")

        # Test enhancement
        print("\nTesting report enhancement...")
        test_report = "Sun in Aries brings dynamic energy today. Moon square Mars creates some tension."

        try:
            enhanced = enhancer.enhance_daily_report(test_report, "Monday")
            if "enhanced" in enhanced.lower() or len(enhanced) > len(test_report) * 1.5:
                print("✅ Report enhancement working!")
                return True
            else:
                print("⚠️  Enhancement may not be working properly")
                return False
        except Exception as e:
            print(f"❌ Enhancement test failed: {e}")
            return False
    else:
        print("❌ Cannot connect to LLM")
        print(f"Endpoint: {config.endpoint}")
        print(f"Model: {config.model}")
        print("\nTroubleshooting:")
        print("1. Make sure your LLM server is running")
        print("2. Check the endpoint URL")
        print("3. Verify the model name")
        return False

def configure_llm(config_manager: LLMConfigManager):
    """Advanced configuration options."""
    config = config_manager.get_config()

    print("Current configuration:")
    for key, value in config.__dict__.items():
        print(f"  {key}: {value}")

    print("\nEnter new values (press Enter to keep current):")

    new_endpoint = input(f"Endpoint [{config.endpoint}]: ").strip()
    new_model = input(f"Model [{config.model}]: ").strip()
    new_timeout = input(f"Timeout [{config.timeout}]: ").strip()
    new_max_tokens = input(f"Max tokens [{config.max_tokens}]: ").strip()
    new_temperature = input(f"Temperature [{config.temperature}]: ").strip()

    updates = {}
    if new_endpoint:
        updates["endpoint"] = new_endpoint
    if new_model:
        updates["model"] = new_model
    if new_timeout:
        try:
            updates["timeout"] = int(new_timeout)
        except ValueError:
            print("Invalid timeout value")
    if new_max_tokens:
        try:
            updates["max_tokens"] = int(new_max_tokens)
        except ValueError:
            print("Invalid max_tokens value")
    if new_temperature:
        try:
            updates["temperature"] = float(new_temperature)
        except ValueError:
            print("Invalid temperature value")

    if updates:
        config_manager.update_config(**updates)
        print("✅ Configuration updated")
    else:
        print("No changes made")

def show_help():
    """Show help information."""
    print("Usage: python setup_llm.py [command]")
    print()
    print("Commands:")
    print("  enable    - Enable LLM enhancement")
    print("  disable   - Disable LLM enhancement")
    print("  test      - Test LLM connection")
    print("  config    - Advanced configuration")
    print()
    print("Without a command, runs interactive setup")

if __name__ == "__main__":
    main()