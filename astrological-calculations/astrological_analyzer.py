#!/usr/bin/env python3
"""
Astrological Analysis Program
A local, offline astrological chart calculator and interpreter.
No external AI dependencies - all analysis done with local algorithms.
"""

import sys
import os
import math
import datetime
import uuid
import zipfile
import shutil
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import skyfield for astronomical calculations
try:
    from skyfield.api import load, wgs84
    from skyfield import almanac
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False
    print("Warning: Skyfield not available - falling back to simplified calculations")

try:
    from llm_enhancer import LocalLLMEnhancer, LLMConfigManager
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LLM enhancement not available - continuing with standard reports")

try:
    from chart_generator import create_chart_for_planets
    CHART_GENERATION_AVAILABLE = True
except ImportError:
    CHART_GENERATION_AVAILABLE = False
    print("Chart generation not available")

try:
    from local_delivery import LocalDeliveryManager
    LOCAL_DELIVERY_AVAILABLE = True
except ImportError:
    LOCAL_DELIVERY_AVAILABLE = False
    print("Local delivery not available")

@dataclass
class Planet:
    """Represents a planet with its position and characteristics."""
    name: str
    longitude: float  # Degrees from 0 Aries
    sign: str
    house: int
    keywords: List[str]

@dataclass
class Aspect:
    """Represents an aspect between two planets."""
    planet1: str
    planet2: str
    angle: float
    aspect_type: str
    orb: float
    keywords: List[str]

class AstrologicalCalculator:
    """Core calculation engine for astrological positions."""

    def __init__(self):
        """Initialize the calculator with data files."""
        self.data_dir = "data"
        self.planets_data = self._load_data_file("planets.txt")
        self.houses_data = self._load_data_file("houses.txt")
        self.signs_data = self._load_data_file("signs.txt")
        self.aspects_data = self._load_data_file("aspects.txt")
        self.historical_data = self._load_data_file("historical_patterns.txt")
        self.activities_data = self._load_data_file("ideal_activities.txt")

        # Sign boundaries (simplified - 30 degrees each)
        self.sign_names = [
            "ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO",
            "LIBRA", "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES"
        ]

        # Initialize skyfield ephemeris if available
        if SKYFIELD_AVAILABLE:
            try:
                self.ephemeris = load('de421.bsp')  # JPL ephemeris
                self.timescale = load.timescale()
                print("✨ Using Skyfield for accurate astronomical calculations")
            except Exception as e:
                print(f"Warning: Could not load Skyfield ephemeris: {e}")
                print("Falling back to simplified calculations")
                self.ephemeris = None
                self.timescale = None
        else:
            self.ephemeris = None
            self.timescale = None

    def _load_data_file(self, filename: str) -> Dict[str, List[str]]:
        """Load and parse a data file into a dictionary."""
        data = {}
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            print(f"Warning: Data file {filepath} not found")
            return data

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        data[key] = value.split(';')
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

        return data

    def _calculate_julian_day(self, date_str: str, time_str: str) -> float:
        """Calculate Julian Day Number for given date and time."""
        try:
            # Parse date (expecting YYYY-MM-DD format)
            year, month, day = map(int, date_str.split('-'))
            # Parse time (expecting HH:MM format)
            hour, minute = map(int, time_str.split(':'))

            # Basic Julian Day calculation (simplified)
            if month <= 2:
                year -= 1
                month += 12

            a = year // 100
            b = 2 - a + (a // 4)

            jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
            jd += (hour + minute / 60.0) / 24.0  # Add time portion

            return jd
        except Exception as e:
            print(f"Error calculating Julian Day: {e}")
            return 2451545.0  # Default to J2000.0

    def _get_sign_from_longitude(self, longitude: float) -> str:
        """Convert longitude to zodiac sign."""
        # Normalize longitude to 0-360 range
        longitude = longitude % 360
        sign_index = int(longitude // 30)
        return self.sign_names[sign_index]

    def _calculate_planetary_positions(self, jd: float) -> Dict[str, float]:
        """Calculate planetary positions for given Julian Day using Skyfield."""
        positions = {}

        # Use Skyfield if available for accurate calculations
        if self.ephemeris and self.timescale:
            try:
                # Convert JD to Skyfield time
                t = self.timescale.tt_jd(jd)

                # Get Earth for observer position
                earth = self.ephemeris['earth']

                # Calculate positions for each planet
                planet_map = {
                    'SUN': 'sun',
                    'MOON': 'moon',
                    'MERCURY': 'mercury',
                    'VENUS': 'venus',
                    'MARS': 'mars',
                    'JUPITER': 'jupiter barycenter',
                    'SATURN': 'saturn barycenter',
                    'URANUS': 'uranus barycenter',
                    'NEPTUNE': 'neptune barycenter',
                    'PLUTO': 'pluto barycenter'
                }

                for planet_name, ephemeris_name in planet_map.items():
                    try:
                        planet = self.ephemeris[ephemeris_name]
                        # Calculate apparent position from Earth
                        astrometric = earth.at(t).observe(planet).apparent()

                        # Get ecliptic coordinates (proper conversion)
                        lat, lon, distance = astrometric.ecliptic_latlon()

                        # Convert to degrees (lon is in degrees already from skyfield)
                        longitude = lon.degrees % 360.0
                        positions[planet_name] = longitude

                    except Exception as e:
                        print(f"Warning: Could not calculate {planet_name}: {e}")
                        # Fall back to simplified calculation for this planet
                        positions[planet_name] = self._simplified_planet_position(jd, planet_name)

            except Exception as e:
                print(f"Warning: Skyfield calculation failed: {e}")
                # Fall back to simplified calculations
                return self._simplified_planetary_positions(jd)
        else:
            # Fall back to simplified calculations
            return self._simplified_planetary_positions(jd)

        return positions

    def _simplified_planetary_positions(self, jd: float) -> Dict[str, float]:
        """Simplified planetary position calculations (fallback)."""
        # Days since J2000.0
        d = jd - 2451545.0

        positions = {}

        # Simplified mean longitudes (basic approximation)
        positions['SUN'] = (280.461 + 0.9856474 * d) % 360
        positions['MOON'] = (218.316 + 13.176396 * d) % 360
        positions['MERCURY'] = (252.251 + 4.092317 * d) % 360
        positions['VENUS'] = (181.980 + 1.602130 * d) % 360
        positions['MARS'] = (355.433 + 0.524032 * d) % 360
        positions['JUPITER'] = (34.352 + 0.083056 * d) % 360
        positions['SATURN'] = (50.078 + 0.033459 * d) % 360
        positions['URANUS'] = (314.055 + 0.011731 * d) % 360
        positions['NEPTUNE'] = (304.349 + 0.006027 * d) % 360
        positions['PLUTO'] = (238.958 + 0.003968 * d) % 360

        return positions

    def _simplified_planet_position(self, jd: float, planet_name: str) -> float:
        """Calculate single planet position with simplified formula."""
        d = jd - 2451545.0

        simple_formulas = {
            'SUN': (280.461, 0.9856474),
            'MOON': (218.316, 13.176396),
            'MERCURY': (252.251, 4.092317),
            'VENUS': (181.980, 1.602130),
            'MARS': (355.433, 0.524032),
            'JUPITER': (34.352, 0.083056),
            'SATURN': (50.078, 0.033459),
            'URANUS': (314.055, 0.011731),
            'NEPTUNE': (304.349, 0.006027),
            'PLUTO': (238.958, 0.003968)
        }

        if planet_name in simple_formulas:
            base, rate = simple_formulas[planet_name]
            return (base + rate * d) % 360

        return 0.0

    def _calculate_houses(self, latitude: float, longitude: float, jd: float) -> List[float]:
        """Calculate house cusps using simplified Placidus system."""
        # This is a very simplified house calculation
        # Real implementation would use proper Placidus or other house system

        houses = []
        ascendant = 0  # Simplified - would calculate based on time and location

        for i in range(12):
            house_cusp = (ascendant + i * 30) % 360
            houses.append(house_cusp)

        return houses

    def _get_house_for_planet(self, planet_longitude: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in."""
        # Simplified house assignment
        for i in range(12):
            next_house = (i + 1) % 12
            if house_cusps[i] <= planet_longitude < house_cusps[next_house]:
                return i + 1
        return 1  # Default to first house

    def _calculate_aspects(self, planets: Dict[str, Planet]) -> List[Aspect]:
        """Calculate aspects between planets."""
        aspects = []
        planet_names = list(planets.keys())

        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                planet1 = planets[planet_names[i]]
                planet2 = planets[planet_names[j]]

                # Calculate angular separation
                angle = abs(planet1.longitude - planet2.longitude)
                if angle > 180:
                    angle = 360 - angle

                # Check for major aspects
                for aspect_name, aspect_info in self.aspects_data.items():
                    parts = aspect_info[0].split(';')
                    if len(parts) >= 2:
                        target_angle = float(parts[0])
                        orb = float(parts[1])

                        if abs(angle - target_angle) <= orb:
                            aspect = Aspect(
                                planet1=planet1.name,
                                planet2=planet2.name,
                                angle=angle,
                                aspect_type=aspect_name,
                                orb=abs(angle - target_angle),
                                keywords=aspect_info[2:] if len(aspect_info) > 2 else []
                            )
                            aspects.append(aspect)

        return aspects

    def calculate_chart(self, date_str: str, time_str: str, location: str) -> Tuple[Dict[str, Planet], List[Aspect]]:
        """Calculate complete astrological chart."""
        # Parse location (simplified - just for display)
        city, state = location.split(';') if ';' in location else (location, "")

        # For simplicity, use approximate coordinates
        # Real implementation would have a city database
        latitude = 40.0  # Approximate latitude
        longitude_geo = -74.0  # Approximate longitude

        # Calculate Julian Day
        jd = self._calculate_julian_day(date_str, time_str)

        # Calculate planetary positions
        planet_positions = self._calculate_planetary_positions(jd)

        # Calculate house cusps
        house_cusps = self._calculate_houses(latitude, longitude_geo, jd)

        # Create Planet objects
        planets = {}
        for planet_name, longitude in planet_positions.items():
            sign = self._get_sign_from_longitude(longitude)
            house = self._get_house_for_planet(longitude, house_cusps)
            keywords = self.planets_data.get(planet_name, [])

            planets[planet_name] = Planet(
                name=planet_name,
                longitude=longitude,
                sign=sign,
                house=house,
                keywords=keywords
            )

        # Calculate aspects
        aspects = self._calculate_aspects(planets)

        return planets, aspects

class AstrologicalAnalyzer:
    """Generates interpretations based on astrological data."""

    def __init__(self, calculator: AstrologicalCalculator):
        """Initialize analyzer with calculator instance."""
        self.calculator = calculator

    def _interpret_planet_in_sign(self, planet: Planet) -> str:
        """Generate interpretation for planet in sign."""
        planet_keywords = self.calculator.planets_data.get(planet.name, [])
        sign_info = self.calculator.signs_data.get(planet.sign, [])

        if not planet_keywords or not sign_info:
            return f"{planet.name} in {planet.sign}: Basic influence"

        # Combine planet and sign characteristics
        element = sign_info[0] if len(sign_info) > 0 else "Unknown"
        modality = sign_info[1] if len(sign_info) > 1 else "Unknown"

        interpretation = f"{planet.name} in {planet.sign} ({element} {modality}): "
        interpretation += f"The {planet_keywords[0]} energy expresses through "
        interpretation += f"{sign_info[3] if len(sign_info) > 3 else 'this sign'} characteristics."

        return interpretation

    def _interpret_planet_in_house(self, planet: Planet) -> str:
        """Generate interpretation for planet in house."""
        house_key = f"HOUSE_{planet.house}"
        house_keywords = self.calculator.houses_data.get(house_key, [])

        if not house_keywords:
            return f"{planet.name} in House {planet.house}: Influences this life area"

        interpretation = f"{planet.name} in House {planet.house}: "
        interpretation += f"Focuses {planet.name.lower()} energy on {house_keywords[0]} "
        interpretation += f"and {house_keywords[1] if len(house_keywords) > 1 else 'related themes'}."

        return interpretation

    def _interpret_aspect(self, aspect: Aspect) -> str:
        """Generate interpretation for an aspect."""
        interpretation = f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2}: "

        if aspect.keywords:
            interpretation += f"This {aspect.keywords[0]} aspect brings "
            interpretation += f"{'; '.join(aspect.keywords[1:3])} " if len(aspect.keywords) > 2 else ""
            interpretation += f"between these planetary energies."
        else:
            interpretation += f"A {aspect.aspect_type.lower()} relationship between these planets."

        return interpretation

    def generate_birth_chart_analysis(self, planets: Dict[str, Planet], aspects: List[Aspect],
                                     date_str: str, time_str: str, location: str) -> str:
        """Generate complete birth chart analysis."""
        analysis = []

        # Header
        analysis.append("=" * 60)
        analysis.append("BIRTH CHART ANALYSIS")
        analysis.append("=" * 60)
        analysis.append(f"Birth Date: {date_str}")
        analysis.append(f"Birth Time: {time_str}")
        analysis.append(f"Birth Location: {location}")
        analysis.append("")

        # Planetary positions
        analysis.append("PLANETARY POSITIONS")
        analysis.append("-" * 30)
        for planet in planets.values():
            degrees = int(planet.longitude % 30)
            minutes = int((planet.longitude % 30 - degrees) * 60)
            analysis.append(f"{planet.name:10} {degrees:2d}°{minutes:02d}' {planet.sign:12} House {planet.house}")
        analysis.append("")

        # Planet in sign interpretations
        analysis.append("PLANETARY SIGN INTERPRETATIONS")
        analysis.append("-" * 40)
        for planet in planets.values():
            analysis.append(self._interpret_planet_in_sign(planet))
            analysis.append("")

        # Planet in house interpretations
        analysis.append("PLANETARY HOUSE INTERPRETATIONS")
        analysis.append("-" * 41)
        for planet in planets.values():
            analysis.append(self._interpret_planet_in_house(planet))
            analysis.append("")

        # Aspects
        if aspects:
            analysis.append("MAJOR ASPECTS")
            analysis.append("-" * 20)
            for aspect in aspects:
                analysis.append(self._interpret_aspect(aspect))
                analysis.append("")

        # Summary themes
        analysis.append("KEY THEMES")
        analysis.append("-" * 15)
        analysis.append(self._generate_summary_themes(planets, aspects))

        return "\n".join(analysis)

    def generate_transit_analysis(self, birth_planets: Dict[str, Planet],
                                current_planets: Dict[str, Planet],
                                current_date: str, current_time: str, current_location: str) -> str:
        """Generate transit analysis comparing current planetary positions to birth chart."""
        analysis = []

        # Header
        analysis.append("TRANSIT ANALYSIS")
        analysis.append("=" * 60)
        analysis.append(f"Current Date: {current_date}")
        analysis.append(f"Current Time: {current_time}")
        analysis.append(f"Current Location: {current_location}")
        analysis.append("")

        # Current planetary positions
        analysis.append("CURRENT PLANETARY POSITIONS")
        analysis.append("-" * 35)
        for planet in current_planets.values():
            degrees = int(planet.longitude % 30)
            minutes = int((planet.longitude % 30 - degrees) * 60)
            analysis.append(f"{planet.name:10} {degrees:2d}°{minutes:02d}' {planet.sign:12} House {planet.house}")
        analysis.append("")

        # Transit aspects to natal planets
        analysis.append("MAJOR TRANSITS")
        analysis.append("-" * 20)
        transit_aspects = self._calculate_transit_aspects(birth_planets, current_planets)

        if transit_aspects:
            for aspect in transit_aspects:
                analysis.append(self._interpret_transit_aspect(aspect))
                analysis.append("")
        else:
            analysis.append("No major transit aspects within orb at this time.")
            analysis.append("")

        # Transit interpretations by planet
        analysis.append("TRANSIT INTERPRETATIONS")
        analysis.append("-" * 30)
        for transit_planet_name, transit_planet in current_planets.items():
            if transit_planet_name in birth_planets:
                birth_planet = birth_planets[transit_planet_name]
                analysis.append(self._interpret_planet_transit(transit_planet, birth_planet))
                analysis.append("")

        return "\n".join(analysis)

    def _calculate_transit_aspects(self, birth_planets: Dict[str, Planet],
                                 current_planets: Dict[str, Planet]) -> List[Aspect]:
        """Calculate aspects between current transiting planets and birth planets."""
        aspects = []

        for transit_name, transit_planet in current_planets.items():
            for birth_name, birth_planet in birth_planets.items():
                # Skip same planet to same planet
                if transit_name == birth_name:
                    continue

                # Calculate angular separation
                angle = abs(transit_planet.longitude - birth_planet.longitude)
                if angle > 180:
                    angle = 360 - angle

                # Check for major aspects
                for aspect_name, aspect_info in self.calculator.aspects_data.items():
                    parts = aspect_info[0].split(';')
                    if len(parts) >= 2:
                        target_angle = float(parts[0])
                        orb = float(parts[1])

                        if abs(angle - target_angle) <= orb:
                            aspect = Aspect(
                                planet1=f"Transit {transit_name}",
                                planet2=f"Natal {birth_name}",
                                angle=angle,
                                aspect_type=aspect_name,
                                orb=abs(angle - target_angle),
                                keywords=aspect_info[2:] if len(aspect_info) > 2 else []
                            )
                            aspects.append(aspect)

        return aspects

    def _interpret_transit_aspect(self, aspect: Aspect) -> str:
        """Generate interpretation for a transit aspect."""
        interpretation = f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2}: "

        if aspect.keywords:
            interpretation += f"This transit brings {aspect.keywords[0]} energy, emphasizing "
            interpretation += f"{'; '.join(aspect.keywords[1:3])} " if len(aspect.keywords) > 2 else ""
            interpretation += f"in the relationship between these planetary energies."
        else:
            interpretation += f"A {aspect.aspect_type.lower()} transit affecting natal planet energies."

        return interpretation

    def _interpret_planet_transit(self, transit_planet: Planet, birth_planet: Planet) -> str:
        """Generate interpretation for a planet's current position relative to its birth position."""
        interpretation = f"Transit {transit_planet.name} in {transit_planet.sign}: "

        if transit_planet.sign == birth_planet.sign:
            interpretation += f"Currently returning to natal sign, reinforcing core {transit_planet.name.lower()} themes."
        elif transit_planet.house == birth_planet.house:
            interpretation += f"Transiting natal {birth_planet.house} house, activating birth themes in this life area."
        else:
            house_key = f"HOUSE_{transit_planet.house}"
            house_keywords = self.calculator.houses_data.get(house_key, [])
            interpretation += f"Currently influencing {house_keywords[0] if house_keywords else 'life areas'} "
            interpretation += f"through {transit_planet.sign} energy."

        return interpretation

    def _generate_summary_themes(self, planets: Dict[str, Planet], aspects: List[Aspect]) -> str:
        """Generate summary of key astrological themes."""
        themes = []

        # Analyze element distribution
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        for planet in planets.values():
            sign_info = self.calculator.signs_data.get(planet.sign, [])
            if sign_info:
                element = sign_info[0]
                if element in elements:
                    elements[element] += 1

        dominant_element = max(elements, key=elements.get)
        themes.append(f"Dominant Element: {dominant_element} - emphasizes {dominant_element.lower()} qualities")

        # Analyze house emphasis
        house_counts = {}
        for planet in planets.values():
            house_counts[planet.house] = house_counts.get(planet.house, 0) + 1

        if house_counts:
            emphasized_house = max(house_counts, key=house_counts.get)
            house_key = f"HOUSE_{emphasized_house}"
            house_keywords = self.calculator.houses_data.get(house_key, [])
            if house_keywords:
                themes.append(f"House {emphasized_house} emphasis - focus on {house_keywords[0]} themes")

        # Note challenging aspects
        challenging_aspects = [a for a in aspects if a.aspect_type in ["SQUARE", "OPPOSITION"]]
        if challenging_aspects:
            themes.append(f"Growth opportunities through {len(challenging_aspects)} challenging aspects")

        # Note harmonious aspects
        harmonious_aspects = [a for a in aspects if a.aspect_type in ["TRINE", "SEXTILE"]]
        if harmonious_aspects:
            themes.append(f"Natural talents indicated by {len(harmonious_aspects)} harmonious aspects")

        return "\n".join(f"• {theme}" for theme in themes)

class WeeklyAnalyzer:
    """Generates weekly astrological reports."""

    def __init__(self, calculator: AstrologicalCalculator, analyzer: AstrologicalAnalyzer):
        """Initialize weekly analyzer with calculator and analyzer instances."""
        self.calculator = calculator
        self.analyzer = analyzer

        # Initialize LLM enhancer if available
        self.llm_enhancer = None
        if LLM_AVAILABLE:
            try:
                config_manager = LLMConfigManager()
                self.llm_enhancer = LocalLLMEnhancer(config_manager.get_config())
                if self.llm_enhancer.is_available():
                    print("✨ LLM enhancement enabled - reports will be user-friendly!")
                    # Pre-warm the model for better performance
                    self.llm_enhancer.warm_model()
                else:
                    print("📝 LLM configured but not available - using standard reports")
                    self.llm_enhancer = None
            except Exception as e:
                print(f"LLM initialization failed: {e}")
                self.llm_enhancer = None

    def generate_weekly_reports(self, birth_date: str, birth_time: str,
                               birth_location: str, current_location: str) -> str:
        """Generate weekly astrological reports starting from today."""
        # Generate unique folder ID
        folder_id = str(uuid.uuid4())[:8]
        now = datetime.datetime.now()
        folder_name = f"weekly_report_{now.strftime('%Y%m%d')}_{folder_id}"

        # Create folder
        os.makedirs(folder_name, exist_ok=True)

        # Calculate birth chart once
        birth_planets, birth_aspects = self.calculator.calculate_chart(
            birth_date, birth_time, birth_location
        )

        # Generate reports for 7 days starting today
        for day_offset in range(7):
            report_date = now + datetime.timedelta(days=day_offset)
            report_date_str = report_date.strftime("%Y-%m-%d")
            report_time_str = "12:00"  # Use noon for daily analysis

            # Calculate daily chart
            daily_planets, _ = self.calculator.calculate_chart(
                report_date_str, report_time_str, current_location
            )

            # Generate daily analysis
            daily_analysis = self._generate_daily_analysis(
                birth_planets, daily_planets, report_date, current_location
            )

            # Save technical version with YYYYMMDD format
            date_str = report_date.strftime('%Y%m%d')
            filename = f"{date_str}.txt"
            filepath = os.path.join(folder_name, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(daily_analysis)

            # Generate daily transit chart
            if CHART_GENERATION_AVAILABLE:
                try:
                    daily_chart_file = create_chart_for_planets(
                        daily_planets,
                        f"Transit Chart - {report_date.strftime('%A, %B %d, %Y')}",
                        folder_name
                    )
                    # Rename chart file to match date format
                    old_chart_name = os.path.basename(daily_chart_file)
                    new_chart_name = f"{date_str}_transits_chart.svg"
                    new_chart_path = os.path.join(folder_name, new_chart_name)

                    if os.path.exists(daily_chart_file):
                        os.rename(daily_chart_file, new_chart_path)

                except Exception as e:
                    print(f"Daily chart generation failed for {date_str}: {e}")

            # Generate and save LLM-enhanced version if available
            if self.llm_enhancer:
                enhanced_analysis = self.llm_enhancer.enhance_daily_report(
                    daily_analysis, report_date.strftime("%A")
                )
                enhanced_filename = f"{date_str}_enhanced.txt"
                enhanced_filepath = os.path.join(folder_name, enhanced_filename)

                with open(enhanced_filepath, 'w', encoding='utf-8') as f:
                    f.write(enhanced_analysis)

                print(f"Generated: {filename}, {date_str}_transits_chart.svg & {enhanced_filename}")
            else:
                print(f"Generated: {filename} & {date_str}_transits_chart.svg")

        # Generate weekly summary
        weekly_summary = self._generate_weekly_summary(
            birth_planets, birth_location, current_location, now
        )

        # Save technical weekly summary
        summary_filepath = os.path.join(folder_name, "weekly_summary.txt")
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(weekly_summary)

        # Generate and save LLM-enhanced weekly summary if available
        if self.llm_enhancer:
            enhanced_summary = self.llm_enhancer.enhance_weekly_summary(weekly_summary)
            enhanced_summary_filepath = os.path.join(folder_name, "weekly_summary_enhanced.txt")

            with open(enhanced_summary_filepath, 'w', encoding='utf-8') as f:
                f.write(enhanced_summary)

            print(f"Generated: weekly_summary.txt & weekly_summary_enhanced.txt")
        else:
            print(f"Generated: weekly_summary.txt")

        # Generate birth chart if available
        if CHART_GENERATION_AVAILABLE:
            try:
                # Create birth chart with consistent naming
                birth_chart_file = create_chart_for_planets(
                    birth_planets,
                    f"Birth Chart - {birth_date}",
                    folder_name
                )

                # Rename to consistent format
                if os.path.exists(birth_chart_file):
                    birth_chart_new = os.path.join(folder_name, "birth_chart.svg")
                    os.rename(birth_chart_file, birth_chart_new)
                    print(f"Generated: birth_chart.svg")

            except Exception as e:
                print(f"Birth chart generation failed: {e}")

        # Create ZIP package
        zip_path = self._create_zip_package(folder_name)
        if zip_path:
            print(f"📦 Report package created: {os.path.basename(zip_path)}")

            # Deliver report using local delivery system
            if LOCAL_DELIVERY_AVAILABLE:
                try:
                    delivery_manager = LocalDeliveryManager()
                    week_info = f"Week of {now.strftime('%B %d, %Y')}"
                    delivery_manager.deliver_report(zip_path, week_info)
                except Exception as e:
                    print(f"Local delivery failed: {e}")

        return folder_name

    def _create_zip_package(self, folder_name: str) -> Optional[str]:
        """Create ZIP package of the report folder."""
        try:
            # Create tosend folder if it doesn't exist
            tosend_folder = "tosend"
            os.makedirs(tosend_folder, exist_ok=True)

            # Create ZIP file name
            zip_filename = f"{folder_name}.zip"
            zip_path = os.path.join(tosend_folder, zip_filename)

            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from the report folder
                for root, dirs, files in os.walk(folder_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add file to ZIP with relative path
                        arcname = os.path.relpath(file_path, os.path.dirname(folder_name))
                        zipf.write(file_path, arcname)

            # Move ZIP file to destination folder
            self._move_zip_to_destination(zip_path, zip_filename)

            # Optionally remove the original folder to save space
            # shutil.rmtree(folder_name)  # Uncomment if you want to cleanup

            return zip_path

        except Exception as e:
            print(f"Failed to create ZIP package: {e}")
            return None

    def _move_zip_to_destination(self, zip_path: str, zip_filename: str) -> None:
        """Move the ZIP file to C:\MyReports\astrology-reports\ folder."""
        try:
            # Define destination folder path
            if os.name == 'nt':  # Windows
                destination_folder = r"C:\MyReports\astrology-reports"
            else:  # Linux/Mac (for WSL compatibility)
                destination_folder = "/mnt/c/MyReports/astrology-reports"

            # Create destination directory if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)

            # Define destination path
            destination_path = os.path.join(destination_folder, zip_filename)

            # Copy the file to destination
            shutil.copy2(zip_path, destination_path)

            print(f"📁 ZIP file copied to: {destination_path}")

        except Exception as e:
            print(f"Warning: Failed to move ZIP to destination folder: {e}")
            print(f"ZIP file remains in: {zip_path}")

    def _generate_daily_analysis(self, birth_planets: Dict[str, Planet],
                                daily_planets: Dict[str, Planet],
                                report_date: datetime.datetime,
                                current_location: str) -> str:
        """Generate analysis for a specific day."""
        analysis = []

        # Header
        analysis.append("=" * 60)
        analysis.append(f"DAILY ASTROLOGICAL FORECAST")
        analysis.append("=" * 60)
        analysis.append(f"Date: {report_date.strftime('%A, %B %d, %Y')}")
        analysis.append(f"Location: {current_location}")
        analysis.append("")

        # Daily planetary positions
        analysis.append("PLANETARY POSITIONS FOR TODAY")
        analysis.append("-" * 35)
        for planet in daily_planets.values():
            degrees = int(planet.longitude % 30)
            minutes = int((planet.longitude % 30 - degrees) * 60)
            analysis.append(f"{planet.name:10} {degrees:2d}°{minutes:02d}' {planet.sign:12} House {planet.house}")
        analysis.append("")

        # Daily themes
        analysis.append("TODAY'S ASTROLOGICAL THEMES")
        analysis.append("-" * 35)
        daily_themes = self._get_daily_themes(daily_planets)
        for theme in daily_themes:
            analysis.append(f"• {theme}")
        analysis.append("")

        # Transit highlights
        analysis.append("TRANSIT HIGHLIGHTS")
        analysis.append("-" * 25)
        transit_aspects = self.analyzer._calculate_transit_aspects(birth_planets, daily_planets)

        if transit_aspects:
            # Show only the most significant transits (up to 3)
            significant_transits = sorted(transit_aspects, key=lambda x: x.orb)[:3]
            for aspect in significant_transits:
                analysis.append(self.analyzer._interpret_transit_aspect(aspect))
                analysis.append("")
        else:
            analysis.append("No major transit aspects active today.")
            analysis.append("")

        # Daily guidance
        analysis.append("DAILY GUIDANCE")
        analysis.append("-" * 20)
        guidance = self._generate_daily_guidance(daily_planets, transit_aspects)
        analysis.append(guidance)
        analysis.append("")

        # Historical/World Events Context
        analysis.append("HISTORICAL & WORLD EVENTS CONTEXT")
        analysis.append("-" * 40)
        historical_context = self._generate_historical_context(daily_planets, transit_aspects)
        for context in historical_context:
            analysis.append(f"• {context}")
        analysis.append("")

        # Ideal Day Breakdown
        analysis.append("IDEAL DAY BREAKDOWN")
        analysis.append("-" * 25)
        day_breakdown = self._generate_ideal_day_breakdown(daily_planets, report_date)
        for time_block in day_breakdown:
            analysis.append(time_block)

        return "\n".join(analysis)

    def _generate_weekly_summary(self, birth_planets: Dict[str, Planet],
                                birth_location: str, current_location: str,
                                start_date: datetime.datetime) -> str:
        """Generate weekly summary report."""
        analysis = []

        # Header
        analysis.append("=" * 60)
        analysis.append("WEEKLY ASTROLOGICAL SUMMARY")
        analysis.append("=" * 60)
        end_date = start_date + datetime.timedelta(days=6)
        analysis.append(f"Week of: {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}")
        analysis.append(f"Birth Location: {birth_location}")
        analysis.append(f"Current Location: {current_location}")
        analysis.append("")

        # Weekly overview
        analysis.append("WEEKLY OVERVIEW")
        analysis.append("-" * 20)

        # Analyze major transits for the week
        weekly_transits = []
        for day_offset in range(7):
            check_date = start_date + datetime.timedelta(days=day_offset)
            date_str = check_date.strftime("%Y-%m-%d")
            daily_planets, _ = self.calculator.calculate_chart(date_str, "12:00", current_location)

            day_transits = self.analyzer._calculate_transit_aspects(birth_planets, daily_planets)
            for transit in day_transits:
                transit.day = check_date.strftime("%A")
                weekly_transits.append(transit)

        # Group and summarize significant transits
        if weekly_transits:
            analysis.append("Major transit themes this week:")
            unique_transits = self._get_unique_weekly_transits(weekly_transits)
            for transit_desc in unique_transits[:5]:  # Top 5 themes
                analysis.append(f"• {transit_desc}")
        else:
            analysis.append("A generally stable week with no major transit aspects.")

        analysis.append("")

        # Key dates
        analysis.append("KEY DATES THIS WEEK")
        analysis.append("-" * 25)
        key_dates = self._identify_key_dates(weekly_transits, start_date)
        for date_info in key_dates:
            analysis.append(f"• {date_info}")

        analysis.append("")

        # Weekly advice
        analysis.append("WEEKLY ADVICE")
        analysis.append("-" * 20)
        weekly_advice = self._generate_weekly_advice(weekly_transits)
        analysis.append(weekly_advice)

        return "\n".join(analysis)

    def _get_daily_themes(self, daily_planets: Dict[str, Planet]) -> List[str]:
        """Extract key themes for the day based on planetary positions."""
        themes = []

        # Check for planets in prominent signs or houses
        for planet in daily_planets.values():
            if planet.name in ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]:
                sign_info = self.calculator.signs_data.get(planet.sign, [])
                if sign_info and len(sign_info) > 3:
                    themes.append(f"{planet.name} in {planet.sign}: Focus on {sign_info[3]} energy")

        # Limit to top 3 themes
        return themes[:3]

    def _generate_daily_guidance(self, daily_planets: Dict[str, Planet],
                                transit_aspects: List[Aspect]) -> str:
        """Generate practical guidance for the day."""
        guidance_parts = []

        # Check Moon sign for emotional guidance
        moon = daily_planets.get("MOON")
        if moon:
            sign_info = self.calculator.signs_data.get(moon.sign, [])
            if sign_info and len(sign_info) > 4:
                guidance_parts.append(f"Emotional focus: {sign_info[4]} approach today")

        # Check for challenging vs harmonious aspects
        challenging = [a for a in transit_aspects if a.aspect_type in ["SQUARE", "OPPOSITION"]]
        harmonious = [a for a in transit_aspects if a.aspect_type in ["TRINE", "SEXTILE"]]

        if challenging:
            guidance_parts.append("Navigate challenges with patience and flexibility")
        if harmonious:
            guidance_parts.append("Take advantage of favorable energy for important activities")

        if not guidance_parts:
            guidance_parts.append("A stable day for routine activities and steady progress")

        return ". ".join(guidance_parts) + "."

    def _get_unique_weekly_transits(self, weekly_transits: List[Aspect]) -> List[str]:
        """Extract unique transit themes for the week."""
        themes = set()
        for transit in weekly_transits:
            if transit.keywords:
                theme = f"{transit.aspect_type} energy bringing {transit.keywords[0]}"
                themes.add(theme)
        return list(themes)

    def _identify_key_dates(self, weekly_transits: List[Aspect],
                           start_date: datetime.datetime) -> List[str]:
        """Identify the most significant dates of the week."""
        key_dates = []

        # Group transits by day
        daily_transit_counts = {}
        for transit in weekly_transits:
            day = getattr(transit, 'day', 'Unknown')
            daily_transit_counts[day] = daily_transit_counts.get(day, 0) + 1

        # Find days with most activity
        if daily_transit_counts:
            max_activity = max(daily_transit_counts.values())
            busy_days = [day for day, count in daily_transit_counts.items() if count >= max_activity - 1]

            for day in busy_days[:3]:  # Top 3 active days
                key_dates.append(f"{day}: High astrological activity")

        if not key_dates:
            key_dates.append("Tuesday: Mid-week energy peak")
            key_dates.append("Friday: Prepare for weekend themes")

        return key_dates

    def _generate_weekly_advice(self, weekly_transits: List[Aspect]) -> str:
        """Generate overall advice for the week."""
        advice_parts = []

        if weekly_transits:
            challenging_count = len([t for t in weekly_transits if t.aspect_type in ["SQUARE", "OPPOSITION"]])
            harmonious_count = len([t for t in weekly_transits if t.aspect_type in ["TRINE", "SEXTILE"]])

            if challenging_count > harmonious_count:
                advice_parts.append("This week emphasizes growth through challenges")
                advice_parts.append("Stay flexible and patient with unexpected developments")
            elif harmonious_count > challenging_count:
                advice_parts.append("Favorable week for pursuing goals and new opportunities")
                advice_parts.append("Trust your instincts and take positive action")
            else:
                advice_parts.append("Balanced week with both opportunities and lessons")
                advice_parts.append("Focus on steady progress and mindful decisions")
        else:
            advice_parts.append("Quiet week perfect for reflection and planning")
            advice_parts.append("Use this stable energy to organize and prepare for future goals")

        return ". ".join(advice_parts) + "."

    def _generate_historical_context(self, daily_planets: Dict[str, Planet],
                                   transit_aspects: List[Aspect]) -> List[str]:
        """Generate historical and world events context."""
        contexts = []

        # Check for major planetary patterns
        for aspect in transit_aspects:
            if aspect.aspect_type in ["CONJUNCTION", "OPPOSITION", "SQUARE"]:
                # Look for historical patterns in our data
                for pattern_key, pattern_info in self.calculator.historical_data.items():
                    if any(planet in aspect.planet1 or planet in aspect.planet2
                          for planet in ["JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"]):
                        if "CONJUNCTION" in pattern_key and aspect.aspect_type == "CONJUNCTION":
                            contexts.append(f"Major {pattern_info[0]}: {pattern_info[1]}")
                        elif "TRANSIT" in pattern_key and aspect.aspect_type in ["SQUARE", "OPPOSITION"]:
                            contexts.append(f"Transformational period: {pattern_info[1]}")

        # Check for specific planetary signatures
        outer_planets = ["JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"]
        for planet_name, planet in daily_planets.items():
            if planet_name in outer_planets:
                # Look for patterns related to this planet's position
                if planet.sign in ["ARIES", "LIBRA", "CANCER", "CAPRICORN"]:  # Cardinal signs
                    contexts.append(f"{planet_name} in {planet.sign}: Period of structural change and leadership shifts")

        # Add general historical context
        if len(transit_aspects) > 3:
            contexts.append("High astrological activity: Similar to periods of major historical transitions")
        elif len(transit_aspects) == 0:
            contexts.append("Quiet astrological period: Time for integration and steady progress")

        # Limit to top 3 most relevant contexts
        return contexts[:3] if contexts else ["Stable astrological period with normal historical patterns"]

    def _generate_ideal_day_breakdown(self, daily_planets: Dict[str, Planet],
                                    report_date: datetime.datetime) -> List[str]:
        """Generate specific ideal day timing breakdown."""
        breakdown = []

        # Get sun and moon signs for the day
        sun = daily_planets.get("SUN")
        moon = daily_planets.get("MOON")
        mercury = daily_planets.get("MERCURY")
        venus = daily_planets.get("VENUS")
        mars = daily_planets.get("MARS")

        # Morning (6 AM - 12 PM) - Sun influence
        morning_activities = []
        if sun:
            sun_key = f"SUN_{sun.sign}"
            sun_activities = self.calculator.activities_data.get(sun_key, [])
            if sun_activities:
                morning_activities.extend(sun_activities[1:3])  # First 2 activities

        breakdown.append("🌅 MORNING (6 AM - 12 PM): Solar Energy Peak")
        if morning_activities:
            breakdown.append(f"   Ideal for: {', '.join(morning_activities)}")
        else:
            breakdown.append("   Ideal for: New beginnings, leadership activities, creative work")
        breakdown.append("")

        # Afternoon (12 PM - 6 PM) - Mercury/Mars influence
        afternoon_activities = []
        if mercury:
            merc_activities = self.calculator.activities_data.get("MERCURY_ACTIVITIES", [])
            if merc_activities:
                afternoon_activities.extend(merc_activities[1:3])

        breakdown.append("☀️ AFTERNOON (12 PM - 6 PM): Mental Energy & Action")
        if afternoon_activities:
            breakdown.append(f"   Ideal for: {', '.join(afternoon_activities)}")
        else:
            breakdown.append("   Ideal for: Communication, planning, focused work, problem solving")
        breakdown.append("")

        # Evening (6 PM - 10 PM) - Venus influence
        evening_activities = []
        if venus:
            venus_activities = self.calculator.activities_data.get("VENUS_ACTIVITIES", [])
            if venus_activities:
                evening_activities.extend(venus_activities[1:3])

        breakdown.append("🌆 EVENING (6 PM - 10 PM): Social & Creative Energy")
        if evening_activities:
            breakdown.append(f"   Ideal for: {', '.join(evening_activities)}")
        else:
            breakdown.append("   Ideal for: Relationships, artistic pursuits, social gatherings")
        breakdown.append("")

        # Night (10 PM - 6 AM) - Moon influence
        night_guidance = []
        if moon:
            moon_phase = self._get_moon_phase_guidance(report_date)
            night_guidance.append(moon_phase)

        breakdown.append("🌙 NIGHT (10 PM - 6 AM): Lunar & Intuitive Energy")
        if night_guidance:
            breakdown.append(f"   Ideal for: {night_guidance[0]}")
        else:
            breakdown.append("   Ideal for: Rest, reflection, emotional processing, dreams")

        # Add activities to avoid based on planetary positions
        avoid_activities = self._get_activities_to_avoid(daily_planets)
        if avoid_activities:
            breakdown.append("")
            breakdown.append("⚠️  ACTIVITIES TO APPROACH WITH CAUTION:")
            for activity in avoid_activities:
                breakdown.append(f"   • {activity}")

        return breakdown

    def _get_moon_phase_guidance(self, date: datetime.datetime) -> str:
        """Get moon phase guidance for the night."""
        # Simplified moon phase calculation (rough approximation)
        days_since_new = (date.day - 1) % 29.5

        if days_since_new < 7:
            return "New Moon energy: Setting intentions, meditation, new beginnings"
        elif days_since_new < 14:
            return "Waxing Moon energy: Building momentum, taking action, manifestation work"
        elif days_since_new < 22:
            return "Full Moon energy: Completion, celebration, emotional release, gratitude"
        else:
            return "Waning Moon energy: Letting go, forgiveness, cleansing, reflection"

    def _get_activities_to_avoid(self, daily_planets: Dict[str, Planet]) -> List[str]:
        """Identify activities to avoid based on planetary positions."""
        avoid_list = []

        # Check for challenging aspects or retrograde patterns
        mercury = daily_planets.get("MERCURY")
        mars = daily_planets.get("MARS")
        venus = daily_planets.get("VENUS")

        # Simplified retrograde check (would need ephemeris for accuracy)
        # For now, we'll use house positions as proxy for challenging periods
        if mercury and mercury.house in [6, 8, 12]:  # Challenging houses
            avoid_list.append("Important contracts or technology purchases")

        if mars and mars.house in [6, 8, 12]:
            avoid_list.append("Confrontational situations or aggressive actions")

        if venus and venus.house in [6, 8, 12]:
            avoid_list.append("Major relationship decisions or financial investments")

        return avoid_list[:2]  # Limit to top 2 cautions

def main():
    """Main program entry point."""
    if len(sys.argv) != 5:
        print("Usage: python astrological_analyzer.py BIRTH_DATE BIRTH_TIME BIRTH_LOCATION CURRENT_LOCATION")
        print("Example: python astrological_analyzer.py 1990-05-15 14:30 'New York;NY' 'Los Angeles;CA'")
        sys.exit(1)

    birth_date = sys.argv[1]
    birth_time = sys.argv[2]
    birth_location = sys.argv[3]
    current_location = sys.argv[4]

    try:
        # Get current date and time
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        # Initialize calculator and analyzer
        calculator = AstrologicalCalculator()
        analyzer = AstrologicalAnalyzer(calculator)

        # Generate weekly reports
        weekly_analyzer = WeeklyAnalyzer(calculator, analyzer)
        report_folder = weekly_analyzer.generate_weekly_reports(
            birth_date, birth_time, birth_location, current_location
        )

        print(f"Weekly astrological reports generated in folder: {report_folder}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()