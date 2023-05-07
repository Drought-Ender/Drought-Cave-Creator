import settings

strip_int = lambda x : int(''.join(filter(str.isdigit, x)))

strip_float = lambda x : float(''.join(filter(str.isdecimal, x)))


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


class TekiBase:
    def __init__(self, name:str, fill:int, weight:int, falltype:int, has_item:bool, item:str):
        self.name = name
        self.has_item = has_item
        self.item = item
        self.fill = fill
        self.weight = weight
        self.falltype = falltype

    def get_weight(self) -> int:
        return self.weight
    
    def get_fill(self) -> int:
        return self.fill

class Teki(TekiBase):
    def __init__(self, name:str, fill:int, weight:int, falltype:int, has_item:bool, item:str, spawn:int):
        super().__init__(name, fill, weight, falltype, has_item, item)
        self.spawn = spawn
    
    
        

class TekiInfo:
    def __init__(self, teki_count:int, tekis:list[Teki]):
        self.teki_count = teki_count
        self.tekis = tekis
    
    def get_objs(self) -> list[Teki]:
        return self.tekis


class Treasure:
    def __init__(self, name:str, fill:int, weight:int):
        self.name = name
        self.fill = fill
        self.weight = weight

    def get_weight(self) -> int:
        return self.weight

    def get_fill(self) -> int:
        return self.fill


class ItemInfo:
    def __init__(self, item_count:int, items:list[Treasure]):
        self.item_count = item_count
        self.items = items
    
    def get_objs(self) -> list[Treasure]:
        return self.items


class Gate:
    def __init__(self, name:str, life:float, weight:int):
        self.name = name
        self.life = life
        self.weight = weight

    def get_weight(self) -> int:
        return self.weight

    def get_fill(self) -> int:
        return 0

class GateInfo:
    def __init__(self, gate_count:int, gates:list[Gate]):
        self.gate_count = gate_count
        self.gates = gates

    def get_objs(self) -> list[Gate]:
        return self.gates

class Cap(TekiBase):
    def __init__(self, cap_type:int, name:str, fill:int, weight:int, falltype:int, has_item:bool, item:str, dont_dupe:bool):
        self.cap_type = cap_type
        super().__init__(name, fill, weight, falltype, has_item, item)
        self.dont_dupe = dont_dupe

class CapInfo:
    def __init__(self, cap_count:int, caps:list[Cap]):
        self.cap_count = cap_count
        self.caps = caps

    def get_objs(self) -> list[Cap]:
        return self.caps



class Floor:
    def __init__(self, floorinfo:Floorinfo, tekiinfo:TekiInfo, iteminfo:ItemInfo, gateinfo:GateInfo, capinfo=None):
        self.floorinfo = floorinfo
        self.tekiinfo = tekiinfo
        self.iteminfo = iteminfo
        self.gateinfo = gateinfo
        self.capinfo = capinfo

class CaveInfo:
    def __init__(self, floor_count:int, floors:list[Floor]):
        self.floor_count = floor_count
        self.floors = floors

#

id32 = '$0123456789abcdefghijklmnopqrstuvwxyz_-ABCDEFGHIJKLMNOPQRSTUVWXYZ.'


def next_string(line:str, subindex = 0):
    while subindex < len(line) and line[subindex] not in id32:
        subindex += 1
    if subindex >= len(line):
        return None, subindex
    start = subindex
    while subindex < len(line) and line[subindex] in id32:
        subindex += 1
    return line[start:subindex], subindex + 1

def next_string_list(lines:list[str], subindex = 0, subsubindex = 0):
    val, subval = next_string(lines[subindex], subsubindex)
    while not val:
        subindex += 1
        val, subval = next_string(lines[subindex])
    return val, subindex, subval

def readID32(cave:list[str], start):
    valueDict = {}
    line, val = readID32Line(cave[start])
    while line != "_eof":
        valueDict[line] = val
        start += 1
        line, val = readID32Line(cave[start])
    return valueDict, start


def readID32Line(line:str):
    subindex = 0
    while subindex < len(line) and line[subindex].lower() not in id32:
        subindex += 1
    _id = line[subindex:subindex+4]
    typeof, place = next_string(line, subindex+4)
    second, place = next_string(line, place)
    return _id, second

def read_cave(cave):
    cave = [line.decode("shift-jis") for line in cave]
    floor_dict, start_index = readID32(cave, 0)
    floor_num = floor_dict["c000"]
    floor_num, start_index = next_int_list(cave, start_index)

    floors = []

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
            start_index += 1
    except Exception as e:
        raise BaseException(f"{e} while reading object at line {start_index}")
    return CaveInfo(floor_num, floors)

def next_int_list(lines:list[str], subindex = 0, subsubindex = 0):
    val:int = next_int(lines[subindex], subsubindex)
    while val == None:
        subindex += 1
        val:int = next_int(lines[subindex])
    return val, subindex + 1

def next_int(line, subindex = 0):
    while subindex < len(line) and not line[subindex].isdigit():
        subindex += 1

    
    
    if subindex >= len(line):
        return None
    return strip_int(line[subindex:])

def next_float_list(lines:list[str], subindex = 0, subsubindex = 0):
    val:float = next_float(lines[subindex], subsubindex)
    while val is None:
        subindex += 1
        val:float = next_float(lines[subindex])
    return val, subindex + 1

def next_float(line, subindex = 0):
    while subindex < len(line) and not line[subindex].isdecimal():
        subindex += 1

    if subindex >= len(line):
        return None
    return strip_float(line[subindex:])


def pad_close(cave, index):
    while str(cave[index]).strip(" \\nrtb'\r\n") != "}":
        index += 1
    return index + 1

def read_floor(cave, start_index):
    parms, start_index = readID32(cave, start_index)
    return read_floorinfo_parms(parms), start_index

def read_floorinfo_parms(floor_read:dict):
    floorinfo = get_unread_floorinfo()
    if "f000" in floor_read:
        floorinfo.floor_start = int(floor_read["f000"])
    if "f001" in floor_read:
        floorinfo.floor_end = int(floor_read["f001"])
    if "f002" in floor_read:
        floorinfo.teki_num = int(floor_read["f002"])
    if "f003" in floor_read:
        floorinfo.item_num = int(floor_read["f003"])
    if "f004" in floor_read:
        floorinfo.gate_num = int(floor_read["f004"])
    if "f005" in floor_read:
        floorinfo.room_num = int(floor_read["f005"])
    if "f006" in floor_read:
        floorinfo.corridor_chance = float(floor_read["f006"])
    if "f007" in floor_read:
        floorinfo.geyser = bool(int(floor_read["f007"]))
    if "f008" in floor_read:
        floorinfo.unit_file = floor_read["f008"]
    if "f009" in floor_read:
        floorinfo.lighting_file = floor_read["f009"]
    if "f00A" in floor_read:
        floorinfo.skybox = floor_read["f00A"]
    if "f010" in floor_read:
        floorinfo.is_clogged = bool(int(floor_read["f010"]))
    if "f011" in floor_read:
        floorinfo.echo = int(floor_read["f011"])
    if "f012" in floor_read:
        floorinfo.music = int(floor_read["f012"])
    if "f013" in floor_read:
        floorinfo.plane = bool(int(floor_read["f013"]))
    if "f014" in floor_read:
        floorinfo.dead_end = int(floor_read["f014"])
    if "f015" in floor_read:
        floorinfo.use_cap = bool(int(floor_read["f015"]))
    if "f016" in floor_read:
        floorinfo.timer = float(floor_read["f016"])
    if "f017" in floor_read:
        floorinfo.seesaw = bool(int(floor_read["f017"]))
    return floorinfo


def read_teki(cave, start_index):
    teki_num, start_index = next_int_list(cave, start_index)
    teki = []
    for i in range(teki_num):
        name, start_index, subval = next_string_list(cave, start_index)
        count, start_index = next_int_list(cave, start_index, subval)
        spawn, start_index = next_int_list(cave, start_index)
        tekibase = read_tekibase([name, str(count)], spawn)
        teki.append(
            Teki(tekibase.name, tekibase.fill, tekibase.weight, tekibase.falltype, tekibase.has_item, tekibase.item, spawn)
        )
    return TekiInfo(teki_num, teki), start_index + 1


def read_tekibase(tekistr, spawn=0):
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

    num = next_int(tekistr[1])
    if spawn == 6:
        fill = num
        weight = 0
    else:
        fill = num // 10
        weight = num % 10

    return TekiBase(teki, fill, weight, fall_type, has_item, item)

def read_item(cave, start_index):
    item_num, start_index = next_int_list(cave, start_index)
    items = []
    for i in range(item_num):
        name, start_index, subval = next_string_list(cave, start_index)
        count, start_index = next_int_list(cave, start_index, subval)
        treasure = read_treasurebase([name, str(count)])
        items.append(
            treasure
        )
    return ItemInfo(item_num, items), start_index + 1

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
    gate_num, start_index = next_int_list(cave, start_index)
    gates = []
    for i in range(gate_num):
        name, start_index, subval = next_string_list(cave, start_index)
        life, start_index = next_float_list(cave, start_index, subval)
        weight, start_index = next_int_list(cave, start_index)
        gates.append(
            Gate(name, life, weight)
        )
    return GateInfo(gate_num, gates), start_index + 1

def read_cap(cave, start_index):
    cap_num, start_index = next_int_list(cave, start_index)
    caps = []
    for i in range(cap_num):
        captype, start_index = next_int_list(cave, start_index)
        name, start_index, subval = next_string_list(cave, start_index)
        weight, start_index = next_int_list(cave, start_index, subval)
        count, start_index = next_int_list(cave, start_index)
        
        tekibase = read_tekibase([name, str(count)], 0)
        caps.append(
            Cap(captype, tekibase.name, tekibase.fill, tekibase.weight, tekibase.falltype, tekibase.has_item, tekibase.item, bool(captype))
        )
    return CapInfo(cap_num, caps), start_index + 1

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
    return Floor(get_default_floorinfo(), TekiInfo(0, []), ItemInfo(0, []), GateInfo(0, []), CapInfo(0, []))

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
        if floor.floorinfo.skybox == "":
            floor.floorinfo.skybox = "none"
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
            f"\t{{f008}} -1 {floor.floorinfo.unit_file} \t# Units File\n",
            f"\t{{f009}} -1 {floor.floorinfo.lighting_file} \t# Lighting File\n",
            f"\t{{f00A}} -1 {floor.floorinfo.skybox} \t# Skybox\n",
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
            fall = f"${teki.falltype}" if teki.falltype > 0 else ""
            item = f"_{teki.item}" if teki.has_item else ""
            weight = teki.weight
            if teki.spawn == 6:
                weight = ""
            export_string.append(f"\t{fall}{teki.name}{item} {teki.fill}{weight} \t# weight\n")
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
                fall = f"${cap.falltype}" if cap.falltype > 0 else ""
                item = f"_{cap.item}" if cap.has_item else ""
                export_string.append(f"\t{cap.cap_type} \t# captype\n")
                export_string.append(f"\t{fall}{cap.name}{item} {cap.fill}{cap.weight} \t# weight\n")
                export_string.append(f"\t{int(cap.dont_dupe)} \t# type\n")
            export_string.append("}\n")
    return export_string

