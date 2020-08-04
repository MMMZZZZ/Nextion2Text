from string import whitespace
import os
import sys

class indentList(list):
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


class component:
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
        comp: component
        return [v["typeName"] for v in self.types.values()].index(comp.typeStr)

    def sortComponents(self):
        self.components.sort(key=lambda comp: comp.__repr__())
        self.components.sort(key=self.sortCriteria)

    def text(self, indentLevel=0, indent=4, recursive=True, emptyLinesLimit=1):
        return "".join(self.textLines(indentLevel, indent, recursive, emptyLinesLimit))

    def textLines(self, indentLevel=0, indent=4, recursive=True, emptyLinesLimit=1):
        result = indentList()
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
                comp: component
                if recursive:
                    compTextLines = comp.textLines(0, result.indent, True, result.emptyLinesLimit)
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


class HMI:
    def __init__(self, HMIFile):
        s = HMIFile.read().decode("ansi")
        allComponentStrs = s.split("\x00\x00\x00att")
        allComponentStrs = ["att" + e for i,e in enumerate(allComponentStrs) if i > 0]
        self.pages = []
        for cs in allComponentStrs:
            comp = component(cs)
            if comp.typeStr == "Page":
                self.pages.append(comp)
            else:
                self.pages[-1].components.append(comp)
        """
        For some reason pages and components can be found multiple times, each time a different version.
        It seems like the last version is the right one. The following code 
        kicks all versions except for the last one from the list of all pages. 
        """
        noDuplicates = dict()
        for i, page in enumerate(self.pages):
            noDuplicates[page.objname] = i
        self.pages = [self.pages[i] for i in noDuplicates.values()]
        for page in self.pages:
            noDuplicates = dict()
            for i, comp in enumerate(page.components):
                noDuplicates[comp.objname] = i
            page.components = [page.components[i] for i in noDuplicates.values()]
            page.sortComponents()

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

with open(os.path.join(hmiPath, hmiFile), "rb") as f:
    hmi = HMI(f)

hmiTextFolder = os.path.join(hmiPath, hmiTextFolder)
if not os.path.exists(hmiTextFolder):
    os.mkdir(hmiTextFolder)

totalCodeLines = 0
for i,page in enumerate(hmi.pages):
    with open(os.path.join(hmiTextFolder, page.objname + hmiTextFileExt), "w") as f:
        pageText = page.text(emptyLinesLimit=1)
        lines = pageText.count("\n")
        totalCodeLines += lines
        print(page.__repr__())
        print(" ", lines, "Lines")
        f.write(pageText)
print("Total", totalCodeLines, "Lines")

print("done")
