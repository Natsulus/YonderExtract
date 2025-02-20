import re
import argparse
import configparser
import xml.etree.ElementTree as ET
import glob
import uuid
import ebooklib.epub as epub

parser = argparse.ArgumentParser(prog="YonderParse", description="Parse XML Chapters extracted from Yonder and build EPUB files.")
parser.add_argument("title")

args = parser.parse_args()

config = configparser.ConfigParser()


chapter_list = []
pattern = None
pattern_type = None


# example on how to sort by volume then chapter:
# lambda x: x.volume, x.number

class Chapter:
	def __init__(self, title, number, volume=None):
		self.title = title
		self.number = int(number)
		if volume:
			self.volume = int(volume)
		else:
			self.volume = volume
		self.text = []
	
	def __str__(self):
		str = self.title
		for text in self.text:
			str += "\n" + text
		return str
		
	def add_text(self, text):
		self.text.append(text)
		
	def to_html(self):
		str = "<h1>{0}</h1>".format(self.title)
		for text in self.text:
			str += "\n" + "<p>{0}</p>".format(text)
		return str

def parse_novel(title):
	config.read(title+"/config.ini", encoding="utf-8")
	global pattern, pattern_type
	pattern = re.compile(config['SETTINGS']['ChapterPattern'])
	pattern_type = config['SETTINGS']['PatternType']
	dir = list(glob.iglob(title+"/*.xml"))
	dir.sort(key=lambda x: int(re.match(r'.*chapter(\d+)', x).group(1)))
	for path in dir:
		xml2list(path)

def xml2list(file):
	doc = ET.parse(file).getroot()
	
	current_chapter = None
	
	for node in doc.iter("node"):
		text = node.get("text")
		check = pattern.match(text)
		if check:
			match pattern_type:
				case "Standard":
					current_chapter = Chapter(text, check.group(1))
				case "Volume":
					current_chapter = Chapter(text, check.group(2), check.group(1))
				case "VolumeAfter":
					current_chapter = Chapter(text, check.group(1), check.group(2))
			chapter_list.insert(current_chapter.number, current_chapter)
		elif current_chapter != None:
			if text != "":
				current_chapter.add_text(text)

	
def output_html(title):
	full_text = ""
	for chapter in chapter_list:
		full_text += chapter.to_html()

	html = open(title+"/test.html", "w", encoding="utf-8")
	html.write(full_text)
	html.close()
	
def print_chapters():
	for chapter in chapter_list:
		print(chapter.title, chapter.number, chapter.volume)
		
def generate_uuid(title):
	return str(uuid.uuid5(uuid.UUID("0192ed6b-1c84-70fe-a8a2-f498827a3a53"), title))
	
def generate_epub(title):
	book = epub.EpubBook()
	book.set_identifier(generate_uuid(title))
	book.set_title(title)
	book.set_language("en")
	
	book.add_author("")
	
	cover = config['SETTINGS']['CoverImage']
	if cover:
		book.set_cover("cover.jpg", open(title+"/"+cover, "rb").read())
	#add notice page
	book_chapters = []
	for idx, chapter in enumerate(chapter_list):
		c = epub.EpubHtml(title=chapter.title, file_name="chapter{0}.xhtml".format(idx))
		c.set_content(chapter.to_html())
		book.add_item(c)
		book_chapters += [c]
	book.add_item(epub.EpubNcx())
	book.add_item(epub.EpubNav())
	#can add css if want
	book.toc = (#epub.Link("Notice.xhtml", "Notice", "notice"),
							book_chapters
	)
	
	book.spine = ["cover", "notice", "nav"] + book_chapters
	epub.write_epub(title+"/test.epub", book, {})

if (args.title):
	parse_novel(args.title)
	#output_html(args.title)
	print_chapters()
	generate_epub(args.title)
	
	

#xml2list("./chapter1.xml")



#doc = doc.find(".//node[@resource-id='section']")
#title = doc.find(".//*[@class='android.view.View']//*[1]").get("text")
#chapter = "<h1>{0}</h1>".format(title)



#for text in doc.findall(".//*[@class='android.widget.TextView']"):

