# Nextion to Text Converter
## Description
This script creates a text file for each page of your Nextion GUI, containing all components of the page, the entire source code, and some of the component's properties. 
This tool was mainly created to get meaningfull commit diffs (which is not possible with the binary HMI file) and to be able to read the source code without having the Nextion Editor installed. 
This tool can NOT convert text back to a .HMI file. 

## Usage
The script is written in Python, v3.8. No additional modules are required. Open the python file, scroll down to the bottom, and change the file paths. 
* hmiPath: Full path of the folder containing the Nextion HMI file.
* hmiFile: Name of the Nextion HMI file
* hmiTextFolder: Name of the subfolder which will contain the text files. It will be created as subfolder of `hmiPath`
* hmiTextFileExt: File extension for the text files (f.ex. ".txt")

Not very intuitive, but good enough for now. 

## Limitations
* While the source code of all components will be displayed, only a few component properties are currently supported (namely those that occur in my own programs). 

## Example
The Example folder contains a HMI file and a subfolder with the resultung text files.