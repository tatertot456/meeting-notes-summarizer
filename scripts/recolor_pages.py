import json
import re
from pathlib import Path

HOME_FOLDER = Path(__file__).parent.parent / "home"
OUTPUT_FOLDER = Path(__file__).parent.parent / "output"
REGISTRY_FILE = HOME_FOLDER / "registry.json"


def recolor_page(filepath: Path, accent: str, glow: str, badge: str):
    if not filepath.exists():
        print(f"Skipping missing file: {filepath.name}")
        return

    html = filepath.read_text(encoding="utf-8")

    # Extract the style block
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if not style_match:
        print(f"No style block found in {filepath.name}")
        return

    style = style_match.group(1)

    # Find all unique hex colors in the style block
    hex_colors = list(dict.fromkeys(re.findall(r'#[0-9a-fA-F]{6}', style)))

    # Known neutrals we never want to replace
    neutrals = {
        "#0f0f0f", "#1a1a1a", "#111111", "#111", "#222222", "#222",
        "#2a2a2a", "#1e1e1e", "#333333", "#555555", "#666666",
        "#888888", "#ffffff", "#f0f0f0", "#e0e0e0", "#cccccc",
        "#aaaaaa", "#000000", "#1a1a2e", "#0f0f0f".upper()
    }

    # Categorize non-neutral colors
    non_neutral = [c for c in hex_colors if c.lower() not in neutrals]

    if len(non_neutral) < 2:
        print(f"Could not identify enough colors in {filepath.name}")
        return

    # The colors appear in a predictable pattern in our pages:
    # First non-neutral = tag/badge background
    # Second non-neutral = nav hover / accent color  
    # Darkest non-neutral = glow/background tint
    # We'll map them by brightness

    def brightness(hex_color):
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299*r + 0.587*g + 0.114*b

    sorted_by_brightness = sorted(non_neutral, key=brightness)

    # Darkest = glow, brightest = accent, middle = badge
    old_glow = sorted_by_brightness[0]
    old_accent = sorted_by_brightness[-1]
    old_badge = sorted_by_brightness[len(sorted_by_brightness)//2]

    # Replace all instances throughout the entire file
    html = re.sub(re.escape(old_accent), accent, html, flags=re.IGNORECASE)
    html = re.sub(re.escape(old_glow), glow, html, flags=re.IGNORECASE)
    html = re.sub(re.escape(old_badge), badge, html, flags=re.IGNORECASE)

    # Fix header gradient
    html = re.sub(
        r'background: linear-gradient\(135deg,[^)]+\)',
        f'background: linear-gradient(135deg, {glow}, #1a1a2e)',
        html,
        count=1
    )

    filepath.write_text(html, encoding="utf-8")
    print(f"Recolored: {filepath.name} | accent={accent} glow={glow} badge={badge}")


def main():
    if not REGISTRY_FILE.exists():
        print("No registry found.")
        return

    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    for page in registry:
        if "accent" not in page:
            print(f"No color stored for {page['title']} — skipping")
            continue

        filepath = OUTPUT_FOLDER / page["filename"]
        recolor_page(filepath, page["accent"], page["glow"], page["badge"])

    print("\nDone! Rebuilding home page...")

    from builder import rebuild_home
    rebuild_home()


if __name__ == "__main__":
    main()