#!/usr/bin/env python3
# Copyright © 2026–present Lubos Kocman and openSUSE contributors
# SPDX-License-Identifier: Apache-2.0
#
# Generates the yearly OpenAlt badge: a 1-bit (two colour) pixel-art take on the
# OpenAlt conference logo (https://www.openalt.cz/), with the year
# in a small tag in the top-right corner.
#
# The ring's three segments are drawn as solid / checkerboard / sparse dither
# instead of the three reds of the original logo, so the badge only ever uses
# two colours. Swap them every year by adding an entry to PALETTES (or pass
# --fg/--bg-top/--bg), e.g. 2027 could be bagel-beige on maple-maroon.
#
# Usage: scripts/openalt-badge.py [--year 2026] [--fg '#fff'] [--bg-top '#333'] [--bg '#000']
#        [--tag "'26"] writes openalt<year>.png to the repository root; then run
#        ./generate-previews.sh
#
# Requires Pillow and the Pixel Operator font (see README.md).

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

# year -> (foreground, background top, background bottom); the background is
# a stepped (banded) vertical gradient between the two
PALETTES = {
    2026: ("#ffffff", "#4a4a4a", "#0a0a0a"),  # white on black, like the OpenAlt t-shirt
}
BANDS = 8

GRID = 128   # logical pixels per side
SCALE = 8    # 128 * 8 = 1024 px output

# Ring geometry, taken from the original SVG logo. Angles are in degrees,
# clockwise from 12 o'clock.
CX, CY = 64, 59
R_OUT, R_IN = 31, 15
SEGMENTS = [          # (start, end, fill pattern)
    (-27, 28, "solid"),    # dark maroon in the original
    (28, 132, "checker"),  # red
    (132, 288, "sparse"),  # salmon
]


def find_font(name):
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", name],
                             capture_output=True, text=True, check=True).stdout
        if out and "PixelOperator" in out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    raise SystemExit(f"Font '{name}' not found; install Pixel Operator or pass --font")


def pattern_on(kind, x, y):
    if kind == "solid":
        return True
    if kind == "checker":
        return (x + y) % 2 == 0
    if kind == "sparse":
        return x % 2 == 0 and (y + x // 2) % 2 == 0
    return False


def ring_segment(x, y):
    """Return (segment index, is edge) for a logical pixel, or None outside."""
    dx, dy = x + 0.5 - CX, y + 0.5 - CY
    d = math.hypot(dx, dy)
    if not R_IN <= d <= R_OUT:
        return None
    ang = math.degrees(math.atan2(dx, -dy))
    for i, (a0, a1, _) in enumerate(SEGMENTS):
        a = ang
        while a < a0:
            a += 360
        if a < a1:
            return i
    return None


def draw_ring(px, fg):
    seg = {}
    for y in range(GRID):
        for x in range(GRID):
            s = ring_segment(x, y)
            if s is not None:
                seg[(x, y)] = s
    for (x, y), s in seg.items():
        # outline: any 4-neighbour outside the ring or in another segment
        edge = any(seg.get((x + ox, y + oy)) != s
                   for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge or pattern_on(SEGMENTS[s][2], x, y):
            px[x, y] = fg


def draw_text(img, text, font, cy, scale, color, right=None, left=None):
    """Draw crisp (non-antialiased) text at row cy, centred horizontally
    or right-aligned to column `right`."""
    l, t, r, b = font.getbbox(text)
    w, h = r - l, b - t
    tmp = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(tmp)
    d.fontmode = "1"
    d.text((-l, -t), text, font=font, fill=1)
    tmp = tmp.resize((w * scale, h * scale), Image.NEAREST)
    if left is not None:
        x = left
    elif right is not None:
        x = right - tmp.width + 1
    else:
        x = (GRID - tmp.width) // 2
    y = cy - tmp.height // 2
    img.paste(color, (x, y), tmp)
    return x, y, tmp.width, tmp.height


def sparkle(px, x, y, fg, big=False):
    pts = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if big:
        pts += [(2, 0), (-2, 0), (0, 2), (0, -2)]
    for ox, oy in pts:
        px[x + ox, y + oy] = fg


def frame(d, fg):
    # thick outer frame + thin inner line, notched (8-bit style) corners
    for inset, n in ((1, 5), (2, 5), (3, 5), (6, 3)):
        a, b = inset, GRID - 1 - inset
        d.line([(a + n, a), (b - n, a)], fill=fg)
        d.line([(a + n, b), (b - n, b)], fill=fg)
        d.line([(a, a + n), (a, b - n)], fill=fg)
        d.line([(b, a + n), (b, b - n)], fill=fg)
        # stair-step corners
        for (sx, sy, ox, oy) in ((a, a, 1, 1), (b, a, -1, 1),
                                 (a, b, 1, -1), (b, b, -1, -1)):
            for i in range(n):
                d.point((sx + ox * (n - i), sy + oy * i), fill=fg)
                d.point((sx + ox * (n - i - 1), sy + oy * i), fill=fg)


def brno_logo(img, font, x, cy, color):
    """Pixel version of the City of Brno logo: B|R|N|O| with bars that get
    thicker left to right. Returns the right edge."""
    d = ImageDraw.Draw(img)
    for letter, bar in zip("BRNO", (1, 1, 3, 4)):
        lx, ly, lw, lh = draw_text(img, letter, font, cy, 1, color, left=x)
        x = lx + lw + 2
        d.rectangle([x, ly - 1, x + bar - 1, ly + lh], fill=color)
        x += bar + 2
    return x - 2


def gradient(img, top, bottom, style="radial"):
    """Stepped background gradient: 'vertical' (top -> bottom) or 'radial'
    (a glow centred on the ring, `top` in the middle fading to `bottom`)."""
    px = img.load()
    far = math.hypot(max(CX, GRID - CX), max(CY, GRID - CY))
    for y in range(GRID):
        for x in range(GRID):
            if style == "vertical":
                t = y / GRID
            else:
                t = math.hypot(x + 0.5 - CX, y + 0.5 - CY) / far
            i = min(int(t * BANDS), BANDS - 1)
            f = i / (BANDS - 1)
            px[x, y] = tuple(round(a + (b - a) * f) for a, b in zip(top, bottom))


def build(year, fg, bg_top, bg, font_path, tag, style="radial"):
    img = Image.new("RGB", (GRID, GRID), bg)
    gradient(img, bg_top, bg, style)
    px = img.load()
    d = ImageDraw.Draw(img)

    frame(d, fg)
    draw_ring(px, fg)

    font = ImageFont.truetype(font_path, 16)

    # decorations around the ring
    sparkle(px, 20, 30, fg, big=True)
    sparkle(px, 108, 44, fg, big=True)
    sparkle(px, 24, 72, fg)
    sparkle(px, 104, 78, fg)
    sparkle(px, 14, 52, fg)

    # small year tag in the top-right corner: inverted box with notched corners
    x, y, w, h = draw_text(img, tag, font, 17, 1, fg, right=114)
    d.rectangle([x - 3, y - 3, x + w + 2, y + h + 2], fill=fg)
    for cx, cy in ((x - 3, y - 3), (x + w + 2, y - 3),
                   (x - 3, y + h + 2), (x + w + 2, y + h + 2)):
        px[cx, cy] = bg
    draw_text(img, tag, font, 17, 1, bg, right=114)

    # where: OpenAlt also runs in České Budějovice, so name the city
    brno_logo(img, font, 13, 17, fg)

    # label below the logo, as in the original
    draw_text(img, "OpenAlt", font, 106, 2, fg)

    return img.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year", type=int, default=2026)
    p.add_argument("--fg", help="foreground colour (default: PALETTES[year])")
    p.add_argument("--bg-top", help="background gradient top (default: PALETTES[year])")
    p.add_argument("--bg", help="background gradient bottom (default: PALETTES[year])")
    p.add_argument("--font", help="path to Pixel Operator Bold .ttf")
    p.add_argument("--gradient", choices=("radial", "vertical"), default="radial")
    p.add_argument("--tag", help="corner tag text (default: the year)")
    p.add_argument("-o", "--output", type=Path)
    args = p.parse_args()

    fg, bg_top, bg = PALETTES.get(args.year, PALETTES[max(PALETTES)])
    fg, bg_top, bg = args.fg or fg, args.bg_top or bg_top, args.bg or bg
    font = args.font or find_font("Pixel Operator:style=Bold")
    out = args.output or ROOT / f"openalt{args.year}.png"
    fg, bg_top, bg = (ImageColor.getrgb(c) for c in (fg, bg_top, bg))
    build(args.year, fg, bg_top, bg, font, args.tag or str(args.year), args.gradient).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
