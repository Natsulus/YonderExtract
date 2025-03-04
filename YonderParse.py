import re
import argparse
import os
import xml.etree.ElementTree as ET
import glob
import uuid
import configparser
from ebooklib import epub

# Argument parser
parser = argparse.ArgumentParser(description="Parse XML chapters from Yonder app into an EPUB.")
parser.add_argument("folder", help="Folder containing XML chapter files")
args = parser.parse_args()

# Load config if it exists
config = configparser.ConfigParser()
config_path = os.path.join(args.folder, "config.ini")
if os.path.exists(config_path):
    config.read(config_path, encoding="utf-8")
else:
    config['SETTINGS'] = {}

# Chapter class
class Chapter:
    def __init__(self, title, chapter_num, act_num=0):
        self.title = title
        self.chapter_num = int(chapter_num)
        self.act_num = int(act_num) if act_num is not None else 0
        self.text = []

    def add_text(self, text):
        self.text.append(text)

    def to_html(self):
        html = f"<h1>{self.title}</h1>"
        for text in self.text:
            html += f"<p>{text}</p>"
        return html.encode('utf-8')

    def __lt__(self, other):
        return (self.act_num, self.chapter_num) < (other.act_num, other.chapter_num)

# Define default chapter patterns with hyphen, en dash, and plain number
default_patterns = [
    re.compile(r"Chapter (\d+): (.+)"),    # e.g., "Chapter 1: Prologue"
    re.compile(r"Chapter (\d+) [-–] (.+)"),  # e.g., "Chapter 1 - Prologue" or "Chapter 1 – Prologue"
    re.compile(r"Chapter (\d+)"),           # e.g., "Chapter 1"
]

# Special pattern for "Prologue" in chapter1.xml
prologue_pattern = re.compile(r"Prologue")

# Get settings with defaults
pattern_type = config['SETTINGS'].get('PatternType', 'Standard')
custom_pattern = config['SETTINGS'].get('ChapterPattern', '').strip()
chapter_patterns = [re.compile(custom_pattern)] if custom_pattern else default_patterns

def parse_chapters(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    chapters = []
    current_chapter = None
    is_chapter1 = os.path.basename(file_path).lower().startswith("chapter1")

    for node in root.iter("node"):
        node_class = node.get("class", "")
        text = node.get("text", "").strip()
        if not text:
            continue

        if node_class in ["android.widget.TextView", "android.view.View"]:
            match = None
            for pattern in chapter_patterns:
                match = pattern.match(text)
                if match:
                    break

            if not match and is_chapter1 and prologue_pattern.match(text):
                new_chapter = Chapter(text, 0)  # Prologue as chapter 0
                chapters.append(new_chapter)
                current_chapter = new_chapter
            elif match:
                if pattern_type == "VolumeAfter":
                    new_chapter = Chapter(text, match.group(1), match.group(2))
                elif pattern_type == "Volume":
                    new_chapter = Chapter(text, match.group(2), match.group(1))
                else:
                    chapter_num = match.group(1)
                    chapter_title = text
                    new_chapter = Chapter(chapter_title, chapter_num)
                chapters.append(new_chapter)
                current_chapter = new_chapter
            elif node_class == "android.widget.TextView" and current_chapter is not None:
                current_chapter.add_text(text)

    if not chapters:
        print(f"Warning: No chapter titles found in {file_path}")
    return chapters

def build_epub(folder):
    xml_files = glob.glob(os.path.join(folder, "*.xml"))
    if not xml_files:
        print(f"No XML files found in {folder}")
        return

    all_chapters = []
    for xml_file in xml_files:
        chapters = parse_chapters(xml_file)
        all_chapters.extend(chapters)
    
    all_chapters.sort()

    book = epub.EpubBook()
    default_title = os.path.basename(folder)
    title = config['SETTINGS'].get('Title', default_title).strip() or default_title
    book.set_identifier(f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_DNS, title)}")
    book.set_title(title)
    book.set_language("en")
    
    author = config['SETTINGS'].get('Author', 'Unknown')
    book.add_author(author)
    if 'Description' in config['SETTINGS']:
        book.add_metadata('DC', 'description', config['SETTINGS']['Description'])
    book.add_metadata('DC', 'publisher', config['SETTINGS'].get('Publisher', 'YONDER'))

    # Check for cover.png first, then cover.jpg
    cover_image = config['SETTINGS'].get('CoverImage', '').strip()
    if not cover_image:  # If not specified, try default covers
        cover_path_png = os.path.join(folder, "cover.png")
        cover_path_jpg = os.path.join(folder, "cover.jpg")
        cover_path = cover_path_png if os.path.exists(cover_path_png) else cover_path_jpg
    else:
        cover_path = os.path.join(folder, cover_image)
    
    if os.path.exists(cover_path):
        with open(cover_path, 'rb') as f:
            book.set_cover(os.path.basename(cover_path), f.read())

    epub_chapters = []
    for idx, chapter in enumerate(all_chapters):
        c = epub.EpubHtml(
            title=chapter.title,
            file_name=f"chapter_{idx}.xhtml",
            lang="en"
        )
        c.content = chapter.to_html()
        book.add_item(c)
        epub_chapters.append(c)

    book.toc = epub_chapters
    book.spine = (["cover"] if os.path.exists(cover_path) else []) + ["nav"] + epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    output_file = os.path.join(folder, f"{title}.epub")
    epub.write_epub(output_file, book)
    print(f"EPUB generated: {output_file}")

if __name__ == "__main__":
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
    else:
        build_epub(args.folder)