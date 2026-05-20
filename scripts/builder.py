import json
from pathlib import Path
from datetime import datetime

OUTPUT_FOLDER = Path(__file__).parent.parent / "output"
HOME_FOLDER = Path(__file__).parent.parent / "home"
REGISTRY_FILE = HOME_FOLDER / "registry.json"

PAGE_COLORS = [
    {"accent": "#dc2626", "glow": "#2a0a0a", "badge": "#b91c1c"},  # red
    {"accent": "#16a34a", "glow": "#0a2a0a", "badge": "#15803d"},  # green
    {"accent": "#d97706", "glow": "#1f1200", "badge": "#b45309"},  # amber
    {"accent": "#2563eb", "glow": "#0a0a2e", "badge": "#1d4ed8"},  # blue
    {"accent": "#7c3aed", "glow": "#1e0a3c", "badge": "#6d28d9"},  # purple
    {"accent": "#0d9488", "glow": "#0a2a28", "badge": "#0f766e"},  # teal
    {"accent": "#ea580c", "glow": "#1f0a00", "badge": "#c2410c"},  # orange
    {"accent": "#6d28d9", "glow": "#1a0f3d", "badge": "#5b21b6"},  # violet
    {"accent": "#0369a1", "glow": "#0a1f2e", "badge": "#075985"},  # sky
    {"accent": "#15803d", "glow": "#0a2010", "badge": "#166534"},  # emerald
    {"accent": "#b45309", "glow": "#1f1200", "badge": "#92400e"},  # yellow
    {"accent": "#be185d", "glow": "#2a0a1a", "badge": "#9d174d"},  # pink
]


def save_page(title: str, html_content: str, category: str = "General"):
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    slug = title.lower().replace(" ", "-").replace("/", "-")
    filename = f"{slug}.html"
    filepath = OUTPUT_FOLDER / filename

    filepath.write_text(html_content, encoding="utf-8")
    print(f"Saved: {filepath}")

    register_page(title, filename, category)
    rebuild_home()

    return filepath


def register_page(title: str, filename: str, category: str):
    HOME_FOLDER.mkdir(exist_ok=True)

    if REGISTRY_FILE.exists():
        registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    else:
        registry = []

    existing = [p for p in registry if p["filename"] == filename]
    if not existing:
        color_index = len(registry) % len(PAGE_COLORS)
        color = PAGE_COLORS[color_index]
        registry.append({
            "title": title,
            "filename": filename,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "accent": color["accent"],
            "glow": color["glow"],
            "badge": color["badge"],
        })
        REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        print(f"Registered: {title} under '{category}'")
    else:
        existing[0]["category"] = category
        existing[0]["title"] = title
        REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        print(f"Updated: {title}")


def delete_page(filename: str):
    if REGISTRY_FILE.exists():
        registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    else:
        print("No registry found.")
        return

    original_count = len(registry)
    registry = [p for p in registry if p["filename"] != filename]

    if len(registry) == original_count:
        print(f"No page found with filename: {filename}")
        return

    REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    filepath = OUTPUT_FOLDER / filename
    if filepath.exists():
        filepath.unlink()
        print(f"Deleted file: {filepath}")

    rebuild_home()
    print(f"Removed {filename} from registry and home page.")


def rebuild_home():
    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    CATEGORY_THEMES = {
        "Machine Learning":  {"accent": "#4f46e5", "glow": "#1e1b4b", "badge": "#4338ca"},
        "Work":              {"accent": "#0891b2", "glow": "#0c2233", "badge": "#0369a1"},
        "Personal":          {"accent": "#059669", "glow": "#0a2318", "badge": "#047857"},
        "Research":          {"accent": "#d97706", "glow": "#1f1200", "badge": "#b45309"},
        "General":           {"accent": "#6b7280", "glow": "#1a1a1a", "badge": "#4b5563"},
    }
    DEFAULT_THEME = {"accent": "#6b7280", "glow": "#1a1a1a", "badge": "#4b5563"}

    categories = {}
    for page in registry:
        cat = page.get("category", "General")
        categories.setdefault(cat, []).append(page)

    sections = ""
    for cat, pages in categories.items():
        theme = CATEGORY_THEMES.get(cat, DEFAULT_THEME)
        accent = theme["accent"]
        glow = theme["glow"]
        badge = theme["badge"]

        cards = ""
        for page in pages:
            p_accent = page.get("accent", accent)
            p_glow = page.get("glow", glow)
            p_badge = page.get("badge", badge)
            cards += f"""
            <div class="card" style="--accent: {p_accent}; --glow: {p_glow};">
                <a href="../output/{page['filename']}">
                    <span class="badge" style="background:{p_badge};">{cat}</span>
                    <h2>{page['title']}</h2>
                    <p class="date">{page['date']}</p>
                </a>
            </div>"""

        sections += f"""
        <div class="category-section">
            <h2 class="category-title" style="color:{accent}; border-color:{accent}22;">{cat}</h2>
            <div class="grid">{cards}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Notes — Home</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #0f0f0f;
            color: #f0f0f0;
            padding: 40px;
        }}
        header {{ margin-bottom: 40px; }}
        h1 {{
            font-size: 2rem;
            color: #ffffff;
            margin-bottom: 6px;
        }}
        .subtitle {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 20px;
        }}
        .search-bar {{
            width: 100%;
            max-width: 500px;
            padding: 10px 16px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #f0f0f0;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-bar:focus {{ border-color: #555; }}
        .category-section {{ margin-bottom: 48px; }}
        .category-title {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px solid;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 16px;
        }}
        .card {{
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 22px;
            transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
            position: relative;
            overflow: hidden;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent);
            opacity: 0;
            transition: opacity 0.25s;
        }}
        .card:hover {{
            border-color: var(--accent);
            transform: translateY(-3px);
            box-shadow: 0 8px 24px var(--glow);
        }}
        .card:hover::before {{ opacity: 1; }}
        .card.hidden {{ display: none; }}
        .card a {{ text-decoration: none; color: inherit; }}
        .badge {{
            display: inline-block;
            font-size: 0.68rem;
            padding: 2px 8px;
            border-radius: 20px;
            color: white;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .card h2 {{
            font-size: 0.95rem;
            margin-bottom: 8px;
            color: #ffffff;
            line-height: 1.4;
        }}
        .date {{ font-size: 0.75rem; color: #555; }}
        .category-section.hidden {{ display: none; }}
    </style>
</head>
<body>
    <header>
        <h1>Meeting Notes</h1>
        <p class="subtitle">{len(registry)} note{"s" if len(registry) != 1 else ""} summarized</p>
        <input class="search-bar" type="text" placeholder="Search notes..." oninput="search(this.value)" />
    </header>
    {sections}
    <script>
        function search(query) {{
            const q = query.toLowerCase();
            document.querySelectorAll('.category-section').forEach(section => {{
                let anyVisible = false;
                section.querySelectorAll('.card').forEach(card => {{
                    const title = card.querySelector('h2').textContent.toLowerCase();
                    if (title.includes(q)) {{
                        card.classList.remove('hidden');
                        anyVisible = true;
                    }} else {{
                        card.classList.add('hidden');
                    }}
                }});
                section.classList.toggle('hidden', !anyVisible);
            }});
        }}
    </script>
</body>
</html>"""

    index_path = HOME_FOLDER / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Home page updated: {index_path}")

if __name__ == "__main__":
    print("What would you like to do?")
    print("1. Add / Update a page")
    print("2. Delete a page")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        title = input("Enter the page title: ").strip()
        category = input("Enter the category (e.g. Machine Learning, Work, Personal): ").strip()
        print("Paste the HTML content below. When done, type END on its own line and press Enter:")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        html_content = "\n".join(lines)
        save_page(title, html_content, category)

    elif choice == "2":
        if REGISTRY_FILE.exists():
            registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            print("\nCurrent pages:")
            for i, page in enumerate(registry):
                print(f"  {i + 1}. {page['title']} ({page['filename']})")
            filename = input("\nEnter the filename to delete (e.g. my-notes.html): ").strip()
            delete_page(filename)
        else:
            print("No registry found.")