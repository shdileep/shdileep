#!/usr/bin/env python3
"""
Generate animated pseudo-3D SVG assets for the profile README.
Produces: hero-banner.svg, stack-orbit.svg, divider.svg
All SVGs use pure SMIL/CSS animation and are fully self-contained.
"""

import math
import os
import random
from pathlib import Path


def ensure_assets_dir():
    """Create assets directory if it doesn't exist."""
    Path("assets").mkdir(exist_ok=True)


def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t


def hex_to_rgb(hex_str):
    """Convert #RRGGBB to (r, g, b) tuple."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """Convert (r, g, b) to #RRGGBB."""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def interpolate_color(color1, color2, t):
    """Interpolate between two hex colors."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(lerp(r1, r2, t))
    g = int(lerp(g1, g2, t))
    b = int(lerp(b1, b2, t))
    return rgb_to_hex(r, g, b)


def rotate_x(x, y, z, angle):
    """Rotate point about X axis."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x, y * cos_a - z * sin_a, y * sin_a + z * cos_a


def rotate_y(x, y, z, angle):
    """Rotate point about Y axis."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a


def rotate_z(x, y, z, angle):
    """Rotate point about Z axis."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a, z


def project_point(x, y, z, perspective=5.5):
    """Apply perspective scale to a 3D point."""
    k = perspective / (perspective + z)
    return x * k, y * k, z, k


def build_cube_frames(half_size=92, center_x=915, center_y=178, num_frames=60):
    """
    Generate 60 frames of a rotating wireframe cube.
    Outer cube rotates Y, inner cube counter-rotates.
    Returns list of (outer_edges_frame, outer_verts_frame, inner_edges_frame, inner_verts_frame).
    """
    # Cube vertices (half-size)
    verts = [
        (-half_size, -half_size, -half_size),
        (half_size, -half_size, -half_size),
        (half_size, half_size, -half_size),
        (-half_size, half_size, -half_size),
        (-half_size, -half_size, half_size),
        (half_size, -half_size, half_size),
        (half_size, half_size, half_size),
        (-half_size, half_size, half_size),
    ]

    # Edges (vertex index pairs)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # front
        (4, 5), (5, 6), (6, 7), (7, 4),  # back
        (0, 4), (1, 5), (2, 6), (3, 7),  # sides
    ]

    frames = []
    for frame_idx in range(num_frames):
        t = frame_idx / num_frames
        theta_outer = t * 2 * math.pi
        theta_inner = -t * 2 * math.pi

        # Transform outer cube
        outer_verts_transformed = []
        for x, y, z in verts:
            x, y, z = rotate_y(x, y, z, theta_outer)
            x, y, z = rotate_x(x, y, z, 0.55)
            x, y, z = rotate_z(x, y, z, 0.25)
            x_proj, y_proj, z_proj, k = project_point(x, y, z, 5.5)
            outer_verts_transformed.append(
                (x_proj + center_x, y_proj + center_y, z_proj, k)
            )

        # Transform inner cube (45px, teal)
        inner_half = 45
        inner_verts = [
            (-inner_half, -inner_half, -inner_half),
            (inner_half, -inner_half, -inner_half),
            (inner_half, inner_half, -inner_half),
            (-inner_half, inner_half, -inner_half),
            (-inner_half, -inner_half, inner_half),
            (inner_half, -inner_half, inner_half),
            (inner_half, inner_half, inner_half),
            (-inner_half, inner_half, inner_half),
        ]
        inner_verts_transformed = []
        for x, y, z in inner_verts:
            x, y, z = rotate_y(x, y, z, theta_inner)
            x, y, z = rotate_x(x, y, z, 0.55)
            x, y, z = rotate_z(x, y, z, 0.25)
            x_proj, y_proj, z_proj, k = project_point(x, y, z, 5.5)
            inner_verts_transformed.append(
                (x_proj + center_x, y_proj + center_y, z_proj, k)
            )

        # Build edge coordinate lists
        outer_edges = []
        for v1, v2 in edges:
            x1, y1, _, k1 = outer_verts_transformed[v1]
            x2, y2, _, k2 = outer_verts_transformed[v2]
            outer_edges.append((x1, y1, x2, y2, (k1 + k2) / 2))

        inner_edges = []
        for v1, v2 in edges:
            x1, y1, _, k1 = inner_verts_transformed[v1]
            x2, y2, _, k2 = inner_verts_transformed[v2]
            inner_edges.append((x1, y1, x2, y2, (k1 + k2) / 2))

        frames.append(
            (outer_edges, outer_verts_transformed, inner_edges, inner_verts_transformed)
        )

    return frames


def generate_hero_banner():
    """Generate hero-banner.svg with 3D rotating cube."""
    width, height = 1200, 440
    frames = build_cube_frames()

    # Seed random for consistent stars
    random.seed(42)
    stars = [
        (random.uniform(72, 900), random.uniform(10, 340))
        for _ in range(45)
    ]

    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Hero banner with 3D cube animation">',
        '<defs>',
        '<style>',
        '@keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }',
        '.cursor { animation: blink 1.1s infinite; }',
        '@keyframes twinkling { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.9; } }',
        '.star { animation: twinkling 3s infinite; }',
        '@keyframes pulse-ring { 0% { r: 54; opacity: 0.6; } 50% { r: 70; opacity: 0.2; } 100% { r: 54; opacity: 0.6; } }',
        '@keyframes scroll-line { 0% { y1: 348; y2: 440; opacity: 0; } 5% { opacity: 1; } 95% { opacity: 1; } 100% { y1: 440; y2: 440; opacity: 0; } }',
        '</style>',
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" style="stop-color:#070a18;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#15103a;stop-opacity:1" />',
        '</linearGradient>',
        '<linearGradient id="nameGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '<stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />',
        '<stop offset="50%" style="stop-color:#c9bcff;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#5eead4;stop-opacity:1" />',
        '</linearGradient>',
        '<linearGradient id="horizonGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '<stop offset="0%" style="stop-color:#5eead4;stop-opacity:0" />',
        '<stop offset="50%" style="stop-color:#5eead4;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#5eead4;stop-opacity:0" />',
        '</linearGradient>',
        '<radialGradient id="cubeGlowGrad" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" style="stop-color:#7c5cff;stop-opacity:0.1" />',
        '<stop offset="100%" style="stop-color:#7c5cff;stop-opacity:0" />',
        '</radialGradient>',
        '<filter id="glow"><feGaussianBlur stdDeviation="2.2" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="url(#bgGrad)" />',
    ]

    # Horizon line
    svg_lines.append(
        '<line x1="0" y1="348" x2="1200" y2="348" stroke="#5eead4" stroke-width="2" opacity="0.6" />'
    )

    # Vanishing point lines
    vp_x = 615 - 300
    for i in range(1, 8):
        x_top = 615 + (i - 4) * 90
        svg_lines.append(
            f'<line x1="{vp_x}" y1="348" x2="{x_top}" y2="440" stroke="#7c5cff" stroke-width="1" opacity="0.3" />'
        )
        svg_lines.append(
            f'<line x1="{vp_x}" y1="348" x2="{1200 - x_top}" y2="440" stroke="#7c5cff" stroke-width="1" opacity="0.3" />'
        )

    # Scrolling perspective lines
    for i in range(7):
        svg_lines.append(f'<g id="scrollLine{i}"><line x1="0" y1="348" x2="1200" y2="348" stroke="#7c5cff" stroke-width="2" opacity="0.4" />')
        svg_lines.append(
            f'<animate attributeName="y1" values="348;440;348" dur="7s" begin="{i/7}s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y2" values="440;440;348" dur="7s" begin="{i/7}s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="stroke-opacity" values="0;0.4;0;0" dur="7s" begin="{i/7}s" repeatCount="indefinite" />'
        )
        svg_lines.append('</g>')

    # Stars
    for i, (sx, sy) in enumerate(stars):
        svg_lines.append(
            f'<circle cx="{sx}" cy="{sy}" r="1.2" fill="#c9bcff" class="star" style="animation-delay: {-i*0.15}s" />'
        )

    # Left side text
    svg_lines.append(
        '<text x="72" y="68" font-family="ui-monospace,SFMono-Regular,Consolas,Menlo,monospace" font-size="14" fill="#5eead4" letter-spacing="1">~/shdileep $ whoami<tspan class="cursor" baseline-shift="2">_</tspan></text>'
    )

    svg_lines.append(
        '<text x="72" y="164" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="84" font-weight="800" letter-spacing="-2" fill="url(#nameGrad)">Dileep Sai</text>'
    )

    svg_lines.append(
        '<text x="72" y="199" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="19" fill="#8f86c9">AI Engineer and Backend Developer</text>'
    )

    # Cycling subtitle
    subtitles = [
        "I build AI products that ship.",
        "Agentic workflows, RAG, FastAPI backends.",
        "LLMs turned into usable software.",
    ]
    for i, subtitle in enumerate(subtitles):
        svg_lines.append(
            f'<text x="72" y="232" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="16" fill="#a995ff">{subtitle}'
        )
        svg_lines.append(
            f'<animate attributeName="opacity" values="0;1;1;0" dur="12s" begin="{i*4}s" repeatCount="indefinite" />'
        )
        svg_lines.append('</text>')

    # Chips
    chip_y = 260
    chips = ["Agentic AI", "RAG", "FastAPI"]
    for i, chip in enumerate(chips):
        chip_x = 72 + i * 150
        svg_lines.append(
            f'<rect x="{chip_x}" y="{chip_y}" width="120" height="36" rx="18" fill="#0d0f24" stroke="#7c5cff" stroke-width="1.5" />'
        )
        svg_lines.append(
            f'<text x="{chip_x + 60}" y="{chip_y + 24}" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="14" fill="#c9bcff" text-anchor="middle">{chip}</text>'
        )

    # Outer cube glow (blurred, thick)
    svg_lines.append(f'<g filter="url(#glow)" opacity="0.55">')
    for edge_idx, (v1, v2) in enumerate(
        [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    ):
        x1_vals = ";".join(str(frames[f][0][edge_idx][0]) for f in range(len(frames)))
        y1_vals = ";".join(str(frames[f][0][edge_idx][1]) for f in range(len(frames)))
        x2_vals = ";".join(str(frames[f][0][edge_idx][2]) for f in range(len(frames)))
        y2_vals = ";".join(str(frames[f][0][edge_idx][3]) for f in range(len(frames)))
        svg_lines.append(
            f'<line x1="{frames[0][0][edge_idx][0]}" y1="{frames[0][0][edge_idx][1]}" x2="{frames[0][0][edge_idx][2]}" y2="{frames[0][0][edge_idx][3]}" stroke="#7c5cff" stroke-width="5" stroke-linecap="round">'
        )
        svg_lines.append(
            f'<animate attributeName="x1" values="{x1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y1" values="{y1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="x2" values="{x2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y2" values="{y2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append('</line>')
    svg_lines.append('</g>')

    # Outer cube crisp
    svg_lines.append(f'<g>')
    for edge_idx, (v1, v2) in enumerate(
        [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    ):
        x1_vals = ";".join(str(frames[f][0][edge_idx][0]) for f in range(len(frames)))
        y1_vals = ";".join(str(frames[f][0][edge_idx][1]) for f in range(len(frames)))
        x2_vals = ";".join(str(frames[f][0][edge_idx][2]) for f in range(len(frames)))
        y2_vals = ";".join(str(frames[f][0][edge_idx][3]) for f in range(len(frames)))
        svg_lines.append(
            f'<line x1="{frames[0][0][edge_idx][0]}" y1="{frames[0][0][edge_idx][1]}" x2="{frames[0][0][edge_idx][2]}" y2="{frames[0][0][edge_idx][3]}" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.8">'
        )
        svg_lines.append(
            f'<animate attributeName="x1" values="{x1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y1" values="{y1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="x2" values="{x2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y2" values="{y2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append('</line>')
    svg_lines.append('</g>')

    # Outer cube vertices (white dots)
    for vert_idx in range(8):
        cx_vals = ";".join(str(frames[f][1][vert_idx][0]) for f in range(len(frames)))
        cy_vals = ";".join(str(frames[f][1][vert_idx][1]) for f in range(len(frames)))
        k_vals = ";".join(
            str(0.3 + frames[f][1][vert_idx][3] * 0.5) for f in range(len(frames))
        )
        svg_lines.append(
            f'<circle cx="{frames[0][1][vert_idx][0]}" cy="{frames[0][1][vert_idx][1]}" r="3" fill="#ffffff" opacity="0.9">'
        )
        svg_lines.append(
            f'<animate attributeName="cx" values="{cx_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="cy" values="{cy_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="r" values="{k_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append('</circle>')

    # Inner cube (teal)
    svg_lines.append(f'<g opacity="0.7">')
    for edge_idx, (v1, v2) in enumerate(
        [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    ):
        x1_vals = ";".join(str(frames[f][2][edge_idx][0]) for f in range(len(frames)))
        y1_vals = ";".join(str(frames[f][2][edge_idx][1]) for f in range(len(frames)))
        x2_vals = ";".join(str(frames[f][2][edge_idx][2]) for f in range(len(frames)))
        y2_vals = ";".join(str(frames[f][2][edge_idx][3]) for f in range(len(frames)))
        svg_lines.append(
            f'<line x1="{frames[0][2][edge_idx][0]}" y1="{frames[0][2][edge_idx][1]}" x2="{frames[0][2][edge_idx][2]}" y2="{frames[0][2][edge_idx][3]}" stroke="#5eead4" stroke-width="2" stroke-linecap="round">'
        )
        svg_lines.append(
            f'<animate attributeName="x1" values="{x1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y1" values="{y1_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="x2" values="{x2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="y2" values="{y2_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append('</line>')
    svg_lines.append('</g>')

    # Inner cube vertices (teal dots)
    for vert_idx in range(8):
        cx_vals = ";".join(str(frames[f][3][vert_idx][0]) for f in range(len(frames)))
        cy_vals = ";".join(str(frames[f][3][vert_idx][1]) for f in range(len(frames)))
        k_vals = ";".join(
            str(0.3 + frames[f][3][vert_idx][3] * 0.5) for f in range(len(frames))
        )
        svg_lines.append(
            f'<circle cx="{frames[0][3][vert_idx][0]}" cy="{frames[0][3][vert_idx][1]}" r="2.5" fill="#5eead4" opacity="0.8">'
        )
        svg_lines.append(
            f'<animate attributeName="cx" values="{cx_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="cy" values="{cy_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append(
            f'<animate attributeName="r" values="{k_vals}" dur="16s" repeatCount="indefinite" />'
        )
        svg_lines.append('</circle>')

    svg_lines.append('</svg>')

    return "\n".join(svg_lines)


def generate_stack_orbit():
    """Generate stack-orbit.svg with orbiting items."""
    width, height = 900, 440
    center_x, center_y = 450, 222

    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Tech stack orbiting LLM core">',
        '<defs>',
        '<style>',
        '@keyframes pulse-core { 0%, 100% { r: 54; } 50% { r: 58; } }',
        '@keyframes expand-ring { 0% { r: 54; opacity: 0.6; } 50% { r: 75; opacity: 0.1; } 100% { r: 54; opacity: 0.6; } }',
        '.core { animation: pulse-core 3.2s infinite; }',
        '.core-ring { animation: expand-ring 3.2s infinite; }',
        '</style>',
        '<linearGradient id="bgGradOrbit" x1="0%" y1="0%" x2="100%" y2="100%">',
        '<stop offset="0%" style="stop-color:#0d0f24;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#15103a;stop-opacity:1" />',
        '</linearGradient>',
        '<radialGradient id="coreSphereGrad" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" style="stop-color:#a995ff;stop-opacity:1" />',
        '<stop offset="70%" style="stop-color:#7c5cff;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#5c4a99;stop-opacity:1" />',
        '</radialGradient>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="url(#bgGradOrbit)" rx="24" />'
    ]

    # Core sphere
    svg_lines.append(
        f'<circle cx="{center_x}" cy="{center_y}" r="54" fill="url(#coreSphereGrad)" class="core" />'
    )
    svg_lines.append(
        f'<circle cx="{center_x}" cy="{center_y}" r="54" fill="none" stroke="#7c5cff" stroke-width="2" opacity="0.5" class="core" />'
    )

    # Expanding ring
    svg_lines.append(
        f'<circle cx="{center_x}" cy="{center_y}" r="54" fill="none" stroke="#5eead4" stroke-width="1.5" class="core-ring" />'
    )

    # Core text
    svg_lines.append(
        f'<text x="{center_x}" y="{center_y + 8}" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="28" font-weight="700" fill="#070a18" text-anchor="middle">LLM</text>'
    )

    # Orbit 1: Ring1 (tilt 0.42, roll -0.12, 30s, violet)
    ring1_items = ["Python", "FastAPI", "LangGraph", "RAG", "PostgreSQL", "Docker"]
    ring1_r = 330
    ring1_tilt = 0.42
    ring1_roll = -0.12
    ring1_duration = 30

    svg_lines.append(f'<g id="orbit1">')
    for item_idx, item_text in enumerate(ring1_items):
        angle_start = (item_idx / len(ring1_items)) * 2 * math.pi

        # Generate 72 keyframes
        positions = []
        scales = []
        opacities = []

        for frame in range(72):
            t = frame / 72
            angle = angle_start + t * 2 * math.pi
            x_orb = ring1_r * math.cos(angle)
            z0_orb = ring1_r * math.sin(angle)
            y_orb = z0_orb * math.sin(ring1_tilt)
            z_orb = z0_orb * math.cos(ring1_tilt)

            # Roll rotation
            z_rot = z_orb * math.cos(ring1_roll) - x_orb * math.sin(ring1_roll)
            x_rot = z_orb * math.sin(ring1_roll) + x_orb * math.cos(ring1_roll)

            # Depth scaling
            d = (z_rot / ring1_r + 1) / 2
            scale = 0.62 + 0.5 * d
            opacity = 0.28 + 0.72 * d

            positions.append((x_rot, y_orb, z_rot))
            scales.append(scale)
            opacities.append(opacity)

        # Build keyframe strings
        tx_vals = ";".join(f"{pos[0]:.1f}" for pos in positions)
        ty_vals = ";".join(f"{pos[1]:.1f}" for pos in positions)
        scale_vals = ";".join(f"{s:.3f}" for s in scales)
        opacity_vals = ";".join(f"{o:.2f}" for o in opacities)

        # Pill size based on text length
        pill_width = len(item_text) * 8 + 20
        pill_height = 32

        svg_lines.append(f'<g>')
        svg_lines.append(
            f'<animateTransform attributeName="transform" type="translate" values="0,0;0,0" dur="{ring1_duration}s" repeatCount="indefinite" />'
        )

        # Outer group for translation
        svg_lines.append(f'<g>')
        svg_lines.append(
            f'<animate attributeName="transform" type="translate" values="{tx_vals}" dur="{ring1_duration}s" repeatCount="indefinite" attributeName="transform" />'
        )

        # Inner group for scale
        svg_lines.append(f'<g>')
        svg_lines.append(
            f'<animate attributeName="transform" type="scale" values="{scale_vals}" dur="{ring1_duration}s" repeatCount="indefinite" />'
        )

        # Pill
        svg_lines.append(
            f'<rect x="{-pill_width/2}" y="{-pill_height/2}" width="{pill_width}" height="{pill_height}" rx="16" fill="#7c5cff" opacity="0.9" />'
        )
        svg_lines.append(
            f'<text x="0" y="5" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="13" font-weight="600" fill="#e4e1ff" text-anchor="middle">{item_text}</text>'
        )

        # Opacity animation
        svg_lines.append(
            f'<animate attributeName="opacity" values="{opacity_vals}" dur="{ring1_duration}s" repeatCount="indefinite" />'
        )

        svg_lines.append('</g></g></g>')

    svg_lines.append('</g>')

    # Orbit 2: Ring2 (tilt 0.50, roll 0.18, 22s, teal, opposite direction)
    ring2_items = ["pgvector", "Redis", "AWS", "React"]
    ring2_r = 190
    ring2_tilt = 0.50
    ring2_roll = 0.18
    ring2_duration = 22

    svg_lines.append(f'<g id="orbit2">')
    for item_idx, item_text in enumerate(ring2_items):
        angle_start = (item_idx / len(ring2_items)) * 2 * math.pi

        # Generate 72 keyframes (opposite direction)
        positions = []
        scales = []
        opacities = []

        for frame in range(72):
            t = frame / 72
            angle = angle_start - t * 2 * math.pi  # Opposite direction
            x_orb = ring2_r * math.cos(angle)
            z0_orb = ring2_r * math.sin(angle)
            y_orb = z0_orb * math.sin(ring2_tilt)
            z_orb = z0_orb * math.cos(ring2_tilt)

            # Roll rotation
            z_rot = z_orb * math.cos(ring2_roll) - x_orb * math.sin(ring2_roll)
            x_rot = z_orb * math.sin(ring2_roll) + x_orb * math.cos(ring2_roll)

            # Depth scaling
            d = (z_rot / ring2_r + 1) / 2
            scale = 0.62 + 0.5 * d
            opacity = 0.28 + 0.72 * d

            positions.append((x_rot, y_orb, z_rot))
            scales.append(scale)
            opacities.append(opacity)

        # Build keyframe strings
        tx_vals = ";".join(f"{pos[0]:.1f}" for pos in positions)
        ty_vals = ";".join(f"{pos[1]:.1f}" for pos in positions)
        scale_vals = ";".join(f"{s:.3f}" for s in scales)
        opacity_vals = ";".join(f"{o:.2f}" for o in opacities)

        # Pill size
        pill_width = len(item_text) * 8 + 20
        pill_height = 32

        svg_lines.append(f'<g>')

        # Outer group for translation
        svg_lines.append(f'<g>')
        svg_lines.append(
            f'<animate attributeName="transform" type="translate" values="{tx_vals}" dur="{ring2_duration}s" repeatCount="indefinite" />'
        )

        # Inner group for scale
        svg_lines.append(f'<g>')
        svg_lines.append(
            f'<animate attributeName="transform" type="scale" values="{scale_vals}" dur="{ring2_duration}s" repeatCount="indefinite" />'
        )

        # Pill
        svg_lines.append(
            f'<rect x="{-pill_width/2}" y="{-pill_height/2}" width="{pill_width}" height="{pill_height}" rx="16" fill="#5eead4" opacity="0.9" />'
        )
        svg_lines.append(
            f'<text x="0" y="5" font-family="\'Segoe UI\',Helvetica,Arial,sans-serif" font-size="13" font-weight="600" fill="#070a18" text-anchor="middle">{item_text}</text>'
        )

        # Opacity animation
        svg_lines.append(
            f'<animate attributeName="opacity" values="{opacity_vals}" dur="{ring2_duration}s" repeatCount="indefinite" />'
        )

        svg_lines.append('</g></g></g>')

    svg_lines.append('</g>')

    svg_lines.append('</svg>')

    return "\n".join(svg_lines)


def generate_divider():
    """Generate divider.svg with animated glowing dot."""
    width, height = 1200, 28

    svg_lines = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" role="presentation">',
        '<defs>',
        '<style>',
        '@keyframes traverse { 0% { cx: -20; opacity: 0; } 5% { opacity: 1; } 95% { opacity: 1; } 100% { cx: 1220; opacity: 0; } }',
        '.glow-dot { animation: traverse 5s infinite; filter: drop-shadow(0 0 8px #5eead4); }',
        '</style>',
        '<linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '<stop offset="0%" style="stop-color:#7c5cff;stop-opacity:0" />',
        '<stop offset="50%" style="stop-color:#7c5cff;stop-opacity:1" />',
        '<stop offset="100%" style="stop-color:#5eead4;stop-opacity:0" />',
        '</linearGradient>',
        '</defs>',
        f'<line x1="0" y1="14" x2="{width}" y2="14" stroke="url(#lineGrad)" stroke-width="2" />',
        f'<circle cx="0" cy="14" r="5" fill="#5eead4" class="glow-dot" />',
        '</svg>',
    ]

    return "\n".join(svg_lines)


def main():
    """Generate all assets."""
    ensure_assets_dir()

    print("Generating hero-banner.svg...")
    hero_svg = generate_hero_banner()
    hero_path = "assets/hero-banner.svg"
    with open(hero_path, "w") as f:
        f.write(hero_svg)
    print(f"✓ {hero_path} ({len(hero_svg)} bytes)")

    print("Generating stack-orbit.svg...")
    stack_svg = generate_stack_orbit()
    stack_path = "assets/stack-orbit.svg"
    with open(stack_path, "w") as f:
        f.write(stack_svg)
    print(f"✓ {stack_path} ({len(stack_svg)} bytes)")

    print("Generating divider.svg...")
    divider_svg = generate_divider()
    divider_path = "assets/divider.svg"
    with open(divider_path, "w") as f:
        f.write(divider_svg)
    print(f"✓ {divider_path} ({len(divider_svg)} bytes)")

    print("\nAll assets generated successfully!")


if __name__ == "__main__":
    main()
