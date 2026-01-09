#!/usr/bin/env python3
"""
Astrological Chart Generator
Creates circular astrological charts in SVG format.
Compatible with all browsers and can be converted to other formats.
"""

import math
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ChartPlanet:
    """Planet data for chart generation."""
    name: str
    longitude: float
    symbol: str
    color: str

class AstrologicalChartGenerator:
    """Generates circular astrological charts in SVG format."""

    def __init__(self):
        """Initialize chart generator with styling and symbols."""
        self.chart_size = 800
        self.center = self.chart_size // 2
        self.outer_radius = 350
        self.inner_radius = 280
        self.planet_radius = 250
        self.house_radius = 200

        # Planet symbols and colors
        self.planet_symbols = {
            'SUN': '☉',
            'MOON': '☽',
            'MERCURY': '☿',
            'VENUS': '♀',
            'MARS': '♂',
            'JUPITER': '♃',
            'SATURN': '♄',
            'URANUS': '♅',
            'NEPTUNE': '♆',
            'PLUTO': '♇'
        }

        self.planet_colors = {
            'SUN': '#FFD700',
            'MOON': '#C0C0C0',
            'MERCURY': '#FFA500',
            'VENUS': '#90EE90',
            'MARS': '#FF6347',
            'JUPITER': '#4169E1',
            'SATURN': '#8B4513',
            'URANUS': '#40E0D0',
            'NEPTUNE': '#4682B4',
            'PLUTO': '#800080'
        }

        # Zodiac signs
        self.zodiac_signs = [
            '♈', '♉', '♊', '♋', '♌', '♍',
            '♎', '♏', '♐', '♑', '♒', '♓'
        ]

        self.sign_names = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]

    def generate_chart(self, planets: Dict[str, any], chart_title: str = "Astrological Chart") -> str:
        """Generate SVG chart from planetary data."""
        svg_content = self._create_svg_header()

        # Add title
        svg_content += self._add_title(chart_title)

        # Draw zodiac wheel
        svg_content += self._draw_zodiac_wheel()

        # Draw house lines (simplified equal house system)
        svg_content += self._draw_house_lines()

        # Add planets
        svg_content += self._add_planets(planets)

        # Add aspects (simplified)
        svg_content += self._draw_major_aspects(planets)

        # Add legend
        svg_content += self._add_legend()

        svg_content += "</svg>"

        return svg_content

    def _create_svg_header(self) -> str:
        """Create SVG header with styling."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.chart_size}" height="{self.chart_size + 180}" xmlns="http://www.w3.org/2000/svg">
<style>
    .chart-bg {{ fill: #1a1a2e; }}
    .zodiac-line {{ stroke: #16213e; stroke-width: 2; fill: none; }}
    .house-line {{ stroke: #4a4a6a; stroke-width: 1; fill: none; }}
    .sign-text {{ fill: #ffffff; font-family: Arial, sans-serif; font-size: 20px; text-anchor: middle; dominant-baseline: central; }}
    .planet-text {{ font-family: Arial, sans-serif; font-size: 18px; text-anchor: middle; dominant-baseline: central; }}
    .title {{ fill: #ffffff; font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; text-anchor: middle; }}
    .legend {{ fill: #ffffff; font-family: Arial, sans-serif; font-size: 12px; }}
    .aspect-line {{ stroke: #888888; stroke-width: 1; opacity: 0.6; }}
</style>

<!-- Background -->
<rect class="chart-bg" width="{self.chart_size}" height="{self.chart_size + 180}"/>

<!-- Outer circle -->
<circle cx="{self.center}" cy="{self.center}" r="{self.outer_radius}"
        fill="none" stroke="#16213e" stroke-width="3"/>

<!-- Inner circle -->
<circle cx="{self.center}" cy="{self.center}" r="{self.inner_radius}"
        fill="none" stroke="#16213e" stroke-width="2"/>

'''

    def _add_title(self, title: str) -> str:
        """Add chart title."""
        return f'<text x="{self.center}" y="30" class="title">{title}</text>\n'

    def _draw_zodiac_wheel(self) -> str:
        """Draw the zodiac wheel with signs."""
        svg = ""

        for i in range(12):
            # Calculate angle for this sign (starting from Aries at 0°)
            angle_deg = i * 30
            angle_rad = math.radians(angle_deg - 90)  # -90 to start at top

            # Draw sign division line
            x1 = self.center + self.inner_radius * math.cos(angle_rad)
            y1 = self.center + self.inner_radius * math.sin(angle_rad)
            x2 = self.center + self.outer_radius * math.cos(angle_rad)
            y2 = self.center + self.outer_radius * math.sin(angle_rad)

            svg += f'<line class="zodiac-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'

            # Add sign symbol
            mid_angle_rad = math.radians((angle_deg + 15) - 90)  # Middle of sign
            text_radius = (self.outer_radius + self.inner_radius) / 2
            text_x = self.center + text_radius * math.cos(mid_angle_rad)
            text_y = self.center + text_radius * math.sin(mid_angle_rad)

            svg += f'<text class="sign-text" x="{text_x}" y="{text_y}">{self.zodiac_signs[i]}</text>\n'

        return svg

    def _draw_house_lines(self) -> str:
        """Draw house division lines (simplified equal house system)."""
        svg = ""

        for i in range(12):
            angle_deg = i * 30
            angle_rad = math.radians(angle_deg - 90)

            x1 = self.center + self.house_radius * math.cos(angle_rad)
            y1 = self.center + self.house_radius * math.sin(angle_rad)
            x2 = self.center + self.inner_radius * math.cos(angle_rad)
            y2 = self.center + self.inner_radius * math.sin(angle_rad)

            svg += f'<line class="house-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'

            # Add house number
            house_text_radius = (self.house_radius + self.inner_radius) / 2
            text_angle_rad = math.radians((angle_deg + 15) - 90)
            text_x = self.center + house_text_radius * math.cos(text_angle_rad)
            text_y = self.center + house_text_radius * math.sin(text_angle_rad)

            house_num = i + 1
            svg += f'<text class="sign-text" x="{text_x}" y="{text_y}" style="font-size: 14px; fill: #888888;">{house_num}</text>\n'

        return svg

    def _add_planets(self, planets: Dict[str, any]) -> str:
        """Add planets to the chart."""
        svg = ""

        for planet_name, planet_data in planets.items():
            if planet_name in self.planet_symbols:
                # Convert longitude to chart position
                longitude = planet_data.longitude
                angle_deg = longitude - 90  # Adjust for chart orientation
                angle_rad = math.radians(angle_deg)

                # Calculate position
                x = self.center + self.planet_radius * math.cos(angle_rad)
                y = self.center + self.planet_radius * math.sin(angle_rad)

                # Get planet symbol and color
                symbol = self.planet_symbols[planet_name]
                color = self.planet_colors[planet_name]

                # Add planet symbol
                svg += f'<text class="planet-text" x="{x}" y="{y}" fill="{color}">{symbol}</text>\n'

                # Add degree marker
                degrees = int(longitude % 30)
                minutes = int((longitude % 30 - degrees) * 60)
                degree_text = f"{degrees}°{minutes:02d}'"

                # Position degree text slightly outward
                degree_radius = self.planet_radius + 25
                degree_x = self.center + degree_radius * math.cos(angle_rad)
                degree_y = self.center + degree_radius * math.sin(angle_rad)

                svg += f'<text x="{degree_x}" y="{degree_y}" style="fill: #cccccc; font-size: 10px; text-anchor: middle;">{degree_text}</text>\n'

        return svg

    def _draw_major_aspects(self, planets: Dict[str, any]) -> str:
        """Draw lines for major aspects between planets."""
        svg = ""

        planet_positions = {}
        for planet_name, planet_data in planets.items():
            if planet_name in self.planet_symbols:
                longitude = planet_data.longitude
                angle_rad = math.radians(longitude - 90)
                x = self.center + self.planet_radius * math.cos(angle_rad)
                y = self.center + self.planet_radius * math.sin(angle_rad)
                planet_positions[planet_name] = (x, y, longitude)

        # Check for major aspects (conjunction, opposition, square, trine, sextile)
        planet_list = list(planet_positions.keys())
        aspect_count = 0

        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                planet1 = planet_list[i]
                planet2 = planet_list[j]

                lon1 = planet_positions[planet1][2]
                lon2 = planet_positions[planet2][2]

                # Calculate angular separation
                angle_diff = abs(lon1 - lon2)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                # Check for major aspects with appropriate orbs
                aspect_info = None
                if abs(angle_diff - 0) <= 10:  # Conjunction - wider orb
                    aspect_info = ("Conjunction", "#ff6b6b", "♂", 3)
                elif abs(angle_diff - 60) <= 6:  # Sextile
                    aspect_info = ("Sextile", "#4ecdc4", "*", 2)
                elif abs(angle_diff - 90) <= 8:  # Square
                    aspect_info = ("Square", "#ff9f43", "□", 3)
                elif abs(angle_diff - 120) <= 8:  # Trine
                    aspect_info = ("Trine", "#6c5ce7", "△", 2)
                elif abs(angle_diff - 180) <= 10:  # Opposition - wider orb
                    aspect_info = ("Opposition", "#fd79a8", "☍", 3)

                if aspect_info:
                    aspect_name, aspect_color, aspect_symbol, line_width = aspect_info
                    x1, y1 = planet_positions[planet1][:2]
                    x2, y2 = planet_positions[planet2][:2]

                    # Draw aspect line with appropriate thickness and style
                    if aspect_name in ["Square", "Opposition"]:
                        # Challenging aspects - dashed line
                        svg += f'<line class="aspect-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{aspect_color}" stroke-width="{line_width}" stroke-dasharray="5,5" opacity="0.8"/>\n'
                    else:
                        # Harmonious aspects - solid line
                        svg += f'<line class="aspect-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{aspect_color}" stroke-width="{line_width}" opacity="0.7"/>\n'

                    # Add aspect label at midpoint
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2

                    # Add small background circle for readability
                    svg += f'<circle cx="{mid_x}" cy="{mid_y}" r="8" fill="#1a1a2e" stroke="{aspect_color}" stroke-width="1" opacity="0.9"/>\n'

                    # Add aspect symbol
                    svg += f'<text x="{mid_x}" y="{mid_y}" fill="{aspect_color}" font-size="10" text-anchor="middle" dominant-baseline="central" font-weight="bold">{aspect_symbol}</text>\n'

                    aspect_count += 1

        # Add aspect count info
        if aspect_count > 0:
            svg += f'<!-- Found {aspect_count} major aspects -->\n'

        return svg

    def _add_legend(self) -> str:
        """Add legend explaining symbols and aspects."""
        svg = ""
        legend_y = self.chart_size + 20

        svg += f'<text class="legend" x="20" y="{legend_y}">Legend:</text>\n'

        # Planet symbols
        x = 20
        y = legend_y + 20
        for planet, symbol in list(self.planet_symbols.items())[:5]:
            color = self.planet_colors[planet]
            svg += f'<text class="legend" x="{x}" y="{y}" fill="{color}">{symbol} {planet}</text>\n'
            x += 100

        # Second row of planets
        x = 20
        y += 20
        for planet, symbol in list(self.planet_symbols.items())[5:]:
            color = self.planet_colors[planet]
            svg += f'<text class="legend" x="{x}" y="{y}" fill="{color}">{symbol} {planet}</text>\n'
            x += 100

        # Zodiac signs legend
        y += 25
        svg += f'<text class="legend" x="20" y="{y}">Zodiac Signs:</text>\n'
        y += 15

        # First row of signs (6 signs)
        x = 20
        for i in range(6):
            symbol = self.zodiac_signs[i]
            name = self.sign_names[i]
            svg += f'<text class="legend" x="{x}" y="{y}" fill="#ffffff">{symbol} {name}</text>\n'
            x += 120

        # Second row of signs (6 signs)
        y += 15
        x = 20
        for i in range(6, 12):
            symbol = self.zodiac_signs[i]
            name = self.sign_names[i]
            svg += f'<text class="legend" x="{x}" y="{y}" fill="#ffffff">{symbol} {name}</text>\n'
            x += 120

        # Aspect legend
        y += 25
        svg += f'<text class="legend" x="20" y="{y}">Aspects (with symbols):</text>\n'
        y += 15

        aspects = [
            ("Conjunction ♂", "#ff6b6b", "solid"),
            ("Sextile *", "#4ecdc4", "solid"),
            ("Square □", "#ff9f43", "dashed"),
            ("Trine △", "#6c5ce7", "solid"),
            ("Opposition ☍", "#fd79a8", "dashed")
        ]

        x = 20
        for aspect_name, color, line_style in aspects:
            if line_style == "dashed":
                svg += f'<line x1="{x}" y1="{y}" x2="{x+20}" y2="{y}" stroke="{color}" stroke-width="2" stroke-dasharray="3,3"/>\n'
            else:
                svg += f'<line x1="{x}" y1="{y}" x2="{x+20}" y2="{y}" stroke="{color}" stroke-width="2"/>\n'
            svg += f'<text class="legend" x="{x+25}" y="{y+4}">{aspect_name}</text>\n'
            x += 140

        # Add note about aspect lines
        y += 25
        svg += f'<text class="legend" x="20" y="{y}" style="font-size: 10px; fill: #cccccc;">Note: Solid lines = Harmonious aspects, Dashed lines = Challenging aspects</text>\n'

        return svg

    def save_chart(self, svg_content: str, filename: str) -> str:
        """Save SVG chart to file."""
        if not filename.endswith('.svg'):
            filename += '.svg'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return filename

def create_chart_for_planets(planets_dict: Dict[str, any], title: str, output_dir: str = "") -> str:
    """Helper function to create chart from planets dictionary."""
    generator = AstrologicalChartGenerator()
    svg_content = generator.generate_chart(planets_dict, title)

    # Create filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    filename = f"{safe_title.lower()}_chart.svg"

    if output_dir:
        filename = os.path.join(output_dir, filename)

    return generator.save_chart(svg_content, filename)

if __name__ == "__main__":
    # Test chart generation
    test_planets = {
        'SUN': type('Planet', (), {'longitude': 45.5})(),
        'MOON': type('Planet', (), {'longitude': 120.3})(),
        'MERCURY': type('Planet', (), {'longitude': 60.8})(),
        'VENUS': type('Planet', (), {'longitude': 90.2})(),
        'MARS': type('Planet', (), {'longitude': 200.7})(),
    }

    generator = AstrologicalChartGenerator()
    svg_content = generator.generate_chart(test_planets, "Test Chart")
    filename = generator.save_chart(svg_content, "test_chart.svg")
    print(f"Test chart created: {filename}")
    print("Open the SVG file in any web browser to view the chart!")