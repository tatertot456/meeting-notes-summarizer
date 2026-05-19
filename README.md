# Meeting Notes Summarizer

A local tool that reads meeting notes and lecture slides in multiple formats, sends the content to Claude AI for summarization, and generates interactive HTML pages organized in a central home page directory.

## How It Works

1. Drop a notes file into the `input/` folder
2. Run `watcher.py` — it detects the file, extracts the text, and copies a ready-to-paste prompt to your clipboard
3. Paste into Claude and specify a category (e.g. Machine Learning, Work, Personal)
4. Claude generates an interactive HTML summary page
5. Run `builder.py`, choose option 1, paste the HTML, type `END`
6. Open `home/index.html` in your browser — your new page appears automatically

## Supported File Types

- `.txt` — Plain text
- `.md` — Markdown
- `.pdf` — PDF documents
- `.docx` — Word documents
- `.pptx` — PowerPoint presentations

## Project Structure

meeting-notes-summarizer/
├── input/          # Drop your notes files here (gitignored)
├── output/         # Generated HTML summary pages
├── home/           # index.html home page directory
├── scripts/
│   ├── reader.py   # Extracts text from all supported file types
│   ├── watcher.py  # Monitors input/ and copies text to clipboard
│   └── builder.py  # Saves HTML pages and updates home page
├── requirements.txt
└── README.md

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/tatertot456/meeting-notes-summarizer.git
cd meeting-notes-summarizer
```

**2. Install dependencies:**
```bash
python -m pip install -r requirements.txt
```

**3. Start the watcher** (from the `scripts/` folder):
```bash
cd scripts
python watcher.py
```

**4. Build or manage pages** (from the `scripts/` folder):
```bash
python builder.py
```

## Home Page Features

- **Categorized sections** — pages grouped by category (Machine Learning, Work, Personal, etc.)
- **Search bar** — filters cards by title in real time
- **Hover effects** — each category has a unique accent color and glow
- **Auto-updating** — adding or deleting a page instantly updates the home page

## Managing Pages

**Add a page:** Run `builder.py` → option 1 → enter title and category → paste HTML → type `END`

**Delete a page:** Run `builder.py` → option 2 → enter the filename → confirms deletion from disk and home page

## Notes

- The `input/` folder is gitignored — your raw notes never get pushed to GitHub
- After the watcher processes a file, delete it from `input/` before dropping the next one
- Claude.ai Pro plan covers all AI summarization — no Anthropic API costs