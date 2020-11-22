from string import whitespace
import os
import sys
import struct
from typing import List

class IndentList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 4
        self.indentLevel = 0
        self.indentStr = " "
        self.emptyLinesLimit = 1
        self.emptyLinesCount = 0

    def appendIndent(self, newStr):
        newStr: str
        if not newStr.strip(whitespace):
            if self.emptyLinesCount < self.emptyLinesLimit:
                self.emptyLinesCount += 1
            else:
                return
        else:
            self.emptyLinesCount = 0
        self.append(self.indentLevel * self.indent * self.indentStr + newStr)

    def appendIndentLine(self, newStr):
        newStr: str
        if not newStr.endswith("\n"):
            newStr += "\n"
        self.appendIndent(newStr)


class Component:
    types = {
        121: {
            "typeName": "Page",
            "events": {
                "codesload": "Preinitialize Event",
                "codesloadend": "Postinitialize Event",
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
                "codesunload": "Page Exit Event"
            },
            "properties": dict(),
        },
        52: {
            "typeName": "Variable",
            "events": dict(),
            "properties": {
                "vscope": "Scope",
                "sta": "Type",
                "val": "Initial Value",
                "txt": "Initial String",
                "txt_maxl": "Max. length"
            },
        },
        51: {
            "typeName": "Timer",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "tim": "Period [ms]",
                "en": "Running",
            },
        },
        54: {
            "typeName": "Number",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial Value",
            },
        },
        59: {
            "typeName": "Float",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial Value",
                "vvs1": "Divide by [10^x]"
            },
        },
        116: {
            "typeName": "Text",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "txt": "Initial Text",
                "txt_maxl": "Max. length"
            },
        },
        55: {
            "typeName": "Scrolling Text",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        112: {
            "typeName": "Picture",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        113: {
            "typeName": "Crop Picture",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        106: {
            "typeName": "Progress Bar",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        122: {
            "typeName": "Gauge",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        0: {
            "typeName": "Waveform",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        58: {
            "typeName": "QRCode",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        98: {
            "typeName": "Button",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "txt": "Caption",
                "txt_maxl": "Max. length"
            },
        },
        53: {
            "typeName": "Dual-state Button",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial State",
                "txt": "Caption",
                "txt_maxl": "Max. length",
            },
        },
        109: {
            "typeName": "Hotspot",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        56: {
            "typeName": "Checkbox",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        57: {
            "typeName": "Radio",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": dict(),
        },
        1: {
            "typeName": "Slider",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
                "codesslide": "Touch Move"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial Position",
                "minval": "Lower End",
                "maxval": "Upper End",
            },
        },
        -1: {
            "typeName": "Unknown",
            "events": dict(),
            "properties": dict(),
        }
    }

    def __init__(self, componentStr):
        self.components = []
        self.typeId = 0
        self.typeStr = ""
        self.events = dict()
        self.sloc = 0
        self.properties = dict()
        self.propNameMaxLength = 0
        self.raw = componentStr
        self.objname = self.getProperty("objname")
        self.loadType()
        self.loadEvents()
        self.loadProperties()

    def __repr__(self):
        return self.typeStr + " " + self.objname

    def sortCriteria(self, comp):
        comp: Component
        return [v["typeName"] for v in self.types.values()].index(comp.typeStr)

    def sortComponents(self):
        self.components.sort(key=lambda comp: comp.__repr__())
        self.components.sort(key=self.sortCriteria)

    def text(self, indentLevel=0, indent=4, recursive=True, emptyLinesLimit=1):
        self.sloc = 0
        return "".join(self.textLines(indentLevel, indent, recursive, emptyLinesLimit)), self.sloc

    def textLines(self, indentLevel=0, indent=4, recursive=True, emptyLinesLimit=1):
        result = IndentList()
        result.indentStr = " "
        result.indentLevel = indentLevel
        result.indent = indent
        result.emptyLinesLimit = emptyLinesLimit
        result.appendIndentLine(self.__repr__())
        result.indentLevel += 1
        if self.properties:
            result.appendIndentLine("Properties")
            result.indentLevel += 1
            for prop, val in self.properties.items():
                prop: str
                prop = self.types[self.typeId]["properties"][prop]
                try:
                    val = val.replace("\r\n", "\\r\\n")
                except:
                    pass
                line = prop.ljust(self.propNameMaxLength, " ") + ": " + str(val)
                result.appendIndentLine(line)
            result.indentLevel -= 1
            result.appendIndentLine("")
        if self.events:
            result.appendIndentLine("Events")
            result.indentLevel += 1
            for event, code in self.events.items():
                code: str
                result.appendIndentLine(event)
                result.indentLevel += 1
                codeLines = code.split("\n")
                for cl in codeLines:
                    originalLength = len(cl)
                    clStripped = cl.lstrip(" ")
                    if clStripped and not clStripped.startswith("//"):
                        self.sloc += 1
                    clIndentLevel = (originalLength - len(clStripped)) // 2
                    clStripped = result.indentStr * result.indent * clIndentLevel + clStripped
                    result.appendIndentLine(clStripped)
                result.indentLevel -= 1
                result.appendIndentLine("")
            result.indentLevel -=1
            result.appendIndentLine("")
        if self.components:
            result.appendIndentLine("Components")
            result.indentLevel += 1
            for comp in self.components:
                comp: Component
                if recursive:
                    compTextLines = comp.textLines(0, result.indent, True, result.emptyLinesLimit)
                    self.sloc += comp.sloc
                    for line in compTextLines:
                        result.appendIndentLine(line)
                    result.appendIndentLine("")
                else:
                    result.appendIndentLine(comp.__repr__())
            result.indentLevel -= 1
            result.appendIndentLine("")
        return result

    def entryEnd(self, start):
        end1 = self.raw.find("\x00\x00\x00\x00", start)
        end2 = self.raw.find("\x00\x00\x00", start)
        if end1 != end2:
            end2 -= 1
        return end2

    def getProperty(self, property):
        # "normal" propertiy names are filled up with \x00 to a length of 16 bytes.
        # "normal" properties end with a random caracter and 3x \x00
        # Variable length properties have the length indicated after their name
        property: str

        if property in self.types[self.typeId]["events"]:
            propertyStr = property + "-"
            propertyIndex = self.raw.find(propertyStr)
            if propertyIndex >= 0:
                # Variable length property
                propertyIndex += len(propertyStr)
                propertyLengthEnd = self.entryEnd(propertyIndex)
                propertyLength = int(self.raw[propertyIndex:propertyLengthEnd])
                properties = list()
                propertyIndex = propertyLengthEnd + 4
                index = 0
                while index < propertyLength:
                    lineEnd = self.entryEnd(propertyIndex)
                    properties.append(self.raw[propertyIndex:lineEnd])
                    propertyIndex = lineEnd + 4
                    index += 1
                return properties
        propertyStr = property + (16 - len(property)) * "\x00"
        propertyIndex = self.raw.find(propertyStr) + 16
        if propertyIndex >= 0:
            propertyEnd = self.entryEnd(propertyIndex)
            return  self.raw[propertyIndex:propertyEnd]
        raise Exception("PropertyNotFound: " + property)

    def loadType(self):
        self.typeId = ord(self.getProperty("type"))
        if self.typeId not in self.types:
            self.typeId = -1
        self.typeStr = self.types[self.typeId]["typeName"]

    def loadEvents(self):
        for event, commonName in self.types[self.typeId]["events"].items():
            eventData = self.getProperty(event)
            self.events[commonName] = "\n".join(eventData)

    def loadProperties(self):
        self.propNameMaxLength = 0
        if self.objname == "fSlider":
            print("")
        for prop in self.types[self.typeId]["properties"].keys():
            try:
                data = self.getProperty(prop)
            except:
                continue
            if prop in ["minval", "maxval", "txt_maxl", "tim", "vvs1"] or (prop == "val" and self.typeStr != "Dual-State Button"):
                self.properties[prop] = 0
                for i,e in enumerate(data):
                    self.properties[prop] += (ord(e) << (8 * i))
            elif prop == "en":
                if ord(data[0]):
                    self.properties[prop] = "Yes"
                else:
                    self.properties[prop] = "No"
            elif prop == "vscope":
                if ord(data[0]):
                    self.properties[prop] = "Global"
                else:
                    self.properties[prop] = "Local"
            elif prop == "sta":
                if ord(data[0]):
                    self.properties[prop] = "String"
                else:
                    self.properties[prop] = "int32"
            elif prop == "en":
                if ord(data[0]):
                    self.properties[prop] = "Yes"
                else:
                    self.properties[prop] = "No"
            elif prop == "val" and self.typeStr == "Dual-State Button":
                if ord(data[0]):
                    self.properties[prop] = "Pushed"
                else:
                    self.properties[prop] = "Not pushed"
            elif prop == "txt":
                self.properties[prop] = "\"" + data + "\""
            else:
                self.properties[prop] = data

            if len(self.types[self.typeId]["properties"][prop]) > self.propNameMaxLength:
                self.propNameMaxLength = len(self.types[self.typeId]["properties"][prop])

        if self.typeStr == "Variable":
            if self.properties["sta"] == "int32":
                if "txt" in self.properties:
                    self.properties.pop("txt")
                if "txt_maxl" in self.properties:
                    self.properties.pop("txt_maxl")
            else:
                if "val" in self.properties:
                    self.properties.pop("val")

class Header:
    _headerFormat = ""

    def __init__(self, raw, start = 0):
        self._raw = raw
        self._headerStart = start
        self.headerSize = self.__getHeaderSize()
        self._processData(self.__getHeaderData())

    def __getHeaderData(self):
        return struct.unpack(self._headerFormat, self._raw[self._headerStart:self._headerStart+self.headerSize])

    def __getHeaderSize(self):
        return struct.calcsize(self._headerFormat)

class PageContentHeader(Header):
    _headerFormat = "III"

    def _processData(self, data):
        self.startOffset : int
        self.size  : int
        self.startOffset = data[0]
        self.size  = data[1]

    def __repr__(self):
        return "Header of " + self.name

class PageHeader(Header):
    _headerFormat = "IIIII?bbb16s16b"

    #crc[4], datasize[4], datainfoaddr[4], numberobj[4], password[4], locked[1], ?[1], version[1], ?[1], name[16], reserved[16]
    def _processData(self, data):
        self.crc          : int
        self.size         : int
        self.start        : int
        self.count        : int
        self.password     : int
        self.locked       : bool
        self.fileVersion  : int
        self.name         : str
        self.components   : List[PageContentHeader] = list()
        self.crc          = data[0]
        self.size        = data[1]
        if data[2] != self.headerSize:
            ValueError("Header Size Mismatch. Expected: {0}, got: {1}".format(self.headerSize, data[2]))
        self.count        = data[3]
        self.password     = data[4]
        self.locked       = data[5]
        self.fileVersion  = data[7]
        self.name         = data[9].decode("ansi").rstrip("\x00")
        index = self._headerStart + self.headerSize
        for i in range(self.count):
            obj = PageContentHeader(self._raw, index)
            self.components.append(obj)
            index += obj.headerSize


class HMIContentHeader(Header):
    _headerFormat = "16sII?bbb"

    def _processData(self, data):
        self.name    : str
        self.start   : int
        self.size    : int
        self.deleted : bool
        self.name    = data[0].decode("ansi").rstrip("\x00")
        self.start   = data[1]
        self.size    = data[2]
        self.deleted = data[3]

    def isPage(self):
        return self.name.endswith(".pa")

    def isImage(self):
        return self.name.endswith(".i")

    def isImageSource(self):
        return self.name.endswith(".is")

    def __bool__(self):
        return not self.deleted

    def __repr__(self):
        return "Header of " + self.name

class HMIHeader(Header):
    _headerFormat = "I"

    def _processData(self, data):
        self.count   : int
        self.content : List[HMIContentHeader] = list()
        self.count = data[0]
        index = self._headerStart + self.headerSize
        for i in range(self.count):
            obj = HMIContentHeader(self._raw, index)
            if obj:
                self.content.append(obj)
            index += obj.headerSize
        self.count = len(self.content)

class Page:
    def __init__(self, raw, start: int, size: int):
        self.__raw = raw
        self.start = start
        self.size = size
        components : List[Component] = list()

        self.header = PageHeader(self.__raw, self.start)

        for comp in self.header.components:
            start = self.start + self.header.headerSize + comp.startOffset
            end = start + comp.size
            compStr = self.__raw[start:end].decode("ansi")
            components.append(Component(compStr))

        self.self = components.pop(0)
        self.self.components = components

class HMI:
    def __init__(self, HMIFilePath):
        objectList = list()
        with open(HMIFilePath, "rb") as HMIFile:
            self.raw = HMIFile.read()
        self.header = HMIHeader(self.raw)
        self.pages = []
        for obj in self.header.content:
            if obj.isPage():
                self.pages.append(Page(self.raw, obj.start, obj.size))
            """
            end = obj.start + len(obj)
            s = self.raw[obj.start:end].decode("ansi")
            comp = component(s)
            if comp.typeStr == "Page":
                self.pages.append(comp)
            else:
                self.pages[-1].components.append(comp)
            """

    def text(self, indent=4, emptyLinesLimit=1):
        return "work in progress"



### Here starts the script part.
if len(sys.argv) != 5:
    print("Arguments: ", sys.argv)
    raise ValueError("Exactly 4 arguments required: Working directory, HMI file name, output subfolder name, output text file extension.")

hmiPath = sys.argv[1]
hmiFile = sys.argv[2]
hmiTextFolder = sys.argv[3]
hmiTextFileExt = sys.argv[4]

hmi = HMI(os.path.join(hmiPath, hmiFile))

hmiTextFolder = os.path.join(hmiPath, hmiTextFolder)
if not os.path.exists(hmiTextFolder):
    os.mkdir(hmiTextFolder)

totalCodeLines = 0
for i,page in enumerate(hmi.pages):
    with open(os.path.join(hmiTextFolder, page.self.objname + hmiTextFileExt), "w") as f:
        pageText, sloc = page.self.text(emptyLinesLimit=1)
        totalCodeLines += sloc
        print(page.self.__repr__())
        print(" ", sloc, "Lines of source code")
        f.write(pageText)
print("Total:", totalCodeLines, "Lines of source code")

print("done")
