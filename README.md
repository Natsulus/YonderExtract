# Yonder Extract
## Preamble
At the end of January 2025, the YONDER platform/app announced that they would be discontinued, leaving until July 31 2025 before access to the service and all content is gone. 

This repository was made to provide instructions on how to extract the Android View into an XML file and in doing so, also be able to also get the text of the chapters on Yonder. 
Also included is Python code that takes the XML files, finds all the text and builds an EPUB using it (likely doesn't work with some series in its current state and will need adjustments). 

I won't be hand-holding on how to do everything, so search it up if you don't know how to do something.

**Note: This only works for Android, so you won't be able to grab your Yonder account library if it was created with Apple ID.**

## Instructions

### 1. Initial Setup

#### 1a. Device and ADB Setup
1. Follow the instructions to setup your device and ADB on your computer: [Setup ADB](https://www.xda-developers.com/install-adb-windows-macos-linux/)
2. Connect your device to your computer or if you're using an emulator, use the commmand `adb connect 127.0.0.1:[PORT]` or `adb connect localhost:[PORT]` replacing `[PORT]` with the port number the emulator uses (please search that up yourself).
3. Verify your device/emulator is connected using the command `adb devices`

#### 1b. Folder Setup
1. Create a Folder and name it "YonderExtract" or whatever you want.
2. Download `YonderParse.py` and `Pull Chapter XML.bat` to the Folder
3. Create a Folder for each Novel and copy the `Pull Chapter XML.bat` into each one

### 2. Extract the Content
1. On your device or emulator, open a chapter to extract and wait for it to fully load.
2. In the folder for that novel, run the `Pull Chapter XML.bat`
3. `chapter#.xml` should be created, starting at 1 and incrementing for each new file
4. Repeat the process for all chapters.

### 3. Python Setup
WIP

### 4. Parse XML to an EPUB
WIP

## What does the batch file do?
It turns off echo, sets the chapter number to 1, uses `adb devices` to make sure the adb daemon is active, then checks if chapter numbers already exists and increments until it finds a free number, then it extracts the view into an XML file on the device, and finally moves the XML file from the device onto your computer with the free chapter number.