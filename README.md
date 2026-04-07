# Astrological Analysis Program

A local astrological chart calculator and interpreter that generates weekly transit reports based on your birth chart. Uses JPL ephemeris data (via Skyfield) for accurate planetary positions and optionally enhances reports with AI (Claude, OpenAI, Gemini, or local LLMs).

## Features

- **Weekly Astrological Reports**: 7-day forecasts with individual daily analysis files
- **Accurate Planetary Positions**: Uses NASA JPL DE421 ephemeris via Skyfield library
- **Birth Chart Integration**: Compares current planetary transits to your natal chart
- **AI-Enhanced Reports** (optional): Converts technical analysis into conversational, friendly horoscopes using Claude, OpenAI, Gemini, or a local LLM
- **SVG Charts**: Visual transit and birth chart diagrams
- **Automatic Date/Time**: Uses your system clock for current transit calculations
- **Local Delivery**: Windows notifications, desktop shortcuts, ZIP packaging

## Prerequisites

Before you begin, make sure you have the following installed:

### 1. Python 3.6+

Download and install Python from [python.org](https://www.python.org/downloads/).

During installation on Windows, **check the box that says "Add Python to PATH"** — this is critical.

To verify Python is installed correctly, open a terminal and run:
```bash
python --version
```
You should see something like `Python 3.12.x` (or higher).

### 2. Git (optional, for cloning)

If you want to clone the repository instead of downloading a ZIP, install Git from [git-scm.com](https://git-scm.com/downloads).

### 3. A Terminal / Command Prompt

- **Windows**: Use Command Prompt, PowerShell, or Windows Terminal
- **WSL**: Works under WSL but the `.bat` launcher is Windows-only; call the Python script directly instead

## Installation

### Step 1: Get the Code

**Option A — Clone with Git:**
```bash
git clone <repository-url>
cd astrological-program
```

**Option B — Download ZIP:**
Download and extract the repository, then open a terminal in the extracted folder.

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **skyfield** — Astronomical calculations using JPL ephemeris (downloads ~17MB ephemeris file on first run)
- **requests** — HTTP library for optional AI enhancement features

### Step 3: Verify Installation

Run a quick test to confirm everything works:
```bash
python astrological-calculations/astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA" none
```

You should see output like:
```
Using Skyfield for accurate astronomical calculations
Generated: 20260317.txt & 20260317_transits_chart.svg
Generated: 20260318.txt & ...
...
Weekly astrological reports generated in folder: weekly_report_YYYYMMDD_XXXXXXXX
```

A folder named `weekly_report_YYYYMMDD_XXXXXXXX` will appear containing your reports.

## Setting Up AI-Enhanced Reports (Optional)

The program can use an AI provider to rewrite the technical astrological analysis into warm, conversational horoscopes. This is completely optional — the program generates full reports without it.

### Option 1: Claude (Anthropic) — Recommended

Claude produces high-quality, nuanced horoscope writing.

#### Getting a Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/) and create an account (or sign in)
2. Navigate to **Settings** > **API Keys** (or go directly to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys))
3. Click **Create Key**
4. Give it a name (e.g., "astrology-program") and click **Create**
5. **Copy the key immediately** — it starts with `sk-ant-` and won't be shown again

#### Adding Your Key to the Config

Open `llm_config.json` in a text editor and:

1. Set `"default_provider"` to `"claude"`
2. Paste your API key into the `claude` provider's `"api_key"` field

```json
{
  "default_provider": "claude",
  "timeout": 120,
  "max_tokens": 1000,
  "temperature": 0.7,
  "providers": {
    "claude": {
      "endpoint": "https://api.anthropic.com/v1/messages",
      "model": "claude-sonnet-4-20250514",
      "api_key": "sk-ant-your-key-here"
    }
  }
}
```

> **Important:** Keep your API key private. Do not commit `llm_config.json` with a real key to a public repository. The Claude API has usage-based pricing — check [anthropic.com/pricing](https://www.anthropic.com/pricing) for current rates. Each weekly report uses roughly 8 API calls (7 daily + 1 summary).

### Option 2: OpenAI

1. Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. In `llm_config.json`, set `"default_provider": "openai"` and paste your key in the `openai` section

### Option 3: Google Gemini

1. Get an API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. In `llm_config.json`, set `"default_provider": "gemini"` and paste your key in the `gemini` section

### Option 4: Local LLM (Ollama) — Free & Private

For fully offline operation with no API costs:

1. Install Ollama from [ollama.com](https://ollama.com/)
2. Download a model:
   ```bash
   ollama pull llama3.1
   ```
3. In `llm_config.json`, set `"default_provider": "local"`

The local provider connects to Ollama's default endpoint at `http://localhost:11434`.

## Usage

### Using the Batch File (Windows)

```bash
run-astrological-analysis.bat -BD 1990-05-15 -BT 14:30 -BL "New York;NY" -CL "Los Angeles;CA"
```

If you omit any parameters, the program will prompt you interactively — including letting you choose an AI provider.

### Using Python Directly (All Platforms)

```bash
python astrological-calculations/astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA"
```

To specify an AI provider:
```bash
python astrological-calculations/astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA" claude
```

### Parameters

| Parameter | Format | Example | Description |
|-----------|--------|---------|-------------|
| Birth Date | `YYYY-MM-DD` | `1990-05-15` | Your date of birth |
| Birth Time | `HH:MM` | `14:30` | Your time of birth (24-hour) |
| Birth Location | `"City;State"` | `"New York;NY"` | Where you were born |
| Current Location | `"City;State"` | `"Los Angeles;CA"` | Where you are now |
| AI Provider | `none`/`claude`/`openai`/`gemini`/`local` | `claude` | Optional, defaults to `none` |

## Output

The program creates a uniquely-named folder with your weekly report:

```
weekly_report_20260317_87f8fa4f/
├── 20260317.txt                    # Daily analysis (one per day)
├── 20260317_transits_chart.svg     # Visual transit chart (one per day)
├── 20260318.txt
├── 20260318_transits_chart.svg
├── ... (7 days total)
├── birth_chart.svg                 # Your natal chart diagram
├── weekly_summary.txt              # Weekly overview
├── 20260317_enhanced.txt           # AI-enhanced version (if AI enabled)
└── weekly_summary_enhanced.txt     # AI-enhanced weekly summary (if AI enabled)
```

Reports are also packaged as a ZIP in the `tosend/` folder and copied to `C:\MyReports\astrology-reports\`.

### What's in a Daily Report

- Planetary positions with sign and house placements
- Astrological themes for the day
- Transit highlights (aspects between transiting and natal planets)
- Historical context for outer planet positions
- Ideal activity breakdown by time of day

### What AI Enhancement Adds

When an AI provider is configured, each report gets a companion `_enhanced.txt` file that rewrites the technical analysis into:
- Warm, conversational language
- Practical daily guidance
- Accessible explanations of astrological concepts
- Personal, supportive tone

## Data Files

The `data/` directory contains the interpretation reference data:

| File | Contents |
|------|----------|
| `planets.txt` | Planetary keywords and meanings |
| `houses.txt` | House meanings and life areas |
| `signs.txt` | Zodiac sign characteristics and elements |
| `aspects.txt` | Aspect types, orbs, and interpretations |
| `historical_patterns.txt` | Historical context for planetary positions |
| `ideal_activities.txt` | Activity suggestions by planetary energy |

You can edit these files to customize the interpretations.

## Technical Notes

- **Ephemeris**: Uses JPL DE421 via Skyfield for accurate planetary longitude calculations
- **Fallback**: If Skyfield is unavailable, uses simplified mean longitude formulas
- **House system**: Simplified Placidus approach
- **Aspect orbs**: 8 degrees for major aspects (conjunction, opposition, square, trine), 6 degrees for sextiles
- **Coordinates**: Approximate city coordinates from a built-in lookup table

## Troubleshooting

**"Python not found" error:**
- Make sure Python is in your system PATH. Re-run the installer and check "Add Python to PATH".
- On some systems, use `python3` instead of `python`.

**"Skyfield not available" warning:**
- Run `pip install skyfield` — the program will still work without it, but positions will be less accurate.

**Ephemeris download fails:**
- Skyfield downloads `de421.bsp` (~17MB) on first run. Make sure you have internet access.
- After the first download, the file is cached locally and no internet is needed.

**AI enhancement not working:**
- Verify your API key is correct in `llm_config.json`
- For Claude: key should start with `sk-ant-`
- For local/Ollama: make sure Ollama is running (`ollama serve`)
- The program always falls back to standard reports if AI is unavailable

**Location format errors:**
- Use `"City;State"` with a semicolon separator (not a comma)
- Enclose in quotes if the city name has spaces: `"New York;NY"`

## License

Free for personal use. Modify as needed for your astrological analysis requirements.
