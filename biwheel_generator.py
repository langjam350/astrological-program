#!/usr/bin/env python3
"""
Bi-Wheel Astrological Chart Generator
Creates a dual-ring chart with natal planets (inner) and transit planets (outer).
Aspect lines drawn between natal and transit positions.
"""

import math
import os
from typing import Dict, List, Tuple, Optional


# Planet display order, symbols, and colors
PLANET_ORDER = ['SUN', 'MOON', 'MERCURY', 'VENUS', 'MARS',
                'JUPITER', 'SATURN', 'URANUS', 'NEPTUNE', 'PLUTO']

PLANET_SYMBOLS = {
    'SUN': '\u2609', 'MOON': '\u263d', 'MERCURY': '\u263f',
    'VENUS': '\u2640', 'MARS': '\u2642', 'JUPITER': '\u2643',
    'SATURN': '\u2644', 'URANUS': '\u2645', 'NEPTUNE': '\u2646',
    'PLUTO': '\u2647',
}

PLANET_COLORS = {
    'SUN': '#B8860B', 'MOON': '#707070', 'MERCURY': '#CC7000',
    'VENUS': '#2E8B57', 'MARS': '#CC3300', 'JUPITER': '#2255BB',
    'SATURN': '#6B3000', 'URANUS': '#008B8B', 'NEPTUNE': '#2B5F8B',
    'PLUTO': '#6B006B',
}

ZODIAC_SYMBOLS = [
    '\u2648', '\u2649', '\u264a', '\u264b', '\u264c', '\u264d',
    '\u264e', '\u264f', '\u2650', '\u2651', '\u2652', '\u2653',
]

SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]

# Aspect definitions: (target_angle, default_orb, symbol, color, label, is_challenging)
ASPECT_DEFS = [
    (0,   8, '\u260c', '#ff6b6b', 'Conjunction', False),
    (60,  6, '\u2731', '#4ecdc4', 'Sextile',     False),
    (90,  8, '\u25a1', '#ff9f43', 'Square',       True),
    (120, 8, '\u25b3', '#6c5ce7', 'Trine',        False),
    (180, 8, '\u260d', '#fd79a8', 'Opposition',    True),
]


def _polar(cx: float, cy: float, radius: float, angle_deg: float) -> Tuple[float, float]:
    """Convert polar coordinates to SVG x, y.  0° = top (Aries cusp)."""
    rad = math.radians(angle_deg - 90)
    return cx + radius * math.cos(rad), cy + radius * math.sin(rad)


def _spread_labels(positions: List[Tuple[str, float]], min_gap: float = 12.0) -> List[Tuple[str, float]]:
    """Nudge label angles so overlapping planets don't stack on top of each other.

    Takes list of (name, longitude) sorted by longitude and returns
    (name, display_angle) with a minimum angular gap enforced.
    """
    if not positions:
        return []

    sorted_pos = sorted(positions, key=lambda p: p[1])
    display = [list(p) for p in sorted_pos]  # mutable copies

    # Forward pass: push apart
    for i in range(1, len(display)):
        gap = display[i][1] - display[i - 1][1]
        if gap < min_gap:
            display[i][1] = display[i - 1][1] + min_gap

    # Backward pass: pull back within 360
    for i in range(len(display) - 2, -1, -1):
        gap = display[i + 1][1] - display[i][1]
        if gap < min_gap:
            display[i][1] = display[i + 1][1] - min_gap

    return [(d[0], d[1]) for d in display]


def _find_aspect(lon1: float, lon2: float,
                 aspects_data: Optional[Dict] = None) -> Optional[Tuple]:
    """Return (symbol, color, orb, is_challenging) if an aspect exists, else None."""
    angle = abs(lon1 - lon2)
    if angle > 180:
        angle = 360 - angle

    # Build orb overrides from aspects_data
    orb_overrides = {}
    if aspects_data:
        name_to_idx = {
            'CONJUNCTION': 0, 'SEXTILE': 1, 'SQUARE': 2,
            'TRINE': 3, 'OPPOSITION': 4,
        }
        for aname, ainfo in aspects_data.items():
            parts = ainfo[0].split(';')
            if len(parts) >= 2 and aname.upper() in name_to_idx:
                orb_overrides[name_to_idx[aname.upper()]] = float(parts[1])

    for i, (target, default_orb, sym, color, _label, challenging) in enumerate(ASPECT_DEFS):
        orb = orb_overrides.get(i, default_orb)
        if abs(angle - target) <= orb:
            return (sym, color, abs(angle - target), challenging)

    return None


def generate_biwheel(natal_planets: Dict[str, object],
                     transit_planets: Dict[str, object],
                     aspects_data: Optional[Dict] = None,
                     title: str = "Natal / Transit Bi-Wheel") -> str:
    """Generate an SVG bi-wheel chart.

    Args:
        natal_planets:   dict of planet_name -> object with .longitude
        transit_planets: dict of planet_name -> object with .longitude
        aspects_data:    optional aspect orb data from aspects.txt
        title:           chart title

    Returns:
        SVG string.
    """
    # --- layout constants ---
    size = 900
    cx = cy = size / 2
    legend_height = 160
    total_height = size + legend_height

    r_outer      = 400   # outer edge of zodiac band
    r_zodiac_mid = 370   # zodiac symbol placement
    r_inner_zodiac = 340 # inner edge of zodiac band

    r_transit    = 310   # transit planet symbols
    r_transit_tick = 330 # small tick from zodiac ring inward

    r_divider    = 270   # ring dividing transit / natal zones

    r_natal      = 230   # natal planet symbols
    r_natal_tick = 260   # small tick from divider outward

    r_aspect     = 180   # aspect lines drawn inside this radius

    # --- begin SVG ---
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
<style>
    .bg {{ fill: #ffffff; }}
    .ring {{ fill: none; stroke: #aaaaaa; }}
    .zodiac-div {{ stroke: #999999; stroke-width: 1.5; }}
    .sign-text {{ fill: #333333; font-family: Arial, sans-serif; font-size: 18px;
                  text-anchor: middle; dominant-baseline: central; }}
    .planet {{ font-family: Arial, sans-serif; font-size: 16px;
              text-anchor: middle; dominant-baseline: central; font-weight: bold; }}
    .planet-label {{ font-family: Arial, sans-serif; font-size: 9px;
                     text-anchor: middle; dominant-baseline: central; fill: #555555; }}
    .degree-text {{ font-family: Arial, sans-serif; font-size: 8px;
                    text-anchor: middle; dominant-baseline: central; fill: #666666; }}
    .title {{ fill: #111111; font-family: Arial, sans-serif; font-size: 22px;
              font-weight: bold; text-anchor: middle; }}
    .ring-label {{ fill: #444444; font-family: Arial, sans-serif; font-size: 10px;
                   font-weight: bold; text-anchor: middle; dominant-baseline: central; }}
    .tick {{ stroke-width: 1; }}
    .aspect-line {{ stroke-width: 1.2; opacity: 0.7; }}
    .legend {{ fill: #333333; font-family: Arial, sans-serif; font-size: 11px;
              dominant-baseline: central; }}
    .aspect-sym {{ font-family: Arial, sans-serif; font-size: 14px;
                   text-anchor: middle; dominant-baseline: central; font-weight: bold; }}
</style>

<!-- Background -->
<rect class="bg" width="{size}" height="{total_height}"/>

<!-- Title -->
<text class="title" x="{cx}" y="28">{title}</text>

'''

    # --- circles ---
    for r, w in [(r_outer, 2.5), (r_inner_zodiac, 2), (r_divider, 1.5)]:
        svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" class="ring" stroke-width="{w}"/>\n'

    # --- zodiac wheel ---
    for i in range(12):
        angle = i * 30
        # division line
        x1, y1 = _polar(cx, cy, r_inner_zodiac, angle)
        x2, y2 = _polar(cx, cy, r_outer, angle)
        svg += f'<line class="zodiac-div" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'

        # sign symbol at midpoint of sector
        sx, sy = _polar(cx, cy, r_zodiac_mid, angle + 15)
        svg += f'<text class="sign-text" x="{sx}" y="{sy}">{ZODIAC_SYMBOLS[i]}</text>\n'

    # --- ring labels ---
    # Place "TRANSIT" and "NATAL" labels in a quiet area
    tx, ty = _polar(cx, cy, (r_transit + r_divider) / 2, 180)
    svg += f'<text class="ring-label" x="{tx}" y="{ty}">TRANSIT</text>\n'
    nx, ny = _polar(cx, cy, (r_natal + r_divider) / 2, 180)
    svg += f'<text class="ring-label" x="{nx}" y="{ny}">NATAL</text>\n'

    # --- helper to place a set of planets ---
    def _place_planets(planets: Dict, radius: float, tick_inner: float,
                       tick_outer: float, tag_suffix: str) -> Dict[str, Tuple[float, float]]:
        """Place planet symbols and return dict of name -> (x, y) at aspect radius."""
        ordered = [(name, planets[name].longitude)
                   for name in PLANET_ORDER if name in planets]
        spread = _spread_labels(ordered, min_gap=10)

        positions = {}
        for name, display_angle in spread:
            real_lon = planets[name].longitude
            color = PLANET_COLORS.get(name, '#ffffff')
            symbol = PLANET_SYMBOLS.get(name, '?')

            # tick mark at real longitude
            tx1, ty1 = _polar(cx, cy, tick_inner, real_lon)
            tx2, ty2 = _polar(cx, cy, tick_outer, real_lon)
            svg_tick = f'<line class="tick" x1="{tx1}" y1="{ty1}" x2="{tx2}" y2="{ty2}" stroke="{color}" opacity="0.5"/>\n'

            # connector from tick to symbol if spread moved it
            px, py = _polar(cx, cy, radius, display_angle)
            if abs(display_angle - real_lon) > 1:
                svg_tick += f'<line x1="{tx2 if tick_inner < tick_outer else tx1}" y1="{ty2 if tick_inner < tick_outer else ty1}" '
                svg_tick += f'x2="{px}" y2="{py}" stroke="{color}" stroke-width="0.5" opacity="0.3"/>\n'

            # planet symbol
            svg_tick += f'<text class="planet" x="{px}" y="{py}" fill="{color}">{symbol}</text>\n'

            # degree label just inside/outside
            deg = int(real_lon % 30)
            mins = int((real_lon % 30 - deg) * 60)
            label_r = radius - 16 if tag_suffix == "natal" else radius + 16
            lx, ly = _polar(cx, cy, label_r, display_angle)
            svg_tick += f'<text class="degree-text" x="{lx}" y="{ly}">{deg}\u00b0{mins:02d}\'</text>\n'

            # save position at aspect radius for drawing aspect lines
            ax, ay = _polar(cx, cy, r_aspect, real_lon)
            positions[name] = (ax, ay)

            nonlocal svg
            svg += svg_tick

        return positions

    # Place transit planets (outer ring)
    transit_pos = _place_planets(transit_planets, r_transit, r_transit_tick,
                                 r_inner_zodiac, "transit")

    # Place natal planets (inner ring)
    natal_pos = _place_planets(natal_planets, r_natal, r_divider,
                               r_natal_tick, "natal")

    # --- aspect lines between natal and transit ---
    aspect_count = 0
    for t_name in PLANET_ORDER:
        if t_name not in transit_planets or t_name not in transit_pos:
            continue
        for n_name in PLANET_ORDER:
            if n_name not in natal_planets or n_name not in natal_pos:
                continue

            result = _find_aspect(
                transit_planets[t_name].longitude,
                natal_planets[n_name].longitude,
                aspects_data
            )
            if result:
                sym, color, orb, challenging = result
                tx, ty = transit_pos[t_name]
                nx, ny = natal_pos[n_name]

                dash = ' stroke-dasharray="5,4"' if challenging else ''
                svg += f'<line class="aspect-line" x1="{tx}" y1="{ty}" x2="{nx}" y2="{ny}" '
                svg += f'stroke="{color}"{dash}/>\n'
                aspect_count += 1

    svg += f'<!-- {aspect_count} aspect lines drawn -->\n'

    # --- legend ---
    ly = size + 20

    # Planet legend - row 1
    svg += f'<text class="legend" x="20" y="{ly}" style="font-weight:bold;">Planets:</text>\n'
    ly += 18
    lx = 20
    for i, name in enumerate(PLANET_ORDER):
        sym = PLANET_SYMBOLS[name]
        col = PLANET_COLORS[name]
        svg += f'<text class="legend" x="{lx}" y="{ly}" fill="{col}">{sym} {name.title()}</text>\n'
        lx += 90
        if i == 4:
            lx = 20
            ly += 16

    # Zodiac legend
    ly += 22
    svg += f'<text class="legend" x="20" y="{ly}" style="font-weight:bold;">Signs:</text>\n'
    ly += 16
    lx = 20
    for i in range(12):
        svg += f'<text class="legend" x="{lx}" y="{ly}">{ZODIAC_SYMBOLS[i]} {SIGN_NAMES[i]}</text>\n'
        lx += 110
        if i == 5:
            lx = 20
            ly += 16

    # Aspect legend
    ly += 22
    svg += f'<text class="legend" x="20" y="{ly}" style="font-weight:bold;">Aspects:</text>\n'
    ly += 16
    lx = 20
    for target, _orb, sym, color, label, challenging in ASPECT_DEFS:
        dash = ' stroke-dasharray="4,3"' if challenging else ''
        svg += f'<line x1="{lx}" y1="{ly}" x2="{lx + 20}" y2="{ly}" stroke="{color}" stroke-width="2"{dash}/>\n'
        svg += f'<text class="legend" x="{lx + 26}" y="{ly}">{sym} {label}</text>\n'
        lx += 140

    svg += "</svg>"
    return svg


def save_biwheel(svg_content: str, filename: str) -> str:
    """Save SVG to file."""
    if not filename.endswith('.svg'):
        filename += '.svg'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    return filename


def create_biwheel(natal_planets: Dict[str, object],
                   transit_planets: Dict[str, object],
                   aspects_data: Optional[Dict] = None,
                   title: str = "Natal / Transit Bi-Wheel",
                   output_dir: str = "") -> str:
    """Helper: generate and save a bi-wheel chart, return the file path."""
    svg = generate_biwheel(natal_planets, transit_planets, aspects_data, title)
    safe = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe.replace(' ', '_').lower()}_biwheel.svg"
    if output_dir:
        filename = os.path.join(output_dir, filename)
    return save_biwheel(svg, filename)


if __name__ == "__main__":
    # Quick visual test with sample data
    P = type('Planet', (), {})

    def _make(lon):
        p = P()
        p.longitude = lon
        return p

    natal = {
        'SUN': _make(54.2), 'MOON': _make(198.7), 'MERCURY': _make(40.1),
        'VENUS': _make(72.5), 'MARS': _make(330.3), 'JUPITER': _make(95.8),
        'SATURN': _make(290.1), 'URANUS': _make(278.4), 'NEPTUNE': _make(283.9),
        'PLUTO': _make(225.6),
    }
    transit = {
        'SUN': _make(3.5), 'MOON': _make(142.1), 'MERCURY': _make(348.9),
        'VENUS': _make(30.4), 'MARS': _make(108.2), 'JUPITER': _make(99.3),
        'SATURN': _make(3.8), 'URANUS': _make(55.1), 'NEPTUNE': _make(359.7),
        'PLUTO': _make(304.2),
    }

    path = create_biwheel(natal, transit, title="Test Bi-Wheel")
    print(f"Test bi-wheel created: {path}")
    print("Open in a browser to preview.")
