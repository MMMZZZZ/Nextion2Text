# Nextion to Text Converter

## Description

This script creates a text file for each page of your Nextion GUI, containing all components of the page, including their properties and the entire source code.

This tool was mainly created to get meaningful commit diffs (which is not possible with the binary HMI file) and to allow you to share *your* source code with other people as easily as developers are used to. Binary files are simply impractical for development and sharing.

This tool can NOT convert text back to a .HMI file. 

## Usage

The script is written in Python, v3.8. No additional modules are required. 
The script offers a couple of options to customize its behavior and output. You can get a full description of all command line options with

```python Nextion2Text.py -h```

For most basic usage, simply run

```python Nextion2Text.py -i PATH_TO_HMI_FILE -o FOLDER_FOR_TEXT_FILES```

Note that by default, visual properties (x/y position, colors, pictures, fonts, ...) are *not* included, see example links below.

## Features and Limitations

Known to work with files created with editor version 1.60.x and newer. May work with some 0.5x versions.

Supports all Nextion components, including the Intelligent series components - except for the new TouchCap component (only partially  supported without attributes). 

However, Intelligent series attributes are only partially supported by now. You can use the `--properties unknown` (See command line help for more details) option to include unknown attributes, too. 

## Example

The [Example folder](/Example) contains a HMI file, a subfolder with the resultung text files, and a `.cmd` file that has been executed to generate the text files. In addition, here are some interesting commits you may want to look at: 
* [How a commit diff looks when the HMI file gets modified](https://github.com/MMMZZZZ/Nextion2Text/commit/e7aa62c85d3041022f8cb8209b569766fcae8477)
* [Visual attributes included](https://github.com/MMMZZZZ/Nextion2Text/blob/cf06bb44621ae505129b2297d8cff55afdaf298c/Example/Syntherrupter_Nextion_Code/Menu.txt)
* [Visual attributes excluded](https://github.com/MMMZZZZ/Nextion2Text/blob/6f858edb0d3eca1824900fcacd19ab91ff8e2af8/Example/Syntherrupter_Nextion_Code/Menu.txt)
* [diff between both](https://github.com/MMMZZZZ/Nextion2Text/commit/cf06bb44621ae505129b2297d8cff55afdaf298c)

## License

This repository is licensed under MPL-2.0. My understanding of this license is that you have to make any changes to my code available under a similar license (GPL compatible). However you do not have to share the rest of your work (unlike GPL). It's kind of a compromise between the MIT and the GPL license. 
