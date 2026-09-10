import json
import re
from pathlib import Path

HOME_FOLDER = Path(__file__).parent.parent / "home"
OUTPUT_FOLDER = Path(__file__).parent.parent / "output"
REGISTRY_FILE = HOME_FOLDER / "registry.json"

# Backfill derived colors for pages registered before the new fields existed
BACKFILL = {
    "#dc2626": {"code_bg": "#1a0a0a", "highlight_bg": "#2a0f0f", "bold": "#f87171"},
    "#16a34a": {"code_bg": "#0a1a0f", "highlight_bg": "#0f2a1a", "bold": "#4ade80"},
    "#d97706": {"code_bg": "#1a1200", "highlight_bg": "#2a1c00", "bold": "#fbbf24"},
    "#2563eb": {"code_bg": "#0a0f1a", "highlight_bg": "#0f1a2e", "bold": "#60a5fa"},
    "#7c3aed": {"code_bg": "#130a1a", "highlight_bg": "#1e0f2e", "bold": "#a78bfa"},
    "#0d9488": {"code_bg": "#0a1a18", "highlight_bg": "#0f2a28", "bold": "#2dd4bf"},
    "#ea580c": {"code_bg": "#1a0f0a", "highlight_bg": "#2a180a", "bold": "#fb923c"},
    "#6d28d9": {"code_bg": "#100a1a", "highlight_bg": "#1a0f2e", "bold": "#a78bfa"},
    "#0369a1": {"code_bg": "#0a141a", "highlight_bg": "#0f1f2e", "bold": "#38bdf8"},
    "#15803d": {"code_bg": "#0a1a0f", "highlight_bg": "#0f2a18", "bold": "#34d399"},
    "#b45309": {"code_bg": "#1a1200", "highlight_bg": "#2a1c00", "bold": "#fcd34d"},
    "#be185d": {"code_bg": "#1a0a12", "highlight_bg": "#2a0f1c", "bold": "#f472b6"},
}


def recolor_page(filepath: Path, accent: str, glow: str, badge: str,
                 code_bg: str, highlight_bg: str, bold: str):
    if not filepath.exists():
        print(f"Skipping missing file: {filepath.name}")
        return

    html = filepath.read_text(encoding="utf-8")

    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if not style_match:
        print(f"No style block found in {filepath.name}")
        return

    style = style_match.group(1)
    hex_colors = list(dict.fromkeys(re.findall(r'#[0-9a-fA-F]{6}', style)))

    neutrals = {
        "#0f0f0f", "#1a1a1a", "#111111", "#222222", "#2a2a2a",
        "#1e1e1e", "#333333", "#555555", "#666666", "#888888",
        "#ffffff", "#f0f0f0", "#e0e0e0", "#d4d4d4", "#c8c8c8",
        "#cccccc", "#aaaaaa", "#000000", "#1a1a2e", "#e2e8f0",
    }

    non_neutral = [c for c in hex_colors if c.lower() not in neutrals]

    if len(non_neutral) < 2:
        print(f"Could not identify enough colors in {filepath.name}")
        return

    def brightness(hex_color):
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299*r + 0.587*g + 0.114*b

    sorted_by_brightness = sorted(non_neutral, key=brightness)
    old_glow   = sorted_by_brightness[0]
    old_accent = sorted_by_brightness[-1]
    old_badge  = sorted_by_brightness[len(sorted_by_brightness)//2]

    # Replace accent/glow/badge throughout
    html = re.sub(re.escape(old_accent), accent, html, flags=re.IGNORECASE)
    html = re.sub(re.escape(old_glow),   glow,   html, flags=re.IGNORECASE)
    html = re.sub(re.escape(old_badge),  badge,  html, flags=re.IGNORECASE)

    # Fix header gradient
    html = re.sub(
        r'background: linear-gradient\(135deg,[^)]+\)',
        f'background: linear-gradient(135deg, {glow}, #1a1a2e)',
        html, count=1
    )

    # Body text off-white
    html = re.sub(
        r'(body\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
        r'\g<1>#c8c8c8', html, flags=re.DOTALL
    )

    # p, li, td off-white
    for selector in [r'\bp\b', r'\bli\b', r'\btd\b']:
        html = re.sub(
            rf'({selector}\s*\{{[^}}]*?color:\s*)#[0-9a-fA-F]{{6}}',
            r'\g<1>#c8c8c8', html, flags=re.DOTALL
        )

    # card p off-white
    html = re.sub(
        r'(\.card\s+p\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
        r'\g<1>#c8c8c8', html, flags=re.DOTALL
    )

    # Highlight box: dark tinted background, off-white text
    html = re.sub(
        r'(\.highlight\s*\{[^}]*?background:\s*)#[0-9a-fA-F]{6}',
        rf'\g<1>{highlight_bg}', html, flags=re.DOTALL
    )
    html = re.sub(
        r'(\.highlight\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
        r'\g<1>#c8c8c8', html, flags=re.DOTALL
    )
    html = re.sub(
        r'(\.highlight\s+p\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
        r'\g<1>#c8c8c8', html, flags=re.DOTALL
    )

    # Code block: tinted background, off-white text
    html = re.sub(
        r'(pre\s*\{[^}]*?background:\s*)(?:#[0-9a-fA-F]{3,6}|[a-z]+)',
        rf'\g<1>{code_bg}', html, flags=re.DOTALL
    )
    html = re.sub(
        r'(pre\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
        r'\g<1>#c8c8c8', html, flags=re.DOTALL
    )

    # Bold text: lighter accent color
    if 'strong {' not in html and 'strong{' not in html:
        html = html.replace(
            'li {',
            f'strong {{ color: {bold}; }}\n        li {{'
        )
    else:
        html = re.sub(
            r'(\bstrong\s*\{[^}]*?color:\s*)#[0-9a-fA-F]{6}',
            rf'\g<1>{bold}', html, flags=re.DOTALL
        )

    filepath.write_text(html, encoding="utf-8")
    print(f"Recolored: {filepath.name} | accent={accent} highlight_bg={highlight_bg} code_bg={code_bg} bold={bold}")


def main():
    if not REGISTRY_FILE.exists():
        print("No registry found.")
        return

    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    # Backfill new fields into registry for existing pages
    changed = False
    for page in registry:
        if "code_bg" not in page and page.get("accent") in BACKFILL:
            page.update(BACKFILL[page["accent"]])
            changed = True
    if changed:
        REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        print("Backfilled new color fields into registry.json")

    for page in registry:
        if "accent" not in page:
            print(f"No color stored for {page['title']} — skipping")
            continue

        filepath = OUTPUT_FOLDER / page["filename"]
        recolor_page(
            filepath,
            page["accent"],
            page["glow"],
            page["badge"],
            page.get("code_bg", "#111111"),
            page.get("highlight_bg", "#1a1a1a"),
            page.get("bold", page["accent"]),
        )

    print("\nDone! Rebuilding home page...")
    from builder import rebuild_home
    rebuild_home()


if __name__ == "__main__":
    main()