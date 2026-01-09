# Astrological Analysis Program

A local, offline astrological chart calculator and interpreter with no external AI dependencies. This program provides comprehensive birth chart analysis and transit calculations using traditional astrological principles.

## Features

- **Weekly Astrological Reports**: Generate 7-day forecasts with daily analysis files
- **Birth Chart Integration**: Compares current planetary transits to your natal chart
- **LLM Enhancement**: Optional user-friendly report translations via local AI (Ollama, LM Studio)
- **Dual Report Formats**: Technical analysis + AI-enhanced conversational versions
- **Automatic Date/Time**: Uses current system date and time for analysis
- **Individual Daily Files**: Each day saved as separate text file in unique folder
- **Local Processing**: All calculations and interpretations done locally without external API calls
- **Complete Privacy**: All processing local - no external services, no stored credentials
- **Local Delivery**: Windows notifications, desktop shortcuts, optional cloud sync
- **Comprehensive Data**: Includes planetary keywords, house meanings, sign characteristics, and aspect interpretations

## Requirements

- Python 3.6 or higher
- Windows environment (for .bat file execution)
- **Optional**: Local LLM for enhanced reports
  - [Ollama](https://ollama.ai) (recommended)
  - [LM Studio](https://lmstudio.ai)
  - Any OpenAI-compatible local endpoint

## Installation

1. Clone or download this repository
2. Ensure Python is installed and accessible from command line
3. Navigate to the program directory

### Complete Privacy-Focused Setup

```bash
# Complete automated setup (recommended)
python setup_private_automation.py
```

This sets up:
- ✅ Local delivery with Windows notifications
- ✅ Automated Saturday midnight generation
- ✅ No external services or credentials
- ✅ Complete privacy protection

### Optional: Setup Local LLM for Enhanced Reports

**Option 1: Ollama (Recommended)**
```bash
# Install Ollama from https://ollama.ai
# Download a model
ollama pull llama2
# or for better results:
ollama pull mistral

# Run LLM setup
python setup_llm.py
```

**Option 2: LM Studio**
1. Install LM Studio from https://lmstudio.ai
2. Download and load a model
3. Start local server on port 1234
4. Run: `python setup_llm.py`

## Usage

### Generate Weekly Astrological Reports

```bash
run-astrological-analysis.bat -BD 1990-05-15 -BT 14:30 -BL "New York;NY" -CL "Los Angeles;CA"
```

### Parameters

**All Parameters Required:**
- `-BD` - Birth Date (YYYY-MM-DD format)
- `-BT` - Birth Time (HH:MM format, 24-hour)
- `-BL` - Birth Location ("City;State" format)
- `-CL` - Current Location ("City;State" format)

**Note:** Current date and time are automatically detected from your system.

## Output

The program generates a unique folder containing:

1. **Standard Reports**: Technical astrological analysis
2. **Enhanced Reports**: User-friendly AI translations (if LLM enabled)
3. **Unique Folder Name**: Format: `weekly_report_YYYYMMDD_[unique_id]`

### File Structure

**Without LLM (Standard):**
- `monday_20231201.txt` - Technical daily analysis
- `weekly_summary.txt` - Technical weekly overview

**With LLM (Enhanced):**
- `monday_20231201.txt` - Technical daily analysis
- `monday_20231201_enhanced.txt` - User-friendly version
- `weekly_summary.txt` - Technical weekly overview
- `weekly_summary_enhanced.txt` - Conversational weekly guidance

### Report Content

**Technical Reports Include:**
- Planetary positions and aspects
- Astrological interpretations
- Transit analysis
- House and sign meanings

**Enhanced Reports Include:**
- Conversational, encouraging tone
- Practical daily guidance
- Accessible language
- Personal, supportive advice

## Data Files

The program uses local data files in the `data/` directory:

- `planets.txt` - Planetary keywords and meanings
- `houses.txt` - House meanings and life areas
- `signs.txt` - Sign characteristics and elements
- `aspects.txt` - Aspect meanings and orbs

## Examples

### Basic Weekly Report
```bash
run-astrological-analysis.bat -BD 1985-03-22 -BT 09:15 -BL "Chicago;IL" -CL "Chicago;IL"
```

### Different Current Location
```bash
run-astrological-analysis.bat -BD 1985-03-22 -BT 09:15 -BL "Chicago;IL" -CL "Miami;FL"
```

### Sample Output Folder

**Without LLM Enhancement:**
```
weekly_report_20231201_a3b7c9f2/
├── 20231201.txt
├── 20231201_transits_chart.svg
├── 20231202.txt
├── 20231202_transits_chart.svg
├── 20231203.txt
├── 20231203_transits_chart.svg
├── 20231204.txt
├── 20231204_transits_chart.svg
├── 20231205.txt
├── 20231205_transits_chart.svg
├── 20231206.txt
├── 20231206_transits_chart.svg
├── 20231207.txt
├── 20231207_transits_chart.svg
├── birth_chart.svg
└── weekly_summary.txt
```

**With LLM Enhancement:**
```
weekly_report_20231201_a3b7c9f2/
├── 20231201.txt
├── 20231201_enhanced.txt
├── 20231201_transits_chart.svg
├── 20231202.txt
├── 20231202_enhanced.txt
├── 20231202_transits_chart.svg
├── [... continues for each day]
├── birth_chart.svg
├── weekly_summary.txt
└── weekly_summary_enhanced.txt
```

## Technical Notes

- Uses simplified astronomical calculations suitable for astrological purposes
- House system: Simplified Placidus approach
- Aspect orbs: Standard traditional orbs (8° for major aspects, 6° for sextiles)
- Coordinates: Approximate city coordinates (for demonstration purposes)

## Limitations

- Simplified astronomical calculations (not ephemeris-quality)
- Limited city coordinate database
- Basic house calculation system
- No advanced techniques (Arabic parts, fixed stars, etc.)

## Privacy & Security

- **Complete Local Processing**: All calculations done on your computer
- **No External Services**: No email providers, cloud AI, or third-party dependencies
- **No Stored Credentials**: No passwords or API keys saved anywhere
- **Local Delivery Only**: Windows notifications, desktop shortcuts, folder access
- **Your Data Stays Private**: Nothing ever leaves your computer unless you choose
- **Optional Cloud Sync**: You can optionally sync to your own cloud folders

## Customization

You can modify the interpretation data by editing files in the `data/` directory:

- Add your own planetary keywords to `planets.txt`
- Customize house meanings in `houses.txt`
- Modify sign descriptions in `signs.txt`
- Adjust aspect interpretations in `aspects.txt`

## Troubleshooting

**Python not found error:**
- Ensure Python is installed and in your system PATH
- Try using `python3` instead of `python` in the .bat file

**Invalid date/time format:**
- Use YYYY-MM-DD for dates (e.g., 2023-01-15)
- Use HH:MM for times in 24-hour format (e.g., 14:30)

**Location format:**
- Use "City;State" format with semicolon separator
- Enclose in quotes if city name contains spaces

**LLM Enhancement Issues:**
- Run `python setup_llm.py test` to check connection
- Ensure your local LLM server is running
- For Ollama: `ollama list` to see available models
- Check `llm_config.json` for correct endpoint and model settings
- Enhanced reports will automatically fallback to standard if LLM unavailable

**Local Delivery Issues:**
- Run `python local_delivery.py` to test delivery system
- Check Windows notification settings if notifications not appearing
- Ensure delivery folders exist and are accessible
- Check `delivery_config.json` for delivery settings
- Reports always saved to `tosend/` folder as backup

## Contributing

This is a standalone local program designed for privacy and independence. Feel free to modify the interpretation algorithms or add features for your personal use.

## License

Free for personal use. Modify as needed for your astrological analysis requirements.