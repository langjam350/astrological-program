AI DAILY ANTICIPATION SUMMARIES
================================

The program now generates AI-powered daily summaries with positives and negatives to anticipate.

QUICK START:
-----------
1. Edit ai_summary_config.json
2. Choose provider: "anthropic" (cloud, better quality) or "local" (free, private)
3. For Anthropic: Add your API key
4. For Local: Install Ollama and run: ollama pull llama3.1

OUTPUT:
------
Each day gets a new file: YYYYMMDD_ai_summary.txt
Contains: Overview, Positives to Embrace, Challenges to Navigate, Practical Guidance

TESTING:
-------
python ai_daily_summary.py

The summaries are automatically generated with your daily reports.
