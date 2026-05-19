import json
from pathlib import Path
from datetime import datetime

OUTPUT_FOLDER = Path(__file__).parent.parent / "output"
HOME_FOLDER = Path(__file__).parent.parent / "home"
REGISTRY_FILE = HOME_FOLDER / "registry.json"


def save_page(title: str, html_content: str) -> Path:
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    slug = title.lower().replace(" ", "-").replace("/", "-")
    filename = f"{slug}.html"
    filepath = OUTPUT_FOLDER / filename

    filepath.write_text(html_content, encoding="utf-8")
    print(f"Saved: {filepath}")

    register_page(title, filename)
    rebuild_home()

    return filepath


def register_page(title: str, filename: str):
    HOME_FOLDER.mkdir(exist_ok=True)

    if REGISTRY_FILE.exists():
        registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    else:
        registry = []

    existing = [p for p in registry if p["filename"] == filename]
    if not existing:
        registry.append({
            "title": title,
            "filename": filename,
            "date": datetime.now().strftime("%Y-%m-%d %I:%M %p")
        })
        REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        print(f"Registered: {title}")


def rebuild_home():
    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    cards = ""
    for page in registry:
        cards += f"""
        <div class="card">
            <a href="../output/{page['filename']}">
                <h2>{page['title']}</h2>
                <p class="date">{page['date']}</p>
            </a>
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
        h1 {{
            font-size: 2rem;
            margin-bottom: 8px;
            color: #ffffff;
        }}
        .subtitle {{
            color: #888;
            margin-bottom: 40px;
            font-size: 0.95rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 24px;
            transition: border-color 0.2s, transform 0.2s;
        }}
        .card:hover {{
            border-color: #555;
            transform: translateY(-2px);
        }}
        .card a {{
            text-decoration: none;
            color: inherit;
        }}
        .card h2 {{
            font-size: 1.1rem;
            margin-bottom: 8px;
            color: #ffffff;
        }}
        .date {{
            font-size: 0.8rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>Meeting Notes</h1>
    <p class="subtitle">{len(registry)} note{"s" if len(registry) != 1 else ""} summarized</p>
    <div class="grid">
        {cards}
    </div>
</body>
</html>"""

    index_path = HOME_FOLDER / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Home page updated: {index_path}")


if __name__ == "__main__":
    title = input("Enter the page title: ")
    print("Paste the HTML content below. When done, type END on its own line and press Enter:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    html_content = "\n".join(lines)
    save_page(title, html_content)