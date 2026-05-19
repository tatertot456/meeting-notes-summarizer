import time
import sys
from pathlib import Path
from reader import read_file

WATCHED_FOLDER = Path(__file__).parent.parent / "input"
SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".pptx"}


def watch():
    print(f"Watching: {WATCHED_FOLDER}")
    print("Drop a file into the input/ folder to begin...\n")

    seen = set()

    while True:
        current_files = set(WATCHED_FOLDER.iterdir())
        new_files = current_files - seen

        for filepath in new_files:
            if filepath.suffix.lower() in SUPPORTED:
                print(f"\n New file detected: {filepath.name}")
                print("=" * 60)
                try:
                    text = read_file(str(filepath))
                    print(text)
                    print("=" * 60)
                    print("Copy the text above and paste it into Claude.")
                except Exception as e:
                    print(f"Error reading file: {e}")

        seen = current_files
        time.sleep(2)


if __name__ == "__main__":
    watch()