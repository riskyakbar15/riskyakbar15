"""
Compose portrait-ascii.svg + info-card.svg into a single hero.svg so the README
hero is ONE image that can never wrap ("turun") and stays perfectly aligned.

Each source SVG is embedded as a nested <svg> (preserves its SMIL animations).
The info card is scaled so both panels share the same height, sitting side by
side with a small gap.

Regenerate after updating either source panel:
  python scripts/prep_photo.py <photo> && python scripts/make_ascii_svg.py
  python scripts/make_info_card.py
  python scripts/make_hero.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PORTRAIT = os.path.join(ROOT, "portrait-ascii.svg")
INFOCARD = os.path.join(ROOT, "info-card.svg")
OUT = os.path.join(ROOT, "hero.svg")

GAP = 22  # horizontal space between the two panels (in portrait-height units)


def load_svg(path):
    """Return (inner_markup, width, height, font_family) for an SVG file."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<svg\b[^>]*>", text)
    if not m:
        raise ValueError(f"no <svg> root found in {path}")
    open_tag = m.group(0)
    inner = text[m.end():]
    inner = inner[: inner.rindex("</svg>")]

    def attr(name):
        a = re.search(name + r'="([^"]*)"', open_tag)
        return a.group(1) if a else None

    w = float(attr("width"))
    h = float(attr("height"))
    return inner, w, h, attr("font-family")


def main():
    p_inner, p_w, p_h, p_font = load_svg(PORTRAIT)
    i_inner, i_w, i_h, i_font = load_svg(INFOCARD)

    # scale the info card so its height matches the portrait height
    i_scaled_w = round(i_w * (p_h / i_h))
    total_w = round(p_w + GAP + i_scaled_w)
    total_h = round(p_h)

    p_extra = f' font-family="{p_font}"' if p_font else ""
    i_extra = f' font-family="{i_font}"' if i_font else ""

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" '
        f'height="{total_h}" viewBox="0 0 {total_w} {total_h}">',
        f'<svg x="0" y="0" width="{p_w:g}" height="{p_h:g}" '
        f'viewBox="0 0 {p_w:g} {p_h:g}"{p_extra}>{p_inner}</svg>',
        f'<svg x="{p_w + GAP:g}" y="0" width="{i_scaled_w}" height="{total_h}" '
        f'viewBox="0 0 {i_w:g} {i_h:g}" preserveAspectRatio="xMinYMin meet"'
        f'{i_extra}>{i_inner}</svg>',
        "</svg>",
    ]
    open(OUT, "w", encoding="utf-8").write("".join(parts))
    print(f"wrote {OUT} ({total_w}x{total_h})")


if __name__ == "__main__":
    main()
