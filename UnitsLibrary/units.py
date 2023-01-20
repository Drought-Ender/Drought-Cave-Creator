from math import dist



class DoorLink:
    def __init__(self, dist_:float, id_:int, flag:int):
        self.dist = dist_
        self.id = id_
        self.flag = flag

class DoorPos:
    def __init__(self, dir_:int, offs:int, index:int):
        self.dir = dir_
        self.offs = offs
        self.index = index

    def to_xy(self, size):
        if self.dir == 0:
            return Size2i(size - self.dir, 0)
        if self.dir == 1:
            return Size2i(0, self.dir)
        if self.dir == 2:
            return Size2i(self.dir, size)
        return Size2i(size, size - self.dir)

class Door:
    def __init__(self, index:int, position:DoorPos, links:list[DoorLink]):
        self.index = index
        self.position = position
        self.links = links

class Size2i:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y
    def __tuple__(self):
        return (self.x, self.y)


class CaveUnit:
    def __init__(self, ver:int, name:str, size:Size2i, room_type:int, flags:list[int], doors:list[Door]):
        self.ver = ver
        self.name = name
        self.size = size
        self.type = room_type
        self.flags = flags
        self.doors = doors

    def dist(self, index1, index2):
        door_a = self.doors[index1]
        door_b = self.doors[index2]
        size = self.size
        
        a_pos = door_a.position.to_xy(size)
        b_pos = door_b.position.to_xy(size)
        return dist(tuple(a_pos), tuple(b_pos)) * 150



class UnitsFile:
    def __init__(self, units:list[CaveUnit]):
        self.units = units


def read_comment_line(line, get_type, split=True):
    line = str(line)
    comment_start = line.find("#")
    line = line[4:comment_start].strip(" '\\\t\r\nt")
    if split:
        line = line.split(" ")
        return get_type(line[0])
    return get_type(line)

def pad_open(units, index):
    while str(units[index]).strip(" \\nrtb'\r\n") != "{":
        index += 1
    return index + 1

def read_link(link):
    dist_, id_, tekiflag = read_comment_line(link, str, False).split()
    return DoorLink(float(dist_), int(id_), int(tekiflag))

def read_doors(start, units_file):
    index = read_comment_line(units_file[start], int)
    pos = DoorPos(*[int(x) for x in read_comment_line(units_file[start + 1], str, False).split()])
    num_links = read_comment_line(units_file[start + 2], int)
    links = [read_link(units_file[start + 3 + i]) for i in range(num_links)]
    return start + 3 + num_links, Door(index, pos, links)

def read_caveunit(units_file, start):
    start = pad_open(units_file, start)
    ver = read_comment_line(units_file[start], int)
    name = read_comment_line(units_file[start + 1], str)
    size = Size2i(*[int(x) for x in (read_comment_line(str(units_file[start + 2]), str, False).strip(" '\\\t\n\rtnrb#").split(" "))])
    room_type = read_comment_line(units_file[start + 3], int)
    room_flags = [int(x) for x in (read_comment_line(str(units_file[start + 4]), str, False).strip(" '\\\t\n\rtnrb#").split(" "))]
    num_doors = read_comment_line(units_file[start + 5], int)
    doors = []
    start += 6
    for _ in range(num_doors):
        start, door = read_doors(start, units_file)
        doors.append(door)
    return start + 1, CaveUnit(ver, name, size, room_type, room_flags, doors)

def read_unitstxt(units_file):
    unit_num = str(units_file[5])
    comment_start = unit_num.find("#")
    unit_num = unit_num[2:comment_start].strip()
    unit_num = unit_num.split(" ")
    unit_num = int(unit_num[0])
    start = 6
    units = []
    for _ in range(unit_num):
        start, unit = read_caveunit(units_file, start)
        units.append(unit)
    return UnitsFile(units)

def export_link(link:DoorLink):
    return f"\t{link.dist:.6f} {link.id} {link.flag} \t# dist/door-id/tekiflag\n"

def export_door(door:Door):
    return [
        f"\t{door.index} \t# index\n",
        f"\t{door.position.dir} {door.position.offs} {door.position.index} \t # dir/offs/wpindex\n",
        f"\t{len(door.links)} \t# door links\n"
    ] + [export_link(link) for link in door.links]

def export_unit(unit:CaveUnit):
    return [f"# {unit.name}\n",
            "{\n",
            f"\t{unit.ver} \t# version\n",
            f"\t{unit.name} \t# folername\n",
            f"\t{unit.size.x} {unit.size.y} \t# dX/dZ ; cell size\n",
            f"\t{unit.type} \t# room type\n",
            f"\t{unit.flags[0]} {unit.flags[1]} \t# room Flags\n",
            f"\t{len(unit.doors)} \t# num doors\n"
        ] + [text for door in unit.doors for text in export_door(door)] + ["}\n"]

def export_file(units_:UnitsFile):
    return [
        "#\n",
        "#\n",
        "#\tunits definition file - Made with Drought's Cave Creator\n",
        "#\n",
        "#\n"
        f"{len(units_.units)} \t # number of units\n"] + [text for unit in units_.units for text in export_unit(unit)]

DEFAULT_UNITS = UnitsFile([])

