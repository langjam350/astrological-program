# Claude Code Configuration

This file contains Claude Code-specific configuration and information for the Astrological Analysis Program.

## Installation

Install required dependencies:
```bash
pip install -r requirements.txt
```

This will install:
- **skyfield**: Astronomical calculations using JPL ephemeris
- **requests**: HTTP library for LLM enhancement features

## Development Commands

### Testing the Program

Test weekly report generation:
```bash
python astrological-calculations/astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA"
```

Test the .bat file:
```bash
./run-astrological-analysis.bat -BD 1990-05-15 -BT 14:30 -BL "New York;NY" -CL "Los Angeles;CA"
```

### Linting and Code Quality

Basic syntax checking:
```bash
python -m py_compile astrological-calculations/astrological_analyzer.py
```

## Code Structure

### Main Components

- **`run-astrological-analysis.bat`**: Windows batch file for parameter parsing and program execution
- **`astrological-calculations/`**: Directory containing astronomical calculation modules
  - **`astrological_analyzer.py`**: Main Python script with calculation and analysis logic
- **`data/`**: Directory containing astrological reference data
- **`requirements.txt`**: Python package dependencies

### Key Classes

- **`AstrologicalCalculator`**: Core astronomical and astrological position calculations
- **`AstrologicalAnalyzer`**: Interpretation engine for generating readable analysis
- **`WeeklyAnalyzer`**: Generates 7-day forecasts with daily and weekly summaries
- **`Planet`**: Data class for planetary information
- **`Aspect`**: Data class for aspect relationships

### Data Files Format

All data files use the format: `KEY:value1;value2;value3;...`

Examples:
- `SUN:Life force;vitality;ego;self-expression`
- `HOUSE_1:Self;identity;appearance;first impressions`
- `CONJUNCTION:0;8;Union;blending;emphasis`

## Development Notes

### Astronomical Calculations

The program uses **Skyfield** library for accurate astronomical calculations:

- **Ephemeris**: JPL DE421 ephemeris for planetary positions
- **Planetary positions**: Accurate ecliptic longitude calculations using Skyfield
- **Fallback mode**: Simplified mean longitude calculations if Skyfield unavailable
- **House system**: Basic approach to house cusp calculation
- **Coordinate system**: Approximate city coordinates for demonstration

The program automatically downloads ephemeris data on first run (requires internet).

### Privacy Considerations

This program is designed for local, offline operation:

- **No API calls**: All astrological calculations done locally
- **Minimal internet**: Only for initial ephemeris download and optional LLM features
- **No data transmission**: Birth data never leaves the local machine
- **No AI services**: Core interpretation uses local algorithms (LLM enhancement is optional)

### Extensibility

The program is designed for easy customization:

1. **Interpretation Data**: Modify `.txt` files in `data/` directory
2. **Calculation Methods**: Extend `AstrologicalCalculator` class
3. **Analysis Styles**: Modify `AstrologicalAnalyzer` methods
4. **Output Formats**: Customize the report generation methods

### Testing Strategy

Test cases should cover:

1. **Parameter parsing**: Valid and invalid parameter combinations
2. **Date/time handling**: Various date formats and edge cases
3. **Location parsing**: Different city/state combinations
4. **Calculation accuracy**: Basic astronomical calculation verification
5. **File I/O**: Data file loading and output file creation

### Code Maintenance

- **Documentation**: All classes and methods include docstrings
- **Error handling**: Comprehensive try/catch blocks for file operations
- **Type hints**: Used throughout for better code clarity
- **Modular design**: Separated calculation, analysis, and I/O concerns

## Deployment Notes

For distribution:

1. Ensure all data files are included in `data/` directory
2. Test on clean Windows environment
3. Verify Python requirements are documented
4. Include example command usage in documentation

## Future Enhancements

Potential improvements that maintain the local/offline nature:

- ✅ **Enhanced astronomical accuracy**: Now using Skyfield with JPL ephemeris
- **City coordinate database**: Local database of city coordinates
- **Additional house systems**: Placidus, Koch, Equal House options
- **More aspects**: Minor aspects, midpoints, Arabic parts
- **Graphical output**: SVG charts (partially implemented)
- **Report customization**: User-selectable analysis sections

## Security Considerations

- **Input validation**: All user inputs are validated and sanitized
- **File paths**: Only writes to local directory, no arbitrary file access
- **No external execution**: No system calls or external process spawning
- **Error disclosure**: Error messages don't reveal system information

## Performance Notes

- **Memory usage**: All data loaded into memory for fast access
- **Calculation speed**: Simplified algorithms prioritize speed over precision
- **File I/O**: Minimal disk operations, cached data structures
- **Scalability**: Designed for single-user, single-calculation use