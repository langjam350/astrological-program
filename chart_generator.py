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
        self.ascendant = None  # Set by generate_chart when provided

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
            'SUN': '#B8860B',
            'MOON': '#707070',
            'MERCURY': '#CC7000',
            'VENUS': '#2E8B57',
            'MARS': '#CC3300',
            'JUPITER': '#2255BB',
            'SATURN': '#6B3000',
            'URANUS': '#008B8B',
            'NEPTUNE': '#2B5F8B',
            'PLUTO': '#6B006B'
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

    def generate_chart(self, planets: Dict[str, any], chart_title: str = "Astrological Chart",
                       ascendant: float = None) -> str:
        """Generate SVG chart from planetary data.

        Args:
            planets: Dictionary of planet data
            chart_title: Title for the chart
            ascendant: Ascendant degree (0-360). When provided, houses are
                       positioned starting from this degree.
        """
        self.ascendant = ascendant
        svg_content = self._create_svg_header()

        # Add title
        svg_content += self._add_title(chart_title)

        # Draw zodiac wheel
        svg_content += self._draw_zodiac_wheel()

        # Draw house lines based on ascendant
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
    .chart-bg {{ fill: #ffffff; }}
    .zodiac-line {{ stroke: #aaaaaa; stroke-width: 2; fill: none; }}
    .house-line {{ stroke: #bbbbbb; stroke-width: 1; fill: none; }}
    .sign-text {{ fill: #333333; font-family: Arial, sans-serif; font-size: 20px; text-anchor: middle; dominant-baseline: central; }}
    .planet-text {{ font-family: Arial, sans-serif; font-size: 18px; text-anchor: middle; dominant-baseline: central; }}
    .title {{ fill: #111111; font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; text-anchor: middle; }}
    .legend {{ fill: #333333; font-family: Arial, sans-serif; font-size: 12px; }}
    .aspect-line {{ stroke: #888888; stroke-width: 1; opacity: 0.6; }}
</style>

<!-- Background -->
<rect class="chart-bg" width="{self.chart_size}" height="{self.chart_size + 180}"/>

<!-- Outer circle -->
<circle cx="{self.center}" cy="{self.center}" r="{self.outer_radius}"
        fill="none" stroke="#aaaaaa" stroke-width="3"/>

<!-- Inner circle -->
<circle cx="{self.center}" cy="{self.center}" r="{self.inner_radius}"
        fill="none" stroke="#aaaaaa" stroke-width="2"/>

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
        """Draw house division lines using Equal House system based on Ascendant."""
        svg = ""

        # Use ascendant as the starting degree for House 1, or default to 0
        asc_offset = self.ascendant if self.ascendant is not None else 0.0

        for i in range(12):
            # Each house cusp starts at ascendant + i*30 degrees
            angle_deg = asc_offset + i * 30
            angle_rad = math.radians(angle_deg - 90)

            x1 = self.center + self.house_radius * math.cos(angle_rad)
            y1 = self.center + self.house_radius * math.sin(angle_rad)
            x2 = self.center + self.inner_radius * math.cos(angle_rad)
            y2 = self.center + self.inner_radius * math.sin(angle_rad)

            # Emphasize the Ascendant line (House 1 cusp)
            if i == 0 and self.ascendant is not None:
                svg += f'<line class="house-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke: #ff6666; stroke-width: 2;"/>\n'
                # Add "ASC" label
                label_radius = self.inner_radius - 15
                label_x = self.center + label_radius * math.cos(angle_rad)
                label_y = self.center + label_radius * math.sin(angle_rad)
                svg += f'<text x="{label_x}" y="{label_y}" style="font-size: 10px; fill: #ff6666; text-anchor: middle; dominant-baseline: central; font-weight: bold;">ASC</text>\n'
            else:
                svg += f'<line class="house-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'

            # Add house number at the midpoint of the house sector
            house_text_radius = (self.house_radius + self.inner_radius) / 2
            text_angle_rad = math.radians((angle_deg + 15) - 90)
            text_x = self.center + house_text_radius * math.cos(text_angle_rad)
            text_y = self.center + house_text_radius * math.sin(text_angle_rad)

            house_num = i + 1
            svg += f'<text class="sign-text" x="{text_x}" y="{text_y}" style="font-size: 14px; fill: #999999;">{house_num}</text>\n'

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

                svg += f'<text x="{degree_x}" y="{degree_y}" style="fill: #666666; font-size: 10px; text-anchor: middle;">{degree_text}</text>\n'

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
                    svg += f'<circle cx="{mid_x}" cy="{mid_y}" r="8" fill="#ffffff" stroke="{aspect_color}" stroke-width="1" opacity="0.9"/>\n'

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
            svg += f'<text class="legend" x="{x}" y="{y}" fill="#333333">{symbol} {name}</text>\n'
            x += 120

        # Second row of signs (6 signs)
        y += 15
        x = 20
        for i in range(6, 12):
            symbol = self.zodiac_signs[i]
            name = self.sign_names[i]
            svg += f'<text class="legend" x="{x}" y="{y}" fill="#333333">{symbol} {name}</text>\n'
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
        svg += f'<text class="legend" x="20" y="{y}" style="font-size: 10px; fill: #666666;">Note: Solid lines = Harmonious aspects, Dashed lines = Challenging aspects</text>\n'

        return svg

    def generate_aspect_grid(self, natal_planets: Dict[str, any],
                              transit_planets: Dict[str, any],
                              aspects_data: Dict[str, list] = None,
                              chart_title: str = "Natal-Transit Aspect Grid") -> str:
        """Generate an SVG aspect grid showing aspects between natal and transit planets.

        Args:
            natal_planets: Dict of natal planet name -> object with .longitude
            transit_planets: Dict of transit planet name -> object with .longitude
            aspects_data: Optional dict of aspect definitions from aspects.txt
                          Format: {'CONJUNCTION': ['0;8;...'], ...}
                          If None, uses default orbs.
            chart_title: Title for the grid
        """
        # Default aspect definitions: (target_angle, orb, symbol, color)
        aspect_defs = [
            (0, 8, '☌', '#ff6b6b', 'Conjunction'),
            (60, 6, '✱', '#4ecdc4', 'Sextile'),
            (90, 8, '□', '#ff9f43', 'Square'),
            (120, 8, '△', '#6c5ce7', 'Trine'),
            (180, 8, '☍', '#fd79a8', 'Opposition'),
        ]

        # Override orbs from aspects_data if provided
        if aspects_data:
            orb_map = {}
            for aspect_name, aspect_info in aspects_data.items():
                parts = aspect_info[0].split(';')
                if len(parts) >= 2:
                    orb_map[aspect_name.upper()] = float(parts[1])
            name_map = {
                'CONJUNCTION': 0, 'SEXTILE': 1, 'SQUARE': 2,
                'TRINE': 3, 'OPPOSITION': 4
            }
            for name, idx in name_map.items():
                if name in orb_map:
                    target, _, sym, col, label = aspect_defs[idx]
                    aspect_defs[idx] = (target, orb_map[name], sym, col, label)

        # Planet order for grid
        planet_order = [p for p in self.planet_symbols.keys()
                        if p in natal_planets and p in transit_planets]

        num_planets = len(planet_order)
        if num_planets == 0:
            return ""

        # Grid dimensions
        cell_size = 52
        header_size = 90
        padding = 30
        title_height = 50
        legend_height = 80

        grid_width = header_size + num_planets * cell_size
        total_width = grid_width + padding * 2
        total_height = title_height + header_size + num_planets * cell_size + legend_height + padding * 2

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
<style>
    .grid-bg {{ fill: #ffffff; }}
    .cell-border {{ stroke: #cccccc; stroke-width: 1; fill: none; }}
    .cell-bg {{ fill: #ffffff; }}
    .cell-bg-alt {{ fill: #f5f5f5; }}
    .header-text {{ font-family: Arial, sans-serif; font-size: 18px; text-anchor: middle; dominant-baseline: central; }}
    .header-label {{ fill: #555555; font-family: Arial, sans-serif; font-size: 11px; text-anchor: middle; dominant-baseline: central; }}
    .aspect-symbol {{ font-family: Arial, sans-serif; font-size: 16px; text-anchor: middle; dominant-baseline: central; font-weight: bold; }}
    .orb-text {{ fill: #666666; font-family: Arial, sans-serif; font-size: 9px; text-anchor: middle; dominant-baseline: central; }}
    .title {{ fill: #111111; font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; text-anchor: middle; }}
    .axis-label {{ fill: #555555; font-family: Arial, sans-serif; font-size: 11px; font-weight: bold; text-anchor: middle; }}
    .legend-text {{ fill: #333333; font-family: Arial, sans-serif; font-size: 11px; dominant-baseline: central; }}
</style>

<!-- Background -->
<rect class="grid-bg" width="{total_width}" height="{total_height}"/>

'''

        # Title
        svg += f'<text class="title" x="{total_width / 2}" y="{padding + 20}">{chart_title}</text>\n'

        # Grid origin
        ox = padding + header_size
        oy = title_height + padding + header_size

        # Axis labels
        col_center = ox + (num_planets * cell_size) / 2
        svg += f'<text class="axis-label" x="{col_center}" y="{oy - header_size + 8}">NATAL</text>\n'

        row_center = oy + (num_planets * cell_size) / 2
        svg += f'<text class="axis-label" x="{padding + 10}" y="{row_center}" '
        svg += f'transform="rotate(-90, {padding + 10}, {row_center})">TRANSIT</text>\n'

        # Column headers (natal planets)
        for col, planet_name in enumerate(planet_order):
            cx = ox + col * cell_size + cell_size / 2
            cy_sym = oy - header_size / 2 + 6
            cy_lbl = cy_sym + 16
            symbol = self.planet_symbols[planet_name]
            color = self.planet_colors[planet_name]
            svg += f'<text class="header-text" x="{cx}" y="{cy_sym}" fill="{color}">{symbol}</text>\n'
            short_name = planet_name[:3].title()
            svg += f'<text class="header-label" x="{cx}" y="{cy_lbl}">{short_name}</text>\n'

        # Row headers (transit planets)
        for row, planet_name in enumerate(planet_order):
            cy = oy + row * cell_size + cell_size / 2
            cx_sym = ox - header_size * 2 / 3
            cx_lbl = ox - header_size / 3
            symbol = self.planet_symbols[planet_name]
            color = self.planet_colors[planet_name]
            svg += f'<text class="header-text" x="{cx_sym}" y="{cy}" fill="{color}">{symbol}</text>\n'
            short_name = planet_name[:3].title()
            svg += f'<text class="header-label" x="{cx_lbl}" y="{cy}">{short_name}</text>\n'

        # Grid cells
        for row, transit_name in enumerate(planet_order):
            for col, natal_name in enumerate(planet_order):
                cx = ox + col * cell_size
                cy = oy + row * cell_size

                # Alternating cell background
                bg_class = "cell-bg-alt" if (row + col) % 2 == 0 else "cell-bg"
                svg += f'<rect class="{bg_class}" x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}"/>\n'
                svg += f'<rect class="cell-border" x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}"/>\n'

                # Calculate aspect
                natal_lon = natal_planets[natal_name].longitude
                transit_lon = transit_planets[transit_name].longitude
                angle_diff = abs(transit_lon - natal_lon)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff

                # Check each aspect type
                for target_angle, orb, symbol, color, label in aspect_defs:
                    if abs(angle_diff - target_angle) <= orb:
                        actual_orb = abs(angle_diff - target_angle)
                        orb_display = f"{actual_orb:.0f}°"

                        # Aspect symbol
                        sym_x = cx + cell_size / 2
                        sym_y = cy + cell_size / 2 - 6
                        svg += f'<text class="aspect-symbol" x="{sym_x}" y="{sym_y}" fill="{color}">{symbol}</text>\n'

                        # Orb value
                        orb_x = cx + cell_size / 2
                        orb_y = cy + cell_size / 2 + 10
                        svg += f'<text class="orb-text" x="{orb_x}" y="{orb_y}">{orb_display}</text>\n'
                        break  # Use tightest aspect match

        # Grid outer border
        svg += f'<rect x="{ox}" y="{oy}" width="{num_planets * cell_size}" height="{num_planets * cell_size}" '
        svg += f'fill="none" stroke="#999999" stroke-width="2"/>\n'

        # Legend
        legend_y = oy + num_planets * cell_size + 20
        legend_x = padding + 10
        for i, (_, _, symbol, color, label) in enumerate(aspect_defs):
            lx = legend_x + i * 130
            svg += f'<text class="aspect-symbol" x="{lx}" y="{legend_y}" fill="{color}" style="text-anchor: start;">{symbol}</text>\n'
            svg += f'<text class="legend-text" x="{lx + 18}" y="{legend_y}">{label}</text>\n'

        svg += "</svg>"
        return svg

    def save_chart(self, svg_content: str, filename: str) -> str:
        """Save SVG chart to file."""
        if not filename.endswith('.svg'):
            filename += '.svg'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return filename

def create_chart_for_planets(planets_dict: Dict[str, any], title: str, output_dir: str = "",
                             ascendant: float = None) -> str:
    """Helper function to create chart from planets dictionary."""
    generator = AstrologicalChartGenerator()
    svg_content = generator.generate_chart(planets_dict, title, ascendant=ascendant)

    # Create filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    filename = f"{safe_title.lower()}_chart.svg"

    if output_dir:
        filename = os.path.join(output_dir, filename)

    return generator.save_chart(svg_content, filename)

def create_aspect_grid(natal_planets: Dict[str, any], transit_planets: Dict[str, any],
                       aspects_data: Dict[str, list] = None,
                       title: str = "Natal-Transit Aspect Grid",
                       output_dir: str = "") -> str:
    """Helper function to create an aspect grid SVG from natal and transit planet dicts."""
    generator = AstrologicalChartGenerator()
    svg_content = generator.generate_aspect_grid(natal_planets, transit_planets, aspects_data, title)

    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    filename = f"{safe_title.lower()}_grid.svg"

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