# Yonder Extract
## Preamble
At the end of January 2025, the YONDER platform/app announced that they would be discontinued, leaving until July 31, 2025 before access to the service and all content is gone. 

This repository was made to provide instructions on how to extract the Android View into an XML file and in doing so, also be able to get the text of the chapters on Yonder. 
Also included is Python code that takes the XML files, finds all the text, and builds an EPUB using it (likely doesn't work with some series in its current state and will need adjustments). 

I won't be hand-holding on how to do everything, so search it up if you don’t know how to do something.

**Note 1: This only works for Android, so you won’t be able to grab your Yonder account library if it was created with Apple ID.**

**Note 2: This was written assuming you are using Windows on your PC**

## Instructions

### 1. Initial Setup

#### 1a. Device and ADB Setup
1. Follow the instructions to set up your device and ADB on your computer: [Setup ADB](https://www.xda-developers.com/install-adb-windows-macos-linux/)
2. Connect your device to your computer or, if using an emulator, use the command `adb connect 127.0.0.1:[PORT]` or `adb connect localhost:[PORT]`, replacing `[PORT]` with the port number the emulator uses (search that up yourself).
3. Verify your device/emulator is connected using the command `adb devices`

#### 1b. Folder Setup
1. Create a main folder named "YonderExtract" (or whatever you prefer).
2. Download `YonderParse.py`,  `Pull Chapter XML.bat`, and `config.ini` into "YonderExtract".
3. Inside "YonderExtract", create a subfolder for each novel (e.g. "Dragon Poor") and copy `Pull Chapter XML.bat` into each subfolder.

### 2. Extract the Content
1. On your device or emulator, open a chapter to extract and wait for it to fully load.
2. In the novel’s subfolder (e.g. "YonderExtract/Dragon Poor"), run `Pull Chapter XML.bat`.
3. `chapter#.xml` should be created, starting at 1 and incrementing for each new file. If the novel starts with a chapter 0, you might want to rename it at such.
4. Repeat the process for all chapters.

### 3. Python Setup
1. Install Python 3.x if you don’t have it: [Download Python](https://www.python.org/downloads/). During installation, check "Add Python to PATH".
2. Open a command prompt and verify Python is installed with `python --version` or `py --version`.
3. Install the required library by running: `pip install ebooklib`.

### 4. Parse XML to an EPUB
1. Open a command prompt in the "YonderExtract" folder (e.g. `cd path\to\YonderExtract`).
2. Run the script with: `py YonderParse.py "NovelName"`, replacing "NovelName" with the novel’s subfolder name. Use quotes if the name has spaces (e.g. `py YonderParse.py "Dragon Poor"`).
3. The script will:
   - Look for all `chapter#.xml` files in "YonderExtract/NovelName".
   - Detect chapter titles like "Chapter 1: Title", "Chapter 1 -/– Title", or "Chapter 1". For `chapter1.xml`, it also recognizes "Prologue" as a chapter.
   - Use the subfolder name as the EPUB title (e.g. "NovelName.epub") unless overridden.
   - Add `cover.png` (preferred) or `cover.jpg` from the subfolder as the cover if either exists.
   - Generate an EPUB file named after the subfolder (or custom title) in the subfolder.
4. Check the output message (e.g. "EPUB generated: path\to\YonderExtract\NovelName\NovelName.epub") and open the EPUB in a reader to verify.

#### Optional: Customizing with `config.ini`
- If the defaults don’t fit your novel, create or copy the `config.ini` file into the novel’s subfolder (e.g. "YonderExtract/NovelName/config.ini"). Add only the fields you need to change from the defaults:
```
[SETTINGS]
Title = Custom Title
Author = Author Name
CoverImage = custom_filename.jpg
ChapterPattern = Regular-Expression
PatternType = Standard
Description = A brief description of the novel.
Publisher = Custom Publisher
```
**Fields** (all optional):
- `Title`: Overrides subfolder name.
- `Author`: Sets author name (default: "Unknown").
- `CoverImage`: Uses a custom cover filename (default: `cover.png` if present, then `cover.jpg`).
- `ChapterPattern`: Custom regex for chapter titles (default: tries "Chapter #: ...", "Chapter # -/– ...", "Chapter #").
- `PatternType`: "Standard" (default), "Volume" (e.g. "Volume #, Chapter #"), or "VolumeAfter" (e.g. "Chapter # of Act #").
- `Description`: Adds a description.
- `Publisher`: Sets publisher (default: "YONDER").

Example for a novel with a different Chapter structure from the defaults:
```
[SETTINGS]
Title = The Heroine of Drayfox
ChapterPattern = Chapter (\d+) of Act (\d+)
PatternType = VolumeAfter
```
- Run the script again after adding `config.ini` to apply these settings. Omit any fields you don’t need to change.

## What does the batch file do?
The batch file (`Pull Chapter XML.bat`) hides command text, starts with chapter number 1, wakes up the ADB tool with `adb devices`, finds the next free chapter number (like `chapter1.xml`, `chapter2.xml`, etc.), grabs the current screen view as an XML file on your device, and pulls it to your computer as `chapter#.xml` with that number.

## "It doesn't work with NovelName!" or "I'm having an issue with..."
Please create an issue on this repository or contact me on Reddit with the details on your issue.