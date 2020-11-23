# Nextion to Text Converter

## Description

This script creates a text file for each page of your Nextion GUI, containing all components of the page, the entire source code, and some of the component's properties. 
This tool was mainly created to get meaningfull commit diffs (which is not possible with the binary HMI file) and to be able to read the source code without having the Nextion Editor installed. 
This tool can NOT convert text back to a .HMI file. 

## Usage

The script is written in Python, v3.8. No additional modules are required. 
Run the script from the command line with
`python Nextion2Text.py FOLDER_PATH HMI_FILE SUBFOLDER FILE_EXT`
Where
* `FOLDER_PATH` is the path to the folder containing the Nextion HMI file.
* `HMI_FILE` is the name of the Nextion HMI file
* `SUBFOLDER` is the name of the folder which will contain the resulting text files. It will be created relative to `FOLDER_PATH`
* `FILE_EXT` is the file extension of the resulting text files (f.ex. ".txt")

## Features and Limitations

Supports all Nextion components, including the Intelligent series components. 

However, to keep files reasonable small, only "important" component attributes are included. Since this is text only, all of the visual attributes are f.ex. not included (size, position, etc). 

## Example

The Example folder contains a HMI file and a subfolder with the resultung text files. If you want to see how a commit diff looks like when the HMI file has been modified, here's an example: https://github.com/MMMZZZZ/Nextion2Text/commit/f973ae2f13539c2c6a4b75de33a59943dda9ab27

## License

This code is licensed under MPL-2.0. My understanding of this license is that you have to make any changes to my code available under a similar license (GPL compatible). However you do not have to share the rest of your work (unlike GPL). It's kind of a compromise between the MIT and the GPL license. 
