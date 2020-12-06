# Nextion to Text Converter

## Description

This script creates a text file for each page of your Nextion GUI, containing all components of the page, the entire source code, and some of the component's properties. 

This tool was mainly created to get meaningfull commit diffs (which is not possible with the binary HMI file) and to allow you to share *your* source code with other people as easily as developpers are used to. Binary files are simply impractical for developpment and sharing.

This tool can NOT convert text back to a .HMI file. 

## Usage

The script is written in Python, v3.8. No additional modules are required. 
The script offers a couple options to customize its behavior and output. For most basic usage, simply run

```python Nextion2Text.py -i HMI_FILE -o OUTPUT_FOLDER```

Where

* `PATH_TO_HMI_FILE` is the path to the Nextion HMI file.
* `OUTPUT_FOLDER` is the name of the folder which will contain the resulting text files. It will be created relative to `FOLDER_PATH`

Note that by default, no visual properties (x/y position, colors, pictures, fonts, ...) are *not* included. 

To get a full description of all command line options, use

```python Nextion2Text.py -h```

## Features and Limitations

Supports all Nextion components, including the Intelligent series components. 

However, Intelligent series attributes are only partially supported by now. You can use the `--properties unknown` (See command line help for more details) option to include unknown attributes, too. 

## Example

The Example folder contains a HMI file and a subfolder with the resultung text files. If you want to see how a commit diff looks like when the HMI file has been modified, here's an example: https://github.com/MMMZZZZ/Nextion2Text/commit/f973ae2f13539c2c6a4b75de33a59943dda9ab27

**Note:** The given example is from an earlier version of the parser that had some bugs and severe limitations. However, it still gives a good idea about what you get!

## License

This code is licensed under MPL-2.0. My understanding of this license is that you have to make any changes to my code available under a similar license (GPL compatible). However you do not have to share the rest of your work (unlike GPL). It's kind of a compromise between the MIT and the GPL license. 
