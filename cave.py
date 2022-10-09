import settings

def strip_int(string:str):
    try:
        i = int(''.join(filter(str.isdigit, string)))
    except:
        raise BaseException(f"required value '{string}' is not an int")
    return i

class CaveInfo:
    def __init__(self, floor_count=0, floors=None):
        if floors is None:
            floors = []
        self.floor_count = floor_count
        self.floors = floors



class Floorinfo:
    def __init__(self):
        self.floor_start = None
        self.floor_end = None
        self.teki_num = None
        self.item_num = None
        self.gate_num = None
        self.room_num = 0
        self.corridor_chance = 0.0
        self.geyser = False
        self.unit_file = "units.txt"
        self.lighting_file = "light.ini"
        self.skybox = "none"
        self.is_clogged = False
        self.echo = 0
        self.music = 0
        self.plane = False
        self.dead_end = 0
        self.use_cap = True
        self.timer = 0.0
        self.seesaw = False

class TekiInfo:
    def __init__(self, teki_count=0, tekis=None):
        if tekis is None:
            tekis = []
        self.teki_count = teki_count
        self.tekis = tekis

class TekiBase:
    def __init__(self, name="Chappy", fill=0, weight=0, falltype=0, has_item=False, item="ahiru"):
        self.name = name
        self.has_item = has_item
        self.item = item
        self.fill = fill
        self.weight = weight
        self.falltype = falltype

class Teki:
    def __init__(self, teki=TekiBase(), spawn=0):
        self.teki = teki
        self.spawn = spawn

class Treasure:
    def __init__(self, name="ahiru", fill=0, weight=0):
        self.name = name
        self.fill = fill
        self.weight = weight

class ItemInfo:
    def __init__(self, item_count=0, items=None):
        if items is None:
            items = []
        self.item_count = item_count
        self.items = items


class Gate:
    def __init__(self, name="gate", life=1000.0, weight=0):
        self.name = name
        self.life = life
        self.weight = weight

class GateInfo:
    def __init__(self, gate_count=0, gates=None):
        if gates is None:
            gates = []
        self.gate_count = gate_count
        self.gates = gates

class Cap:
    def __init__(self, cap_type=0, teki=TekiBase(), dont_dupe=True):
        self.cap_type = cap_type
        self.teki = teki
        self.dont_dupe = dont_dupe

class CapInfo:
    def __init__(self, cap_count=0, caps=None):
        if caps is None:
            caps = []
        self.cap_count = cap_count
        self.caps = caps

class Floor:
    def __init__(self, floorinfo=Floorinfo(), tekiinfo=TekiInfo(), iteminfo=ItemInfo(), gateinfo=GateInfo()):
        self.floorinfo = floorinfo
        self.tekiinfo = tekiinfo
        self.iteminfo = iteminfo
        self.gateinfo = gateinfo
        self.capinfo = None

#

def read_cave(cave):
    floor_num = str(cave[2])
    comment_start = floor_num.index("#")
    floor_num = floor_num[4:comment_start].strip()
    floor_num = floor_num.split(" ")
    
    floor_num = int(floor_num[2])
    
    floors = []

    start_index = 4
    try:
        for i in range(floor_num):
            floorinfo, start_index = read_floor(cave, start_index)
            tekiinfo, start_index = read_teki(cave, start_index)
            iteminfo, start_index = read_item(cave, start_index)
            gateinfo, start_index = read_gate(cave, start_index)
            floors.append(Floor(floorinfo, tekiinfo, iteminfo, gateinfo))
            if floorinfo.use_cap:
                capinfo, start_index = read_cap(cave, start_index)
                floors[i].capinfo = capinfo
    except Exception as e:
        raise BaseException(f"{e} while reading object at line {start_index}")
    return CaveInfo(floor_num, floors)
        
        


def pad_close(cave, index):
    while str(cave[index]).strip(" \\nrtb'\r\n") != "}":
        index += 1
    return index + 1

def read_floor(cave, start_index):
    floor_read = []
    start_index += 3
    for i, line in enumerate(cave[start_index:]):
        line = str(line)
        
        comment_start = line.index("#") if "#" in line else -1
        stripped_line = line[4:comment_start].strip()
        floor_read.append(stripped_line.split(" "))
        if floor_read[-1][0] == "{_eof}":
            return read_floorinfo_parms(floor_read), pad_close(cave, start_index + i)

def read_floorinfo_parms(floor_read):
    floorinfo = get_unread_floorinfo()
    for parm in floor_read: # how do I switch case help
        if parm[0] == "{f000}":
            floorinfo.floor_start = strip_int(parm[2])
        if parm[0] == "{f001}":
            floorinfo.floor_end = strip_int(parm[2])
        if parm[0] == "{f002}":
            floorinfo.teki_num = strip_int(parm[2])
        if parm[0] == "{f003}":
            floorinfo.item_num = strip_int(parm[2])
        if parm[0] == "{f004}":
            floorinfo.gate_num = strip_int(parm[2])
        if parm[0] == "{f005}":
            floorinfo.room_num = strip_int(parm[2])
        if parm[0] == "{f006}":
            floorinfo.corridor_chance = float(parm[2])
        if parm[0] == "{f007}":
            floorinfo.geyser = parm[2] == "1"
        if parm[0] == "{f008}":
            floorinfo.unit_file = parm[2]
        if parm[0] == "{f009}":
            floorinfo.lighting_file = parm[2]
        if parm[0] == "{f00A}":
            floorinfo.skybox = parm[2]
        if parm[0] == "{f010}":
            floorinfo.is_clogged = parm[2] == "1"
        if parm[0] == "{f011}":
            floorinfo.echo = strip_int(parm[2])
        if parm[0] == "{f012}":
            floorinfo.music = strip_int(parm[2])
        if parm[0] == "{f013}":
            floorinfo.plane = parm[2] == "1"
        if parm[0] == "{f014}":
            floorinfo.dead_end = strip_int(parm[2])
        if parm[0] == "{f015}":
            floorinfo.use_cap = parm[2] == "1"
        if parm[0] == "{f016}":
            floorinfo.timer = float(parm[2])
        if parm[0] == "{f017}":
            floorinfo.seesaw = parm[2] == "1"
    return floorinfo


def read_teki(cave, start_index):
    start_index += 2
    teki_num = str(cave[start_index])
    comment_start = teki_num.index("#") if "#" in teki_num else -1
    teki_num = teki_num[4:comment_start].strip(" \\trnb")
    teki_num = int(teki_num)
    if teki_num == 0:
        return TekiInfo(0, []), pad_close(cave, start_index)
    teki = []
    start_index += 1
    for i, line in enumerate(cave[start_index:]):
        line = str(line)
        if i % 2 == 0:
            comment_start = line.index("#") if "#" in line else -1
            teki_read = line[4:comment_start].strip(" \\")
            teki_read = teki_read.split(" ")
        else:
            comment_start = line.index("#") if "#" in line else -1
            weight_read = line[4:comment_start].strip(" \\trnb")
            weight_read = weight_read.split(" ")
            teki.append(Teki(read_tekibase(teki_read), strip_int(weight_read[0])))
        if i == teki_num * 2:
            return TekiInfo(teki_num, teki), pad_close(cave, start_index + i)


def read_tekibase(tekistr):
    num = tekistr[1].strip("\\rnt")
    if len(str(num)) == 1:
        fill = strip_int(str(num)[0])
        weight = 0
    else:
        fill = strip_int(str(num)[0:-1])
        weight = strip_int(num[-1])
    i = 0
    fall_type = 0
    if tekistr[0][0] == "$":
        if tekistr[0][1] in ("1", "2", "3", "4", "5"):
            fall_type = strip_int(tekistr[0][1])
            i = 2
        else:
            i = 1
            fall_type = 1
    for t in settings.settings.teki_dict:
        if (str(tekistr[0][i:]).find(t + "_") == 0) or (len(t) == len(str(tekistr[0][i:])) and str(tekistr[0][i:]).lower().find(t.lower()) == 0):
            teki = t
            break
    item = "ahiru"
    has_item = False
    if len(tekistr[0][i:]) > len(teki):
        has_item = True
        i += len(teki)
        i += 1
        item = tekistr[0][i:]
    return TekiBase(teki, fill, weight, fall_type, has_item, item)

def read_item(cave, start_index):
    item = []
    start_index += 2
    item_num = str(cave[start_index])
    comment_start = item_num.index("#") if "#" in item_num else -1
    item_num = item_num[4:comment_start].strip(" \\trnb\t\r\b")
    item_num = strip_int(item_num)
    if item_num == 0:
        return ItemInfo(0, []), pad_close(cave, start_index)
    start_index += 1
    for i, line in enumerate(cave[start_index:]):
        line = str(line)
        comment_start = line.index("#") if "#" in line else -1
        treasure_read = line[4:comment_start].strip()
        treasure_read = treasure_read.split(" ")
        item.append(read_treasurebase(treasure_read))
        if i == item_num - 1:
            return ItemInfo(item_num, item), pad_close(cave, start_index + i)

def read_treasurebase(treasure_read):
    num = treasure_read[1].strip("\\rnt")
    if len(str(num)) == 1:
        fill = strip_int(str(num)[0])
        weight = 0
    else:
        fill = strip_int(str(num)[0:-1])
        weight = strip_int(num[-1])

    return Treasure(treasure_read[0], fill, weight)

def read_gate(cave, start_index):
    start_index += 2
    gate_count = str(cave[start_index])
    comment_start = gate_count.index("#") if "#" in gate_count else -1
    gate_count = gate_count[4:comment_start].strip(" \\trnb")
    gate_count = int(gate_count)

    if gate_count == 0:
        return GateInfo(0, []), pad_close(cave, start_index)

    gate = []
    start_index += 1
    for i, line in enumerate(cave[start_index:]):
        line = str(line)
        if i % 2 == 0:
            comment_start = line.index("#") if "#" in line else -1
            gate_read = line[4:comment_start].strip()
            gate_read = gate_read.split(" ")
        else:
            comment_start = line.index("#") if "#" in line else -1
            weight_read = line[4:comment_start].strip(" \\trnb")
            gate.append(Gate(gate_read[0], float(gate_read[1].strip("\\rnt")), strip_int(weight_read[-1])))
        if i == gate_count * 2 - 1:
            return GateInfo(gate_count, gate), pad_close(cave, start_index + i)

def read_cap(cave, start_index):
    start_index += 2
    cap_count = str(cave[start_index])
    comment_start = cap_count.index("#") if "#" in cap_count else -1
    cap_count = cap_count[4:comment_start].strip(" \\trnb")
    cap_count = int(cap_count)
    if cap_count == 0:
        return CapInfo(0, []), pad_close(cave, start_index)
    cap = []
    start_index += 1
    for i, line in enumerate(cave[start_index:]):
        line = str(line)
        if i % 3 == 0:
            comment_start = line.index("#") if "#" in line else -1
            captype_read = line[4:comment_start].strip(" \\trnb")
        elif i % 3 == 1:
            comment_start = line.index("#") if "#" in line else -1
            cap_read = line[4:comment_start].strip()
            cap_read = cap_read.split(" ")
        else:
            comment_start = line.index("#") if "#" in line else -1
            type_read = line[4:comment_start].strip(" \\trnb")
            cap.append(Cap(strip_int(captype_read), read_tekibase(cap_read), type_read == "1"))
        if i == cap_count * 3 - 1:
            return CapInfo(cap_count, cap), pad_close(cave, start_index + i)

def get_default_floorinfo():
    default_floor = Floorinfo()
    default_floor.corridor_chance = 0.0
    default_floor.dead_end = 0
    default_floor.echo = 0
    default_floor.floor_end = 0
    default_floor.floor_start = 0
    default_floor.geyser = False
    default_floor.gate_num = 0
    default_floor.is_clogged = False
    default_floor.lighting_file = "light.ini"
    default_floor.item_num = 0
    default_floor.teki_num = 0
    default_floor.music = 0
    default_floor.plane = False
    default_floor.room_num = 0
    default_floor.seesaw = False
    default_floor.use_cap = True
    default_floor.timer = 0.0
    default_floor.skybox = "none"
    default_floor.unit_file = "units.txt"
    return default_floor

def get_unread_floorinfo():
    default_floor = Floorinfo()
    default_floor.corridor_chance = 0.0
    default_floor.dead_end = 0
    default_floor.echo = 0
    default_floor.floor_end = 0
    default_floor.floor_start = 0
    default_floor.geyser = False
    default_floor.gate_num = 0
    default_floor.is_clogged = False
    default_floor.lighting_file = ""
    default_floor.item_num = 0
    default_floor.teki_num = 0
    default_floor.music = 0
    default_floor.plane = False
    default_floor.room_num = 0
    default_floor.seesaw = False
    default_floor.use_cap = False
    default_floor.timer = 0.0
    default_floor.skybox = ""
    default_floor.unit_file = ""
    return default_floor

def get_default_floor():
    default_floor = Floor(get_default_floorinfo(), TekiInfo(), ItemInfo(), GateInfo())
    default_floor.capinfo = CapInfo()
    return default_floor

DEFAULT_CAVEINFO = CaveInfo(1, [get_default_floor()])

def export_cave(caveinfo:CaveInfo):
    export_string = ["# Caveinfo - Made with Drought Ender's Cave Creator\n"]
    export_string.append("{\n")
    export_string.append(f"\t{{c000}} 4 {caveinfo.floor_count} \t# Floor Count\n")
    export_string.append("\t{_eof} \n")
    export_string.append("}\n")
    for i, floor in enumerate(caveinfo.floors):
        if i == caveinfo.floor_count:
            break
        if i == 0:
            export_string.append(f"{caveinfo.floor_count} # FloorInfo\n")
        else:
            export_string.append("# FloorInfo\n")
        export_string += ["{\n",
        f"\t{{f000}} 4 {floor.floorinfo.floor_start} \t# Floor Start\n",
            f"\t{{f001}} 4 {floor.floorinfo.floor_end} \t# Floor End\n",
            f"\t{{f002}} 4 {floor.floorinfo.teki_num} \t# Teki Spawns\n",
            f"\t{{f003}} 4 {floor.floorinfo.item_num} \t# Treasure Spawns\n",
            f"\t{{f004}} 4 {floor.floorinfo.gate_num} \t# Gate Spawns\n",
            f"\t{{f014}} 4 {floor.floorinfo.dead_end} \t# Dead End Percent\n",
            f"\t{{f005}} 4 {floor.floorinfo.room_num} \t# Rooms Placed\n",
            f"\t{{f006}} 4 {floor.floorinfo.corridor_chance:.6f} \t# Corridor Chance\n",
            f"\t{{f007}} 4 {int(floor.floorinfo.geyser)} \t# Place Geyser\n",
            f"\t{{f008}} 4 {floor.floorinfo.unit_file} \t# Units File\n",
            f"\t{{f009}} 4 {floor.floorinfo.lighting_file} \t# Lighting File\n",
            f"\t{{f00A}} 4 {floor.floorinfo.skybox} \t# Skybox\n",
            f"\t{{f010}} 4 {int(floor.floorinfo.is_clogged)} \t# Clog Hole\n",
            f"\t{{f011}} 4 {floor.floorinfo.echo} \t# Echo Strength\n",
            f"\t{{f012}} 4 {floor.floorinfo.music} \t# Music Type\n",
            f"\t{{f013}} 4 {int(floor.floorinfo.plane)} \t# Skybox Plane\n",
            f"\t{{f015}} 4 {int(floor.floorinfo.use_cap)} \t# Use Capinfo\n",
            f"\t{{f016}} 4 {floor.floorinfo.timer:.6f} \t# Waterwraith Timer\n",
            f"\t{{f017}} 4 {int(floor.floorinfo.seesaw)} \t# Spawn Seesaw\n"
            "\t{_eof} \n", "}\n"]
        
        export_string.append("# TekiInfo\n")
        export_string.append("{\n")
        export_string.append(f"\t{floor.tekiinfo.teki_count} \t# num\n")
        for t, teki in enumerate(floor.tekiinfo.tekis):
            if t == floor.tekiinfo.teki_count:
                break
            fall = f"${teki.teki.falltype}" if teki.teki.falltype > 0 else ""
            item = f"_{teki.teki.item}" if teki.teki.has_item else ""
            print(teki.teki.name)
            export_string.append(f"\t{fall}{teki.teki.name}{item} {teki.teki.fill}{teki.teki.weight} \t# weight\n")
            export_string.append(f"\t{teki.spawn} \t# type\n")

        export_string.append("}\n")
        export_string.append("# Iteminfo\n")
        export_string.append("{\n")
        export_string.append(f"\t{floor.iteminfo.item_count} \t# num\n")
        for t, item in enumerate(floor.iteminfo.items):
            if t == floor.iteminfo.item_count:
                break
            export_string.append(f"\t{item.name} {item.fill}{item.weight} \t# weight\n")

        export_string.append("}\n")
        export_string.append("# Gateinfo\n")
        export_string.append("{\n")
        export_string.append(f"\t{floor.gateinfo.gate_count} \t# num\n")
        for t, gate in enumerate(floor.gateinfo.gates):
            if t == floor.gateinfo.gate_count:
                break
            export_string.append(f"\t{gate.name} {gate.life:.2f} \t# life\n")
            export_string.append(f"\t{gate.weight} \t# weight\n")
        export_string.append("}\n")
        if floor.floorinfo.use_cap:
            export_string.append("# Capinfo\n")
            export_string.append("{\n")
            export_string.append(f"\t{floor.capinfo.cap_count} \t# num\n")
            for t, cap in enumerate(floor.capinfo.caps):
                if t == floor.capinfo.cap_count:
                    break
                fall = f"${cap.teki.falltype}" if cap.teki.falltype > 0 else ""
                item = f"_{cap.teki.item}" if cap.teki.has_item else ""
                export_string.append(f"\t{cap.cap_type} \t# captype\n")
                export_string.append(f"\t{fall}{cap.teki.name}{item} {cap.teki.fill}{cap.teki.weight} \t# weight\n")
                export_string.append(f"\t{int(cap.dont_dupe)} \t# type\n")
            export_string.append("}\n")
    return export_string
        
        

