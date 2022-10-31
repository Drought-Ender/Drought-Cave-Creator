
from wwlib.fs_helpers import *

from wwlib.data_tables import DataTables

class DZx: # DZR or DZS, same format
  def __init__(self, file_entry):
    self.file_entry = file_entry
    data = self.file_entry.data
    
    num_chunks = read_u32(data, 0)
    
    self.chunks = []
    for chunk_index in range(0, num_chunks):
      offset = 4 + chunk_index*0xC
      chunk = Chunk(self.file_entry)
      chunk.read(offset)
      self.chunks.append(chunk)
  
  def entries_by_type(self, chunk_type):
    entries = []
    for chunk in self.chunks:
      if chunk_type == chunk.chunk_type:
        entries += chunk.entries
    return entries
  
  def entries_by_type_and_layer(self, chunk_type, layer):
    entries = []
    for chunk in self.chunks:
      if chunk_type == chunk.chunk_type and layer == chunk.layer:
        entries += chunk.entries
    return entries
  
  def add_entity(self, chunk_type, layer=None):
    chunk_to_add_entity_to = None
    for chunk in self.chunks:
      if chunk_type == chunk.chunk_type and layer == chunk.layer:
        chunk_to_add_entity_to = chunk
        break
    
    if chunk_to_add_entity_to is None:
      chunk_to_add_entity_to = Chunk(self.file_entry)
      chunk_to_add_entity_to.chunk_type = chunk_type
      chunk_to_add_entity_to.layer = layer
      self.chunks.append(chunk_to_add_entity_to)
    
    entity = chunk_to_add_entity_to.entry_class(self.file_entry)
    chunk_to_add_entity_to.entries.append(entity)
    
    return entity
  
  def remove_entity(self, entity, chunk_type, layer=None):
    assert hasattr(entity, "name")
    
    # Instead of actually removing the entity from the list, simply set its name to the empty string.
    # This will cause the game to not load any actor there, so it's effectively removing it.
    # The benefit of this is that removing an entity from the list shifts down the entity indexes of all entities after it in the list, which has the potential to screw up paths to entities in item_locations.txt and enemy locations.txt.
    entity.name = ""
    entity.save_changes()
    
    # Below is the old code that actually removed the entity from the list.
    #chunk_to_remove_entity_from = None
    #for chunk in self.chunks:
    #  if chunk_type == chunk.chunk_type and layer == chunk.layer:
    #    chunk_to_remove_entity_from = chunk
    #    break
    #
    #if chunk_to_remove_entity_from is None:
    #  raise Exception("Could not find chunk of type %s on layer %s" % (chunk_type, layer))
    #
    #chunk_to_remove_entity_from.entries.remove(entity)
  
  def save_changes(self):
    for chunk in self.chunks:
      # Make sure all chunk entries are fully loaded before trying to save them.
      chunk.read_entries()
    
    data = self.file_entry.data
    data.truncate(0)
    
    offset = 0
    write_u32(data, offset, len(self.chunks))
    offset += 4
    
    for chunk in self.chunks:
      chunk.offset = offset
      chunk.save_changes()
      offset += 0xC
    
    for chunk in self.chunks:
      # Pad the start of each chunk to the nearest 4 bytes.
      align_data_to_nearest(data, 4)
      offset = data_len(data)
      
      chunk.first_entry_offset = offset
      write_u32(data, chunk.offset+8, chunk.first_entry_offset)
      
      for entry in chunk.entries:
        if entry is None:
          raise Exception("Tried to save unknown chunk type: %s" % chunk.chunk_type)
        
        entry.offset = offset
        
        offset += chunk.entry_class.DATA_SIZE
      
      if chunk.fourcc == "RTBL":
        # Assign offsets for RTBL sub entries.
        for rtbl_entry in chunk.entries:
          rtbl_entry.sub_entry.offset = offset
          offset += rtbl_entry.sub_entry.DATA_SIZE
        
        # Assign offsets for RTBL sub entry adjacent rooms.
        for rtbl_entry in chunk.entries:
          rtbl_entry.sub_entry.adjacent_rooms_list_offset = offset
          for adjacent_room in rtbl_entry.sub_entry.adjacent_rooms:
            adjacent_room.offset = offset
            offset += adjacent_room.DATA_SIZE
        
        # Pad the end of the adjacent rooms list to 4 bytes.
        file_size = offset
        padded_file_size = (file_size + 3) & ~3
        padding_size_needed = padded_file_size - file_size
        write_bytes(data, offset, b"\xFF"*padding_size_needed)
        offset += padding_size_needed
      
      for entry in chunk.entries:
        entry.save_changes()
    
    # Pad the length of this file to 0x20 bytes.
    file_size = offset
    padded_file_size = (file_size + 0x1F) & ~0x1F
    padding_size_needed = padded_file_size - file_size
    write_bytes(data, offset, b"\xFF"*padding_size_needed)

class Chunk:
  LAYER_CHAR_TO_LAYER_INDEX = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11}
  
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.chunk_type = None
    self.num_entries = 0
    self.first_entry_offset = None
    
    self._entries = []
    self.layer = None
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.chunk_type = read_str(data, self.offset, 4)
    self.num_entries = read_u32(data, self.offset+4)
    self.first_entry_offset = read_u32(data, self.offset+8)
    
    # Some types of chunks are conditional and only appear on certain layers. The 4th character of their type determines what letter they appear on.
    if self.chunk_type.startswith("TRE") or self.chunk_type.startswith("ACT") or self.chunk_type.startswith("SCO"):
      layer_char = self.chunk_type[3]
      if layer_char in self.LAYER_CHAR_TO_LAYER_INDEX:
        self.layer = self.LAYER_CHAR_TO_LAYER_INDEX[layer_char]
    if self.chunk_type.startswith("TRE"):
      self.chunk_type = "TRES"
    if self.chunk_type.startswith("ACT"):
      self.chunk_type = "ACTR"
    if self.chunk_type.startswith("SCO"):
      self.chunk_type = "SCOB"
    
    # Lazy load entries to avoid loading old-versioned chunks that would crash the program.
    self._entries = None
  
  def save_changes(self):
    data = self.file_entry.data
    
    self.num_entries = len(self.entries)
    
    write_magic_str(data, self.offset, self.fourcc, 4)
    write_u32(data, self.offset+4, self.num_entries)
    write_u32(data, self.offset+8, 0) # Placeholder for first entry offset
  
  @property
  def entry_class(self):
    class_name = self.chunk_type
    if class_name[0].isdigit():
      class_name = "_" + class_name
    return globals().get(class_name, None)
  
  @property
  def fourcc(self):
    fourcc = self.chunk_type
    if self.layer is not None:
      assert 0 <= self.layer <= 11
      fourcc = fourcc[:3]
      fourcc += "%x" % self.layer
    return fourcc
  
  @property
  def entries(self):
    self.read_entries()
    
    return self._entries
  
  @entries.setter
  def entries(self, value):
    self._entries = value
  
  def read_entries(self):
    if self._entries is not None:
      # Already read.
      return
    
    if self.entry_class is None:
      #raise Exception("Unknown chunk type: " + self.chunk_type)
      self._entries = [None]*self.num_entries
      return self._entries
    
    entry_size = self.entry_class.DATA_SIZE
    
    self._entries = []
    for entry_index in range(self.num_entries):
      entry_offset = self.first_entry_offset + entry_index*entry_size
      entry = self.entry_class(self.file_entry)
      entry.read(entry_offset)
      self._entries.append(entry)

class ChunkEntry:
  PARAMS = {}
  IS_ACTOR_CHUNK = False
  
  def __getattr__(self, attr_name):
    if attr_name in ["name"]:
      return super(self.__class__, self).__getattribute__(attr_name)
    
    if attr_name in self.param_fields:
      params_bitfield_name, mask = self.param_fields[attr_name]
      amount_to_shift = self.get_lowest_set_bit(mask)
      return ((getattr(self, params_bitfield_name) & mask) >> amount_to_shift)
    else:
      return super(self.__class__, self).__getattribute__(attr_name)
  
  def __setattr__(self, attr_name, value):
    if attr_name in ["name"]:
      self.__dict__[attr_name] = value
    
    if attr_name in self.param_fields:
      params_bitfield_name, mask = self.param_fields[attr_name]
      amount_to_shift = self.get_lowest_set_bit(mask)
      new_params_value = (getattr(self, params_bitfield_name) & (~mask)) | ((value << amount_to_shift) & mask)
      super().__setattr__(params_bitfield_name, new_params_value)
    else:
      if self.IS_ACTOR_CHUNK and attr_name not in ["offset", "file_entry", "name", "params", "x_pos", "y_pos", "z_pos", "x_rot", "y_rot", "z_rot", "enemy_number", "scale_x", "scale_y", "scale_z", "padding"]:
        raise Exception("Tried to set unknown actor parameter \"%s\" for actor class %s (actor name: %s)" % (attr_name, self.actor_class_name, self.name))
      
      self.__dict__[attr_name] = value
  
  @staticmethod
  def get_lowest_set_bit(integer):
    lowest_set_bit_index = None
    for bit_index in range(32):
      if integer & (1 << bit_index):
        lowest_set_bit_index = bit_index
        break
    if lowest_set_bit_index is None:
      raise Exception("Invalid mask: %08X" % mask)
    return lowest_set_bit_index
  
  @property
  def actor_class_name(self):
    if not self.IS_ACTOR_CHUNK:
      raise Exception("Tried to get the actor class name of an entity in a non-actor DZx chunk")
    
    if self.name not in DataTables.actor_name_to_class_name:
      return None
    
    return DataTables.actor_name_to_class_name[self.name]
  
  @property
  def param_fields(self):
    if self.IS_ACTOR_CHUNK and hasattr(self, "name"):
      if self.name in DataTables.actor_name_to_class_name:
        if self.actor_class_name is None:
          raise Exception("Unknown actor name: \"%s\"" % self.name)
        else:
          return DataTables.actor_parameters[self.actor_class_name]
      else:
        return {}
    else:
      return self.PARAMS

class SCOB(ChunkEntry):
  DATA_SIZE = 0x24
  
  IS_ACTOR_CHUNK = True
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.name = None
    self.params = 0
    self.x_pos = 0
    self.y_pos = 0
    self.z_pos = 0
    self.x_rot = 0
    self.y_rot = 0
    self.z_rot = 0
    self.enemy_number = 0xFFFF
    self.scale_x = 10
    self.scale_y = 10
    self.scale_z = 10
    self.padding = 0xFF
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.name = read_str(data, offset, 8)
    
    self.params = read_u32(data, offset + 8)
    
    self.x_pos = read_float(data, offset + 0x0C)
    self.y_pos = read_float(data, offset + 0x10)
    self.z_pos = read_float(data, offset + 0x14)
    
    self.x_rot = read_u16(data, offset + 0x18)
    self.y_rot = read_u16(data, offset + 0x1A)
    self.z_rot = read_u16(data, offset + 0x1C)
    
    self.enemy_number = read_u16(data, offset + 0x1E)
    
    self.scale_x = read_u8(data, offset + 0x20)
    self.scale_y = read_u8(data, offset + 0x21)
    self.scale_z = read_u8(data, offset + 0x22)
    self.padding = read_u8(data, offset + 0x23)
    
  def save_changes(self):
    data = self.file_entry.data
    
    write_str(data, self.offset, self.name, 8)
    
    write_u32(data, self.offset+0x08, self.params)
    
    write_float(data, self.offset+0x0C, self.x_pos)
    write_float(data, self.offset+0x10, self.y_pos)
    write_float(data, self.offset+0x14, self.z_pos)
    
    write_u16(data, self.offset+0x18, self.x_rot)
    write_u16(data, self.offset+0x1A, self.y_rot)
    write_u16(data, self.offset+0x1C, self.z_rot)
    
    write_u16(data, self.offset+0x1E, self.enemy_number)
    
    write_u8(data, self.offset+0x20, self.scale_x)
    write_u8(data, self.offset+0x21, self.scale_y)
    write_u8(data, self.offset+0x22, self.scale_z)
    write_u8(data, self.offset+0x23, self.padding)

class ACTR(ChunkEntry):
  DATA_SIZE = 0x20
  
  IS_ACTOR_CHUNK = True
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.name = None
    self.params = 0
    self.x_pos = 0
    self.y_pos = 0
    self.z_pos = 0
    self.x_rot = 0
    self.y_rot = 0
    self.z_rot = 0
    self.enemy_number = 0xFFFF
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.name = read_str(data, offset, 8)
    
    self.params = read_u32(data, offset + 8)
    
    self.x_pos = read_float(data, offset + 0x0C)
    self.y_pos = read_float(data, offset + 0x10)
    self.z_pos = read_float(data, offset + 0x14)
    
    self.x_rot = read_u16(data, offset + 0x18)
    self.y_rot = read_u16(data, offset + 0x1A)
    self.z_rot = read_u16(data, offset + 0x1C)
    
    self.enemy_number = read_u16(data, offset + 0x1E)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_str(data, self.offset, self.name, 8)
    
    write_u32(data, self.offset+0x08, self.params)
    
    write_float(data, self.offset+0x0C, self.x_pos)
    write_float(data, self.offset+0x10, self.y_pos)
    write_float(data, self.offset+0x14, self.z_pos)
    
    write_u16(data, self.offset+0x18, self.x_rot)
    write_u16(data, self.offset+0x1A, self.y_rot)
    write_u16(data, self.offset+0x1C, self.z_rot)
    
    write_u16(data, self.offset+0x1E, self.enemy_number)

class TRES(ACTR):
  pass

class PLYR(ACTR):
  def __init__(self, file_entry):
    super(PLYR, self).__init__(file_entry)
    
    self.name = "Link"
    self.unknown_param_4 = 0xFF
    self.evnt_index = 0xFF
    self.unknown_param_5 = 0xFF

class SCLS(ChunkEntry):
  DATA_SIZE = 0xC
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.dest_stage_name = None
    self.spawn_id = 0
    self.room_index = 0
    self.fade_type = 0
    self.padding = 0xFF
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.dest_stage_name = read_str(data, offset, 8)
    self.spawn_id = read_u8(data, offset+8)
    self.room_index = read_u8(data, offset+9)
    self.fade_type = read_u8(data, offset+0xA)
    self.padding = read_u8(data, offset+0xB)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_str(data, self.offset, self.dest_stage_name, 8)
    write_u8(data, self.offset+0x8, self.spawn_id)
    write_u8(data, self.offset+0x9, self.room_index)
    write_u8(data, self.offset+0xA, self.fade_type)
    write_u8(data, self.offset+0xB, self.padding)

class STAG(ChunkEntry):
  DATA_SIZE = 0x14
  
  PARAMS = {
    "is_dungeon": ("params_1", 0x01),
    "stage_id":   ("params_1", 0xFE),
    
    "minimap_type":         ("params_2", 0x0003),
    "unknown_3":            ("params_2", 0x0004),
    "loaded_particle_bank": ("params_2", 0x07F8),
    "unknown_4":            ("params_2", 0xF800),
    
    "default_time_of_day": ("params_3", 0x0000FF00),
    "stage_type":          ("params_3", 0x00070000),
    
    "base_actor_draw_distance": ("params_4", 0x0000FFFF),
  }
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.depth_min = read_float(data, offset)
    self.depth_max = read_float(data, offset+4)
    self.unknown_1 = read_u8(data, offset+8)
    
    self.params_1 = read_u8(data, offset+9)
    self.params_2 = read_u16(data, offset+0xA)
    self.params_3 = read_u32(data, offset+0xC)
    self.params_4 = read_u32(data, offset+0x10)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_float(data, self.offset, self.depth_min)
    write_float(data, self.offset+4, self.depth_max)
    write_u8(data, self.offset+8, self.unknown_1)
    
    write_u8(data, self.offset+9, self.params_1)
    write_u16(data, self.offset+0xA, self.params_2)
    write_u32(data, self.offset+0xC, self.params_3)
    write_u32(data, self.offset+0x10, self.params_4)

class FILI(ChunkEntry):
  DATA_SIZE = 8
  
  PARAMS = {
    "unknown_1":                ("params", 0x0000007F),
    "draw_depth":               ("params", 0x00007F80),
    "unknown_2":                ("params", 0x00038000),
    "wind_type":                ("params", 0x000C0000),
    "is_weather":               ("params", 0x00100000),
    "loaded_particle_bank":     ("params", 0x1FE00000),
    "unknown_3":                ("params", 0x20000000),
    "can_play_song_of_passing": ("params", 0x40000000),
    "unknown_4":                ("params", 0x80000000),
  }
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.params = read_u32(data, offset)
    self.skybox_y_origin = read_float(data, offset+0x04)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_u32(data, self.offset, self.params)
    write_float(data, self.offset+0x04, self.skybox_y_origin)

class SHIP(ChunkEntry):
  DATA_SIZE = 0x10
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.x_pos = read_float(data, offset + 0x00)
    self.y_pos = read_float(data, offset + 0x04)
    self.z_pos = read_float(data, offset + 0x08)
    self.y_rot = read_u16(data, offset + 0x0C)
    self.ship_id = read_u8(data, offset + 0x0E)
    self.unknown = read_u8(data, offset + 0x0F)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_float(data, self.offset+0x00, self.x_pos)
    write_float(data, self.offset+0x04, self.y_pos)
    write_float(data, self.offset+0x08, self.z_pos)
    write_u16(data, self.offset+0x0C, self.y_rot)
    write_u8(data, self.offset+0x0E, self.ship_id)
    write_u8(data, self.offset+0x0F, self.unknown)

class RTBL(ChunkEntry):
  DATA_SIZE = 0x4
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    sub_entry_offset = read_u32(data, offset)
    self.sub_entry = RTBL_SubEntry(self.file_entry)
    self.sub_entry.read(sub_entry_offset)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_u32(data, self.offset, self.sub_entry.offset)
    
    self.sub_entry.save_changes()

class RTBL_SubEntry:
  DATA_SIZE = 0x8
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    num_rooms = read_u8(data, offset)
    self.reverb_amount = read_u8(data, offset+1)
    self.does_time_pass = read_u8(data, offset+2)
    self.unknown = read_u8(data, offset+3)
    
    self.adjacent_rooms_list_offset = read_u32(data, offset+4)
    self.adjacent_rooms = []
    for i in range(num_rooms):
      adjacent_room = RTBL_AdjacentRoom(self.file_entry)
      adjacent_room.read(self.adjacent_rooms_list_offset + i)
      self.adjacent_rooms.append(adjacent_room)
  
  def save_changes(self):
    data = self.file_entry.data
    
    num_rooms = len(self.adjacent_rooms)
    write_u8(data, self.offset, num_rooms)
    write_u8(data, self.offset+1, self.reverb_amount)
    write_u8(data, self.offset+2, self.does_time_pass)
    write_u8(data, self.offset+3, self.unknown)
    
    write_u32(data, self.offset+4, self.adjacent_rooms_list_offset)
    
    for adjacent_room in self.adjacent_rooms:
      adjacent_room.save_changes()

class RTBL_AdjacentRoom:
  DATA_SIZE = 0x1
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    byte = read_u8(data, offset)
    self.should_load_room = ((byte & 0x80) != 0)
    self.unknown = ((byte & 0x40) != 0)
    self.room_index = (byte & 0x3F)
  
  def save_changes(self):
    data = self.file_entry.data
    
    byte = (self.room_index & 0x3F)
    if self.should_load_room:
      byte |= 0x80
    if self.unknown:
      byte |= 0x40
    
    write_u8(data, self.offset, byte)

class RPAT(ChunkEntry):
  DATA_SIZE = 0xC
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.num_points = 0
    self.next_path_index = 0xFFFF
    self.unknown_1 = 0xFF
    self.is_loop = 0
    self.unknown_2 = 0xFF
    self.unknown_3 = 0xFF
    self.first_waypoint_offset = 0
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.num_points = read_u16(data, self.offset+0x00)
    self.next_path_index = read_u16(data, self.offset+0x02)
    self.unknown_1 = read_u8(data, self.offset+0x04)
    self.is_loop = read_u8(data, self.offset+0x05)
    self.unknown_2 = read_u8(data, self.offset+0x06)
    self.unknown_3 = read_u8(data, self.offset+0x07)
    self.first_waypoint_offset = read_u32(data, self.offset+0x08)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_u16(data, self.offset+0x00, self.num_points)
    write_u16(data, self.offset+0x02, self.next_path_index)
    write_u8(data, self.offset+0x04, self.unknown_1)
    write_u8(data, self.offset+0x05, self.is_loop)
    write_u8(data, self.offset+0x06, self.unknown_2)
    write_u8(data, self.offset+0x07, self.unknown_3)
    write_u32(data, self.offset+0x08, self.first_waypoint_offset)

class RPPN(ChunkEntry):
  DATA_SIZE = 0x10
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.unknown_1 = 0xFF
    self.unknown_2 = 0xFF
    self.unknown_3 = 0xFF
    self.action_type = 0xFF
    self.x_pos = 0
    self.y_pos = 0
    self.z_pos = 0
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.unknown_1 = read_u8(data, self.offset+0x00)
    self.unknown_2 = read_u8(data, self.offset+0x01)
    self.unknown_3 = read_u8(data, self.offset+0x02)
    self.action_type = read_u8(data, self.offset+0x03)
    self.x_pos = read_float(data, self.offset+0x04)
    self.y_pos = read_float(data, self.offset+0x08)
    self.z_pos = read_float(data, self.offset+0x0C)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_u8(data, self.offset+0x00, self.unknown_1)
    write_u8(data, self.offset+0x01, self.unknown_2)
    write_u8(data, self.offset+0x02, self.unknown_3)
    write_u8(data, self.offset+0x03, self.action_type)
    write_float(data, self.offset+0x04, self.x_pos)
    write_float(data, self.offset+0x08, self.y_pos)
    write_float(data, self.offset+0x0C, self.z_pos)

class TGOB(ACTR):
  pass

class TGSC(SCOB):
  pass

class DOOR(SCOB):
  pass

class TGDR(SCOB):
  pass

class EVNT(ChunkEntry):
  DATA_SIZE = 0x18
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.unknown_1 = 0xFF
    self.name = None
    self.unknown_2 = 0xFF
    self.unknown_3 = 0xFF
    self.unknown_4 = 0
    self.event_seen_switch_index = 0xFF
    self.room_index = 0xFF
    self.padding = b"\xFF"*3
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.unknown_1 = read_u8(data, offset)
    self.name = read_str(data, offset+1, 0xF)
    self.unknown_2 = read_u8(data, offset+0x10)
    self.unknown_3 = read_u8(data, offset+0x11)
    self.unknown_4 = read_u8(data, offset+0x12)
    self.event_seen_switch_index = read_u8(data, offset+0x13)
    self.room_index = read_u8(data, offset+0x14)
    
    self.padding = read_bytes(data, offset+0x15, 3)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_u8(data, self.offset, self.unknown_1)
    write_str(data, self.offset+1, self.name, 0xF)
    write_u8(data, self.offset+0x10, self.unknown_2)
    write_u8(data, self.offset+0x11, self.unknown_3)
    write_u8(data, self.offset+0x12, self.unknown_4)
    write_u8(data, self.offset+0x13, self.event_seen_switch_index)
    write_u8(data, self.offset+0x14, self.room_index)
    
    write_bytes(data, self.offset+0x15, self.padding)

class _2DMA(ChunkEntry):
  DATA_SIZE = 0x38
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.full_map_image_scale_x = read_float(data, offset)
    self.full_map_image_scale_y = read_float(data, offset+4)
    self.full_map_space_scale_x = read_float(data, offset+8)
    self.full_map_space_scale_y = read_float(data, offset+0xC)
    self.full_map_x_coord = read_float(data, offset+0x10)
    self.full_map_y_coord = read_float(data, offset+0x14)
    
    self.zoomed_map_x_scrolling_1 = read_float(data, offset+0x18)
    self.zoomed_map_y_scrolling_1 = read_float(data, offset+0x1C)
    self.zoomed_map_x_scrolling_2 = read_float(data, offset+0x20)
    self.zoomed_map_y_scrolling_2 = read_float(data, offset+0x24)
    self.zoomed_map_x_coord = read_float(data, offset+0x28)
    self.zoomed_map_y_coord = read_float(data, offset+0x2C)
    self.zoomed_map_scale = read_float(data, offset+0x30)
    
    self.unknown_1 = read_u8(data, offset+0x34)
    self.unknown_2 = read_u8(data, offset+0x35)
    
    sector_coordinates = read_u8(data, offset+0x36)
    self.sector_x =  sector_coordinates & 0x0F
    self.sector_y = (sector_coordinates & 0xF0) >> 4
    if self.sector_x >= 8: # Negative
      self.sector_x = self.sector_x - 16
    if self.sector_y >= 8: # Negative
      self.sector_y = self.sector_y - 16
    
    self.padding = read_u8(data, offset+0x37)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_float(data, self.offset+0x00, self.full_map_image_scale_x)
    write_float(data, self.offset+0x04, self.full_map_image_scale_y)
    write_float(data, self.offset+0x08, self.full_map_space_scale_x)
    write_float(data, self.offset+0x0C, self.full_map_space_scale_y)
    write_float(data, self.offset+0x10, self.full_map_x_coord)
    write_float(data, self.offset+0x14, self.full_map_y_coord)
    
    write_float(data, self.offset+0x18, self.zoomed_map_x_scrolling_1)
    write_float(data, self.offset+0x1C, self.zoomed_map_y_scrolling_1)
    write_float(data, self.offset+0x20, self.zoomed_map_x_scrolling_2)
    write_float(data, self.offset+0x24, self.zoomed_map_y_scrolling_2)
    write_float(data, self.offset+0x28, self.zoomed_map_x_coord)
    write_float(data, self.offset+0x2C, self.zoomed_map_y_coord)
    write_float(data, self.offset+0x30, self.zoomed_map_scale)
    
    write_u8(data, self.offset+0x34, self.unknown_1)
    write_u8(data, self.offset+0x35, self.unknown_2)
    
    sector_coordinates = (self.sector_x & 0xF) | ((self.sector_y & 0xF) << 4)
    write_u8(data, self.offset+0x36, sector_coordinates)
    
    write_u8(data, self.offset+0x37, self.padding)

class MULT(ChunkEntry):
  DATA_SIZE = 0xC
  
  def __init__(self, file_entry):
    self.file_entry = file_entry
    
    self.x_pos = 0.0
    self.z_pos = 0.0
    self.y_rot = 0
    self.room_index = 0
    self.ocean_height = 0
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.x_pos = read_float(data, offset)
    self.z_pos = read_float(data, offset+4)
    self.y_rot = read_u16(data, offset+8)
    self.room_index = read_u8(data, offset+0xA)
    self.ocean_height = read_u8(data, offset+0xB)
    
  def save_changes(self):
    data = self.file_entry.data
    
    write_float(data, self.offset, self.x_pos)
    write_float(data, self.offset+4, self.z_pos)
    write_u16(data, self.offset+8, self.y_rot)
    write_u8(data, self.offset+0xA, self.room_index)
    write_u8(data, self.offset+0xB, self.ocean_height)

class DummyEntry(ChunkEntry):
  def __init__(self, file_entry):
    self.file_entry = file_entry
  
  def read(self, offset):
    self.offset = offset
    data = self.file_entry.data
    
    self.raw_data_bytes = read_bytes(data, self.offset, self.DATA_SIZE)
  
  def save_changes(self):
    data = self.file_entry.data
    
    write_bytes(data, self.offset, self.raw_data_bytes)

class FLOR(DummyEntry):
  DATA_SIZE = 0x14

class LBNK(DummyEntry):
  DATA_SIZE = 0x1

class SOND(DummyEntry):
  DATA_SIZE = 0x1C

class RCAM(DummyEntry):
  DATA_SIZE = 0x14

class RARO(DummyEntry):
  DATA_SIZE = 0x14

class DMAP(DummyEntry):
  DATA_SIZE = 0x10

class EnvR(DummyEntry):
  DATA_SIZE = 0x8

class Colo(DummyEntry):
  DATA_SIZE = 0xC

class Pale(DummyEntry):
  DATA_SIZE = 0x2C

class Virt(DummyEntry):
  DATA_SIZE = 0x24

class LGHT(DummyEntry):
  DATA_SIZE = 0x1C

class LGTV(DummyEntry):
  DATA_SIZE = 0x1C

class MECO(DummyEntry):
  DATA_SIZE = 0x2

class MEMA(DummyEntry):
  DATA_SIZE = 0x4

class PATH(DummyEntry):
  DATA_SIZE = 0xC

class PPNT(DummyEntry):
  DATA_SIZE = 0x10

class CAMR(DummyEntry):
  DATA_SIZE = 0x14

class AROB(DummyEntry):
  DATA_SIZE = 0x14
