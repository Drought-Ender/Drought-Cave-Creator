import CaveLibrary.cave as Cave
import copy


def optimise_cave(in_caveInfo:Cave.CaveInfo) -> Cave.CaveInfo:
    caveInfo:Cave.CaveInfo = copy.deepcopy(in_caveInfo)
    for floor in caveInfo.floors:
        optimise_floor(floor)
    return caveInfo

def optimise_capInfo(capinfo:Cave.CapInfo):
    capinfo.caps = [cap for cap in capinfo.caps if not is_fillable_pointless(cap)]
    capinfo.cap_count = len(capinfo.caps)

def optimise_gateInfo(gateInfo:Cave.GateInfo):
    gateInfo.gates = [gate for gate in gateInfo.gates if not is_weighable_pointless(gate)]

    gate_stats:dict[str, dict[float, int]] = {}
    for gate in gateInfo.gates:
        gate_stats[gate.name][gate.life] += gate.weight
    
    new_gates = [Cave.Gate(name, life, weight) for name, gate_data in gate_stats.items() for life, weight in gate_data.items()]

    gateInfo.gates = new_gates
    gateInfo.gate_count = len(gateInfo.gates)

def optimise_itemInfo(itemInfo:Cave.ItemInfo):
    itemInfo.items = [item for item in itemInfo.items if not is_fillable_pointless(item)]
    itemInfo.item_count = len(itemInfo.items)

def is_teki_pointless(teki:Cave.Teki):
    if (teki.spawn == 3):
         return True
    if is_fillable_pointless(teki):
        return True


def is_fillable_pointless(obj):
    return is_weighable_pointless(obj) and obj.fill == 0

def is_weighable_pointless(obj):
    return obj.weight == 0

def optimise_tekiInfo(tekiInfo:Cave.TekiInfo):
    tekiInfo.tekis = [teki for teki in tekiInfo.tekis if not is_teki_pointless(teki)]
    tekiInfo.teki_count = len(tekiInfo.tekis)

def has_wraith(tekiInfo:Cave.TekiInfo, capInfo:Cave.CapInfo):
    for teki in tekiInfo.tekis + capInfo.caps:
        if teki.name == "BlackMan":
            return True
    return False

def has_no_weight(info):
    for obj in info.get_objs():
        if obj.get_weight() > 0:
            return False
    return True

def get_total_obj_count(info):
    return sum(obj.get_fill() for obj in info.get_objs())

def set_info_max(info, maxi):
    obj_count = get_total_obj_count(info)
    return obj_count if has_no_weight(info) or maxi < obj_count else maxi 

        

def optimise_floor(floor:Cave.Floor):
    optimise_tekiInfo(floor.tekiinfo)
    optimise_itemInfo(floor.iteminfo)
    optimise_gateInfo(floor.gateinfo)
    optimise_capInfo(floor.capinfo)

    # No Cap Enemies? No capinfo
    if floor.floorinfo.use_cap and set_info_max(floor.capinfo, 0) == 0:
        floor.floorinfo.use_cap = False
        floor.capinfo.caps = []
    
    
    floor.floorinfo.teki_num, floor.floorinfo.item_num, floor.floorinfo.gate_num = \
    [set_info_max(*args) for args in ((floor.tekiinfo, floor.floorinfo.teki_num), (floor.iteminfo, floor.floorinfo.item_num), (floor.gateinfo, floor.floorinfo.gate_num))]

    floor.floorinfo.timer = floor.floorinfo.timer if has_wraith(floor.tekiinfo, floor.capinfo) else 0.0
        


    
    
    



    

    