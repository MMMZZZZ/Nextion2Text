from string import whitespace
import os
import sys
import struct
from typing import List
import argparse

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
    """
    How the attributes dict is organized:
    attributes:
        "encoded" name:
            -1: default interpretation:
                name: Name by which the encoded name will be replaced
                type: int/str/strlist/bool - how to decode the content
                mapping: optional: replace the values by a string
            12: Optional interpretation if attribute is part of a component of type 12
    """
    codeEvents = {
        "codesload":    "Preinitialize Event",
        "codesloadend": "Postinitialize Event",
        "codesdown":    "Touch Press Event",
        "codesup":      "Touch Release Event",
        "codesunload":  "Page Exit Event",
        "codestimer":   "Timer Event",
        "codesplayend": "Play Complete Event",
    }
    attributes = {
        "type": {
            "name": "Type",
            "struct": "<B",
            "mapping": {
                -1:  "Unknown",
                121: "Page",
                52:  {
                    "sta": {
                        0: {
                            "name": "Variable (int32)",
                        },
                        1: {
                            "name": "Variable (string)",
                        },
                    },
                },
                51:  "Timer",
                54:  "Number",
                59:  "XFloat",
                116: "Text",
                55:  "Scrolling Text",
                112: "Picture",
                113: "Crop Picture",
                106: "Progress Bar",
                122: "Gauge",
                0:   "Waveform",
                58:  "QR Code",
                98:  "Button",
                53:  "Dual-state Button",
                109: "Hotspot",
                56:  "Checkbox",
                57:  "Radio",
                1:   "Slider",
                67:  "Switch",
                61:  "Combo Box",
                68:  "Text Select",
                62:  "SLText",
                66:  "Data Record",
                65:  "File Browser",
                63:  "File Stream",
                2:   "Gmov",
                3:   "Video",
                4:   "Audio",
                60:  "External Picture",
            },
        },
        "id": {
            "name": "ID",
            "struct": "<B",
        },
        "vscope": {
            "name": "Scope",
            "struct": "<B",
            "mapping": {
                0: "local",
                1: "global",
            },
        },
        "objname": {
            "name": "Object Name",
            "struct": "s",
        },
        "sta": {
            "name": "Variant",
            "struct": "<B",
            "mapping": {
                0: "Crop Image Background",
                1: "Solid Color Background",
                2: "Image Background",
            },
            "type": {
                52: {
                    "mapping": {
                        0: "int32",
                        1: "string",
                    },
                },
                121: {
                    "mapping": {
                        0: "No background (white)",
                        1: "Solid color",
                        2: "Picture",
                    },
                },
            },
            "model": {
                "P": {
                    "type": {
                        121: {
                            "mapping": {
                                0: "No background (transparent)",
                            },
                        },
                    },
                },
            },
        },
        "val": {
            "name": "Initial value",
            "struct": "<i",
            "type": {
                53: {
                    "name": "Initial state",
                    "mapping": {
                        0: "Unpressed",
                        1: "Pressed",
                    },
                },
                98: 53,
                56: {
                    "name": "Initial state",
                    "mapping": {
                        0: "Unselected",
                        1: "Selected",
                    },
                },
                57: 56,
            },
        },
        "x": {
            "name": "x coord.",
            "struct": "<H",
            "vis": True,
            "type": {
                121: {
                    "ignore": True,
                },
            },
            "model": {
                "P": {
                    "drag": {
                        1: {
                            "name": "Initial x coord."
                        },
                    },
                },
            },
        },
        "y": {
            "name": "y coord.",
            "struct": "<H",
            "vis": True,
            "type": {
                121: {
                    "ignore": True,
                },
            },
            "model": {
                "P": {
                    "drag": {
                        1: {
                            "name": "Initial y coord."
                        },
                    },
                },
            },
        },
        "w": {
            "name": "Width",
            "struct": "<H",
            "vis": True,
            type: {
                121: {
                    "ignore": True,
                },
            },
        },
        "h": {
            "name": "Height",
            "struct": "<H",
            "vis": True,
            "type": {
                121: {
                    "ignore": True,
                },
            },
        },
        "bco": {
            "name": "Background Color",
            "struct": "<H",
            "vis": True,
            "sta": {
                0: {
                    "ignore": True,
                },
                2: 0,
            },
        },
        "pco": {
            "name": "Font Color",
            "struct": "<H",
            "vis": True,
            "sta": {
                0: {
                    "ignore": True,
                },
                2: 0,
            },
            "type": {
                58: {
                    "name": "Foreground Color"
                },
                53: {
                    "name": "Font Color (Unpressed)"
                },
                98: 53,
            },
        },
        "pco2": {
            "name": "Font Color (Pressed)",
            "struct": "<H",
            "vis": True,
            "ignore": True,
            "type": {
                53: {
                    "sta": {
                        1: {
                            "ignore": False,
                        },
                    },
                },
                98: 53,
            },
        },
        "pic": {
            "name": "Picture ID",
            "struct": "<H",
            "vis": True,
            "type": {
                121: {
                    "sta": {
                        0: {
                            "ignore": True,
                        },
                        1: 0,
                    },
                },
            },
        },
        "drag": {
            "name": "Dragging",
            "struct": "<B",
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
                "P": {
                    "type": {
                        121: {
                            "ignore": True
                        },
                    },
                },
            },
        },
        "disup": {
            "name": "Disable release event after dragging",
            "struct": "<B",
            "model": {
                "T": {
                    "ignore": True
                },
                "K": "T",
                "P": {
                    "type": {
                        121: {
                            "ignore": True
                        },
                    },
                    "drag": {
                        0: {
                            "ignore": True
                        }
                    }
                },
            },
        },
        "aph": {
            "name": "Opacity",
            "struct": "<B",
            "vis": True,
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
        "first": {
            "name": "Effect Priority",
            "struct": "<B",
            "vis": True,
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
                "P": {
                    "effect": {
                        0: {
                            "ignore": True,
                        },
                    },
                },
            },
        },
        "time": {
            "name": "Effect Time",
            "struct": "<H",
            "vis": True,
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
                "P": {
                    "effect": {
                        0: {
                            "ignore": True,
                        },
                    },
                },
            },
        },
        "sendkey": {
            "name": "Dunno",
            "struct": "<B",
            "ignore": True,
        },
        "movex": {
            "name": "",
            "struct": "<H",
            "vis": True,
            "ignore": True
        },
        "movey": {
            "name": "",
            "struct": "<H",
            "vis": True,
            "ignore": True
        },
        "endx": {
            "name": "",
            "struct": "<H",
            "vis": True,
            "ignore": True
        },
        "endy": {
            "name": "",
            "struct": "<H",
            "vis": True,
            "ignore": True
        },
        "effect": {
            "name": "Effect",
            "struct": "<B",
            "vis": True,
            "mapping": {
                0: "load fly into",
                1: "top fly into",
                2: "bottom fly into",
                3: "left fly into",
                4: "right fly into",
                5: "top left fly into",
                6: "top right fly into",
                7: "bottom left fly into",
                8: "bottom right fly into",
                9: "fade into the gradual change",
                10: "middle zoom",
            },
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
        "lockobj": {
            "name": "Locked",
            "struct": "<B",
            "mapping": {
                0: "No",
                1: "Yes",
            },
        },
        "groupid0": {
            "struct": "<I",
            "ignore": True
        },
        "groupid1": {
            "struct": "<I",
            "ignore": True
        },
        "up": {
            "name": "Swide up page ID",
            "struct": "<B",
            "type": {
                122: {  # Gauge
                    "vis": True,
                    "name": "Gauge Head Length"
                },
            },
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
        "down": {
            "name": "Swide down page ID",
            "struct": "<B",
            "type": {
                122: {  # Gauge
                    "vis": True,
                    "name": "Gauge Head Length"
                },
            },
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
        "left": {
            "name": "Swide left page ID",
            "struct": "<B",
            "type": {
                122: {  # Gauge
                    "vis": True,
                    "name": "Gauge Head Length"
                },
            },
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
        "right": {
            "name": "Swide right page ID",
            "struct": "<B",
            "model": {
                "T": {
                    "ignore": True,
                },
                "K": "T",
            },
        },
    }
    types = {
        121: {
            "typeName": "Page",
            "events": {
                "codesload": "Preinitialize Event",
                "codesloadend": "Postinitialize Event",
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
                "codesunload": "Page Exit Event",
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
                "codestimer": "Timer Event",
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
            "properties": {
                "vscope": "Scope",
                "txt": "Initial Text",
                "txt_maxl": "Max. length",
            },
        },
        112: {
            "typeName": "Picture",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
            },
        },
        113: {
            "typeName": "Crop Picture",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
            },
        },
        106: {
            "typeName": "Progress Bar",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "dez": "Horizontal/Verical",
                "val": "Inital value",
            },
        },
        122: {
            "typeName": "Gauge",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial angle",
            },
        },
        0: {
            "typeName": "Waveform",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "dir": "Flow direction",
                "ch": "Channels",
            },
        },
        58: {
            "typeName": "QRCode",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "txt": "Initial Text",
                "txt_maxl": "Max. length",
            },
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
            "properties": {
                "vscope": "Scope",
                "val": "Initial State",
            },
        },
        57: {
            "typeName": "Radio",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event"
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial State",
            },
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
        67: {
            "typeName": "Switch",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "val": "Initial state",
                "txt": "Label",
            },
        },
        61: {
            "typeName": "ComboBox",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "path": "Options",
            },
        },
        68: {
            "typeName": "TextSelect",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "path": "Options",
            },
        },
        62: {
            "typeName": "SLText",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "txt": "Text",
            },
        },
        66: {
            "typeName": "DataRecord",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "path": "Data file path",
                "format": "Format",
                "dir": "Header",
                "mode": "Auto create files",
            },
        },
        65: {
            "typeName": "FileBrowser",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "dir": "Directory path",
                "filter": "File name filter(s)",
                "psta": "Support sub-folder",
            },
        },
        63: {
            "typeName": "FileStream",
            "events": dict(),
            "properties": {
                "vscope": "Scope",
            },
        },
        2: {
            "typeName": "Gmov",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
                "codesplayend": "Play Complete Event",
            },
            "properties": {
                "vscope": "Scope",
                "vid": "Video ID",
                "loop": "Loop",
                "dis": "Playback Speed",
            },
        },
        3: {
            "typeName": "Video",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
                "codesplayend": "Play Complete Event",
            },
            "properties": {
                "vscope": "Scope",
                "from": "Source (Int/Ext)",
                "vid": "Video ID",
                "loop": "Loop",
                "dis": "Playback Speed",
            },
        },
        4: {
            "typeName": "Audio",
            "events": {
                "codesplayend": "Play Complete Event",
            },
            "properties": {
                "vscope": "Scope",
                "vid": "Audio ID",
                "loop": "Loop",
            },
        },
        60: {
            "typeName": "External Picture",
            "events": {
                "codesdown": "Touch Press Event",
                "codesup": "Touch Release Event",
            },
            "properties": {
                "vscope": "Scope",
                "path": "File Path",
            },
        },
        -1: {
            "typeName": "Unknown",
            "events": dict(),
            "properties": dict(),
        }
    }

    def __init__(self, raw, modelSeries="T"):
        self.components = []
        self.data = dict()
        self.typeId = 0
        self.typeStr = ""
        self.events = dict()
        self.sloc = 0
        self.uniqueSloc = set()
        self.properties = dict()
        self.propNameMaxLength = 0
        self.raw = raw
        self.modelSeries = modelSeries
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
        self.uniqueSloc = set()
        return "".join(self.textLines(indentLevel, indent, recursive, emptyLinesLimit)), self.sloc, len(self.uniqueSloc)

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
                        self.uniqueSloc.add(clStripped)
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
                    self.uniqueSloc |= comp.uniqueSloc
                    for line in compTextLines:
                        result.appendIndentLine(line)
                    result.appendIndentLine("")
                else:
                    result.appendIndentLine(comp.__repr__())
            result.indentLevel -= 1
            result.appendIndentLine("")
        return result

    def getProperty(self, property):
        # "normal" propertiy names are filled up with \x00 to a length of 16 bytes.
        # Variable length properties have the length indicated after their name
        property: str

        if property in self.types[self.typeId]["events"]:
            #rawBytes = self.raw.encode()
            propertyStr = (property + "-").encode("ansi")
            propertyIndex = self.raw.find(propertyStr)
            if propertyIndex >= 0:
                # Variable length property
                propertyTitleLength = struct.unpack_from("<I", self.raw, propertyIndex - 4)[0]
                propertyEntriesCount = int(self.raw[propertyIndex + len(propertyStr) : propertyIndex + propertyTitleLength].decode("ansi"))
                propertyIndex += propertyTitleLength
                properties = list()
                # propertyIndex = propertyLengthEnd + 4
                propertyEntries = 0
                while propertyEntries < propertyEntriesCount:
                    entryLength = struct.unpack_from("<I", self.raw, propertyIndex)[0]
                    propertyIndex += 4
                    entryEnd = propertyIndex + entryLength
                    properties.append(self.raw[propertyIndex:entryEnd].decode("ansi"))
                    propertyIndex = entryEnd
                    propertyEntries += 1
                return properties
        propertyStr = (property + (16 - len(property)) * "\x00").encode("ansi")
        propertyIndex = self.raw.find(propertyStr)
        if propertyIndex >= 0:
            propertyLength = struct.unpack_from("<I", self.raw, propertyIndex - 4)[0]
            return  self.raw[propertyIndex + len(propertyStr) : propertyIndex + propertyLength].decode("ansi")
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
        # First level parsing. Find all property entries
        index = 0
        properties = list()
        while index < len(self.raw):
            length = struct.unpack_from("<I", self.raw, index)[0]
            index += 4
            properties.append(self.raw[index : index + length])
            index += length
        # Drop the last (empty) element
        if not properties[-1]:
            properties = properties[:-1]
        # Second level parsing. Properties are grouped. The group name includes
        # the group length as string. F.ex. a attribute group wth 29 entries is
        # is encoded as "att-29". After those 29 entries the next group follows.
        index = 0
        self.data = dict()
        while index < len(properties):
            name, length = properties[index].rsplit(b"-", 1)
            length = int(length)
            index += 1
            self.data[name.decode("ansi")] = properties[index : index + length]
            index += length
        for k, v in self.data.items():
            if k == "att":
                # Parse attributes. They have a 16 byte fixed length name (filled with \x00 to 16)
                # followed by the actual value.
                rawAttributes = dict()
                # Model name is considered as an "attribute", too. (needed to know the right interpretation; see below)
                rawAttributes["model"] = self.modelSeries
                for att in v:
                    # Basic name, data separation and interpretation
                    attName = att[:16].rstrip(b"\x00").decode("ansi")
                    attData = att[16:]
                    if attName in self.attributes:
                        if "s" in self.attributes[attName]["struct"]:
                            attData = attData.decode("ansi")
                        else:
                            attData = struct.unpack(self.attributes[attName]["struct"], attData)[0]
                    rawAttributes[attName] = attData
                attributes = dict()
                # The interpretation of any attribute can depend on other attributes. (see code below)
                dependencies = set(self.attributes.keys())
                dependencies.add("model")
                for attName, attData in rawAttributes.items():
                    if attName in self.attributes:
                        # Build dictionary that interpretes and ignores the right attributes.
                        attProperties = dict()
                        attProperties.update(self.attributes[attName])
                        done = False
                        while not done:
                            done = True
                            for d in dependencies:
                                if d in attProperties:
                                    done = False
                                    if rawAttributes[d] in attProperties[d]:
                                        i = rawAttributes[d]
                                        while not type(attProperties[d][i]) is dict:
                                            vOld = i
                                            i = attProperties[d][i]
                                            attProperties[d].pop(vOld)
                                        try:
                                            attProperties.update(attProperties[d][i])
                                        except:
                                            print("help")
                                    attProperties.pop(d)
                        if ("vis" in attProperties and attProperties["vis"]) and not self.includeVisualProperties:
                            attProperties["ignore"] = True
                        if (not "ignore" in attProperties or not attProperties["ignore"]):
                            if "name" in attProperties:
                                attName = attProperties["name"]
                            if "mapping" in attProperties:
                                if attData in attProperties["mapping"]:
                                    attData = attProperties["mapping"][attData]
                            attributes[attName] = attData
                    else:
                        d = dict()
                        if len(attData) in (1, 2, 4):
                            s = "xBHxI"[len(attData)]
                        else:
                            s = "s"
                        d[attName] = {"name": "", "struct":"<" + s, "vis": True, "ignore": True}
                        print(d)
                self.data[k] = attributes
            else:
                # codelines
                if k in self.codeEvents:
                    k = self.codeEvents[k]
                self.data[k] = b"\n".join(v)


    def loadPropertiesOld(self, all=False):
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
    _headerFormat = "<III"

    def _processData(self, data):
        self.startOffset : int
        self.size  : int
        self.startOffset = data[0]
        self.size  = data[1]

    def __repr__(self):
        return "Header of " + self.name

class PageHeader(Header):
    _headerFormat = "<IIIII?bbb16s16b"

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
    _headerFormat = "<16sII?bbb"

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
    _headerFormat = "<I"

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
    def __init__(self, raw, start: int, size: int, modelSeries: str):
        self.__raw = raw
        self.start = start
        self.size = size
        components : List[Component] = list()

        self.header = PageHeader(self.__raw, self.start)

        for comp in self.header.components:
            start = self.start + self.header.headerSize + comp.startOffset
            end = start + comp.size
            compRaw = self.__raw[start:end]
            components.append(Component(compRaw, modelSeries))

        self.self = components.pop(0)
        self.self.components = components

class HMI:
    _models = {
        0x9aa696a7: {"short": "TJC3224T022_011", "long": "TJC 2.2\" Basic 320x240",},
        0xea4c3169: {"short": "TJC3224T024_011", "long": "TJC 2.4\" Basic 320x240",},
        0x0b997ef5: {"short": "TJC3224T028_011", "long": "TJC 2.8\" Basic 320x240",},
        0x72930b67: {"short": "TJC4024T032_011", "long": "TJC 3.2\" Basic 400x240",},
        0xade186d6: {"short": "TJC4832T035_011", "long": "TJC 3.5\" Basic 480x240",},
        0xd5f3287f: {"short": "TJC4827T043_011", "long": "TJC 4.3\" Basic 480x270",},
        0x98777c2d: {"short": "TJC8048T050_011", "long": "TJC 5.0\" Basic 480x240",},
        0x17c5fb02: {"short": "TJC8048T070_011", "long": "TJC 7.0\" Basic 480x270",},
        0x334e7201: {"short": "TJC3224K022_011", "long": "TJC 2.2\" Enhanced 320x240",},
        0x43a4d5cf: {"short": "TJC3224K024_011", "long": "TJC 2.4\" Enhanced 320x240",},
        0xa2719a53: {"short": "TJC3224K028_011", "long": "TJC 2.8\" Enhanced 320x240",},
        0xdb7befc1: {"short": "TJC4024K032_011", "long": "TJC 3.2\" Enhanced 400x240",},
        0x04096270: {"short": "TJC4832K035_011", "long": "TJC 3.5\" Enhanced 480x240",},
        0x7c1bccd9: {"short": "TJC4827K043_011", "long": "TJC 4.3\" Enhanced 480x270",},
        0x319f988b: {"short": "TJC8048K050_011", "long": "TJC 5.0\" Enhanced 480x240",},
        0xbe2d1fa4: {"short": "TJC8048K070_011", "long": "TJC 7.0\" Enhanced 480x270",},
        0xf52fdc1d: {"short": "TJC4827X343_011", "long": "TJC 4.3\" X3-Series 480x270",},
        0xb8ab884f: {"short": "TJC8048X350_011", "long": "TJC 5.0\" X3-Series 800x480",},
        0x37190f60: {"short": "TJC8048X370_011", "long": "TJC 7.0\" X3-Series 800x480",},
        0xa7ff9055: {"short": "TJC1060X3A1_011", "long": "TJC 10.0\" X3-Series 1024x600",},
        0x51841ccd: {"short": "TJC4827X543_011", "long": "TJC 4.3\" X5-Series 480x270",},
        0x1c00489f: {"short": "TJC8048X550_011", "long": "TJC 5.0\" X5-Series 800x480",},
        0x93b2cfb0: {"short": "TJC8048X570_011", "long": "TJC 7.0\" X5-Series 800x480",},
        0x8da106d5: {"short": "TJC1060X570_011", "long": "TJC 7.0\" X5-Series 1024x600",},
        0x03545085: {"short": "TJC1060X5A1_011", "long": "TJC 10.0\" X5-Series 1024x600",},
        0xf59677a7: {"short":  "NX3224T024_011", "long": "Nextion 2.4\" Basic 320x240",},
        0x1443383b: {"short":  "NX3224T028_011", "long": "Nextion 2.8\" Basic 320x240",},
        0x6d494da9: {"short":  "NX4024T032_011", "long": "Nextion 3.2\" Basic 400x240",},
        0xb23bc018: {"short":  "NX4832T035_011", "long": "Nextion 3.5\" Basic 480x240",},
        0xca296eb1: {"short":  "NX4827T043_011", "long": "Nextion 4.3\" Basic 480x270",},
        0x87ad3ae3: {"short":  "NX8048T050_011", "long": "Nextion 5.0\" Basic 480x240",},
        0x081fbdcc: {"short":  "NX8048T070_011", "long": "Nextion 7.0\" Basic 480x270",},
        0x5c7e9301: {"short":  "NX3224K024_011", "long": "Nextion 2.4\" Enhanced 320x240",},
        0xbdabdc9d: {"short":  "NX3224K028_011", "long": "Nextion 2.8\" Enhanced 320x240",},
        0xc4a1a90f: {"short":  "NX4024K032_011", "long": "Nextion 3.2\" Enhanced 400x240",},
        0x1bd324be: {"short":  "NX4832K035_011", "long": "Nextion 3.5\" Enhanced 480x240",},
        0x63c18a17: {"short":  "NX4827K043_011", "long": "Nextion 4.3\" Enhanced 480x270",},
        0x2e45de45: {"short":  "NX8048K050_011", "long": "Nextion 5.0\" Enhanced 480x240",},
        0xa1f7596a: {"short":  "NX8048K070_011", "long": "Nextion 7.0\" Enhanced 480x270",},
        0x181169da: {"short":  "NX4827P043_011", "long": "Nextion 4.3\" Intelligent 480x270",},
        0x55953d88: {"short":  "NX8048P050_011", "long": "Nextion 5.0\" Intelligent 800x480",},
        0xda27baa7: {"short":  "NX8048P070_011", "long": "Nextion 7.0\" Intelligent 800x480",},
        0x4fc44fa0: {"short":  "NX1060P101_011", "long": "Nextion 10.0\" Intelligent 1024x600",},
    }

    def __init__(self, HMIFilePath):
        objectList = list()
        with open(HMIFilePath, "rb") as HMIFile:
            self.raw = HMIFile.read()
        self.header = HMIHeader(self.raw)
        self.pages = []
        # Parse "main.HMI" first, then the other structures
        for obj in self.header.content:
            if obj.name == "main.HMI":
                self.modelCRC = struct.unpack_from("<I", obj._raw, obj.start + 16)[0]
                if self.modelCRC not in self._models:
                    raise Exception("Unknown model ID: " + hex(self.modelCRC))
                self.modelName = self._models[self.modelCRC]["short"]
                self.modelDesc = self._models[self.modelCRC]["long"]
                # Strip the NX/TJC prefix, take the T/K/P/X letter at the 4th place and unify P/X to P.
                self.modelSeries = self.modelName.replace("NX", "").replace("TJC", "")[4].replace("X", "P")
        for obj in self.header.content:
            if obj.isPage():
                self.pages.append(Page(self.raw, obj.start, obj.size, self.modelSeries))
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
if __name__ == '__main__':
    desc = """Get a readable text version of a Nextion HMI file. 
              Developped by Max Zuidberg, licensed under MPL-2.0"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-i", metavar="hmiFile", type=str, required=True,
                        help="Path to the HMI source file")
    parser.add_argument("-o", metavar="textFolder", type=str, required=True,
                        help="Path to the folder for the generated text files.")
    parser.add_argument("-e", metavar="extension", type=str, required=False, default=".txt",
                        help="Optional Extension that is added to the text files (default: \".txt\")")
    parser.add_argument("-a", type=bool, required=False, const=True, default=False, nargs="?",
                        help="Add this flag to include all properties. By default, only \"non-visual\" properties are included (no .x, .y, font, ...)")

    args = parser.parse_args()

    hmiFile = args.i
    hmiTextFolder = args.o
    hmiTextFileExt = args.e

    hmi = HMI(hmiFile)

    if not hmiTextFileExt.startswith("."):
        hmiTextFileExt = "." + hmiTextFileExt

    if not os.path.exists(hmiTextFolder):
        os.mkdir(hmiTextFolder)

    totalCodeLines = 0
    tusloc = 0
    for i,page in enumerate(hmi.pages):
        with open(os.path.join(hmiTextFolder, page.self.objname + hmiTextFileExt), "w") as f:
            pageText, sloc, uniqueSloc = page.self.text(emptyLinesLimit=1)
            totalCodeLines += sloc
            tusloc += uniqueSloc
            print(page.self.__repr__())
            print(" ", sloc, "Lines of source code")
            print(" ", uniqueSloc, "Unique lines of source code")
            f.write(pageText)
    print("Total:", totalCodeLines, "Lines of source code")
    print("      ", tusloc, "Unique lines of source code")

    print("done")
