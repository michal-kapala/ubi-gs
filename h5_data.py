from enum import Enum
from ctypes import c_int32, c_uint32
from group import Room
from utils import read_u32, read_as_u32_list, read_u16, write_u32, write_u32_list, write_u16

class H5_STREAM_TYPE(Enum):
  """Main file stream type for serialized buffers; names assumed."""
  STRUCTURE = 0
  """Empty."""
  COMPRESSED_DATA = 1
  """Contains serialized data, optionally compressed with zlib."""
  RAW_DATA = 2
  """Empty."""
  METADATA = 3
  """Unused."""
  SERIALIZATION_MODE = 4
  """Contains pointer search serialization mode."""
  LOOKUP_TABLE = 5
  """Empty."""

class H5_Stream:
  """File stream/substream (structure field) for serialized buffers."""
  def __init__(self, buf: bytes = None):
    if buf is None:
      self.id = -1
      self.size = -1
      self.size_4b = False
      self.data = bytes()
    else:
      self.read(buf)

  def read(self, buf: bytes):
    """Returns nb of bytes read."""
    self.id = int(buf[0])
    # 4-byte size
    if int(buf[1]) & 1 == 1:
      self.size_4b = True
      self.size = read_u32(buf[1:]) >> 1
      if len(buf) < self.size + 5:
        raise ValueError("Stream's declared size exceeds the buffer size.")
      self.data = buf[5:self.size + 5]
    # 1-byte size
    else:
      self.size_4b = False
      self.size = int(buf[1]) >> 1
      if len(buf) < self.size + 2:
        raise ValueError("Stream's declared size exceeds the buffer size.")
      self.data = buf[2:self.size + 2]

  def write(self):
    """Returns a serialized buffer."""
    buf = bytearray([self.id])
    if self.size_4b or self.size > 127:
      buf.extend(write_u32((self.size << 1) | 1))
    else:
      buf.append(self.size << 1)
    buf.extend(self.data)
    return bytes(buf)

  def __len__(self):
    return (5 if self.size_4b else 2) + self.size

class H5_PlayerInfo:
  def __init__(self, buf: bytes = None):
    if buf is None:
      self.username = ""
      """idx = 2"""
      self.ext_ip = ""
      """idx = 3; external (public) IPv4"""
      self.local_port = 0
      """idx = 4; local (private) port"""
      self.local_ip = ""
      """idx = 4; local (private) IPv4"""
      self.int38 = 0
      """idx = 5; unknown value"""
    else:
      # parse buffer
      pos = 0
            
      field = H5_Stream(buf)
      cur_idx = 2
      if field.id == cur_idx and field.size > 0:
        self.username = field.data.decode("utf-8")
      else:
        raise ValueError(f"PlayerInfo: missing/invalid field - Username ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 3
      if field.id == cur_idx and field.size == 18:
        self.ext_ip = H5_Serializer.read_ipv4(field.data, False)
      else:
        raise ValueError(f"PlayerInfo: missing/invalid field - ExtIP ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 4
      if field.id == cur_idx:
        self.local_port, self.local_ip = H5_PlayerInfo.read_port_ipv4(field.data)
      else:
        raise ValueError(f"PlayerInfo: missing/invalid field - LocalPortIP ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 5
      if field.id == cur_idx and field.size == 4:
        self.int38 = read_u32(field.data)
      else:
        raise ValueError(f"PlayerInfo: missing/invalid field - Int38 ({cur_idx})")
      pos += len(field)

  @staticmethod
  def read_port_ipv4(buf: bytes):
    """Reads port and IPv4 address; compare with `read_ipv4`"""
    # port - idx 2
    field = H5_Stream(buf)
    if field.id == 2 and field.size == 2:
      port = read_u16(field.data)
    else:
      raise ValueError(f"PlayerInfo: missing/invalid field -  (3)")
    # ip - idx 3
    field = H5_Stream(buf[len(field):])
    if field.id == 3 and field.size == 16:
      pt1 = read_u32(field.data)
      pt2 = read_u32(field.data[4:])
      pt3 = read_u32(field.data[8:])
      pt4 = read_u32(field.data[12:])
      ip = f"{pt1}.{pt2}.{pt3}.{pt4}"
    else:
      raise ValueError(f"PlayerInfo: missing/invalid field -  (3)")
    return port, ip

  @staticmethod
  def write_port_ipv4(port: int, ip: str):
    """Writes port and IPv4 address; compare with `write_ipv4`"""
    buf = bytearray()
    field = H5_Stream()

    field.id = 2
    field.data = write_u16(port)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 3
    nbs = ip.split(".")
    if len(nbs) != 4:
      raise ValueError(f"PlayerInfo: invalid LocalIP ({field.id}), serialization failed")
    ip_buf = bytearray()
    ip_buf.extend(write_u32(int(nbs[0])))
    ip_buf.extend(write_u32(int(nbs[1])))
    ip_buf.extend(write_u32(int(nbs[2])))
    ip_buf.extend(write_u32(int(nbs[3])))
    field.data = ip_buf
    field.size = len(field.data)
    buf.extend(field.write())
    return bytes(buf)

  def serialize(self):
    """Returns a serialized buffer."""
    buf = bytearray()
    field = H5_Stream()

    field.id = 2
    field.data = self.username.encode("utf-8")
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 3
    field.data = H5_Serializer.write_ipv4(self.ext_ip, False)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 4
    field.data = H5_PlayerInfo.write_port_ipv4(self.local_port, self.local_ip)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 5
    field.data = write_u32(self.int38)
    field.size = len(field.data)
    buf.extend(field.write())
    return bytes(buf)

class H5_RoomInfo:
  """Data from `group.Room.group_info` buffer (HoMM5)."""
  def __init__(self, buf: bytes = None):
    if buf is None:
      self.group_id: int = -1
      """idx = 2"""
      self.lobby_srv_id: int = -1
      """idx = 3"""
      self.host_ip: str = "0.0.0.0"
      """idx = 4"""
      self.host_logic_init: bool = False
      """idx = 6"""
      self.group_name: str = ""
      """idx = 7"""
      self.password: str = ""
      """idx = 8"""
      self.is_pwd_protected: bool = False
      """idx = 9"""
      self.ghost_mode: bool = False
      """idx = 10"""
      self.quick_combat: bool = False
      """idx = 11"""
      self.fast_combat_turns: bool = False
      """idx = 12"""
      self.time_limit: int = 0
      """idx = 13"""
      self.difficulty_id: int = 0
      """idx = 14"""
      self.map_desc: str = ""
      """idx = 15; map descriptor path (`AdvMapDesc`)"""
      self.teams: list[int] = []
      """idx = 19"""
      self.max_players: int = 0
      """idx = 20"""
      self.map_size: int = 0
      """idx = 21"""
      self.player_infos: list[H5_PlayerInfo] = []
      """idx = 22"""
      self.game_version: int = 0
      """idx = 23"""
      self.is_saved: bool = False
      """idx = 24"""
      self.some_ip: str = ""
      """idx = 25"""
      self.ubi_send_results_wait: bool = False
      """idx = 26"""
      self.options: dict[str, tuple[int, str]] = {}
      """idx = 27"""
      self.is_arena: bool = False
      """idx = 28"""
      self.host_checksum: int = 0
      """idx = 29"""
      self.adventure_type: int = 0
      """idx = 30"""
      self.map_desc_tag: str = ""
      """idx = 31"""
      self.map_goal: str = ""
      """idx = 32"""
      self.arena_map_name: str = ""
      """idx = 33"""
      self.int104: int = 0
      """idx = 37"""
      self.int108: int = 0
      """idx = 38"""
      self.combat_turn_speed: int = 0
      """idx = 39"""
      self.flag110: bool = False
      """idx = 40"""
    else:
      # parse buffer
      pos = 0
      
      field = H5_Stream(buf)
      cur_idx = 2
      if field.id == cur_idx and field.size == 4:
        self.group_id = c_int32(read_u32(field.data)).value
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - GroupID ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 3
      if field.id == cur_idx and field.size == 4:
        self.lobby_srv_id = c_int32(read_u32(field.data)).value
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - LobbySrvID ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 4
      if field.id == cur_idx and field.size == 18:
        self.host_ip = H5_Serializer.read_ipv4(field.data, True)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - host IP ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 6
      if field.id == cur_idx and field.size == 1:
        self.host_logic_init = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - bHostLogicInitialized ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 7
      if field.id == cur_idx and field.size > 0:
        self.group_name = field.data.decode("utf-16-le")
      elif field.size == 0:
        self.group_name = ""
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - GroupName ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 8
      if field.id == cur_idx and field.size > 0:
        self.password = field.data.decode("utf-16-le")
      elif field.size == 0:
        self.password = ""
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Password ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 9
      if field.id == cur_idx and field.size == 1:
        self.is_pwd_protected = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - IsPasswordProtected ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 10
      if field.id == cur_idx and field.size == 1:
        self.ghost_mode = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - GhostMode ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 11
      if field.id == cur_idx and field.size == 1:
        self.quick_combat = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - QuickCombat ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 12
      if field.id == cur_idx and field.size == 1:
        self.fast_combat_turns = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - FastCombatTurns ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 13
      if field.id == cur_idx and field.size == 4:
        self.time_limit = c_int32(read_u32(field.data)).value
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - TimeLimit ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 14
      if field.id == cur_idx and field.size == 4:
        self.difficulty_id = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - DifficultyID ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 15
      if field.id == cur_idx:
        self.map_desc = H5_RoomInfo.read_nested_string(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - MapDescriptor ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 19
      if field.id == cur_idx:
        self.teams = H5_RoomInfo.read_uints(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Teams ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 20
      if field.id == cur_idx and field.size == 4:
        self.max_players = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - MaxPlayers ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 21
      if field.id == cur_idx and field.size == 4:
        self.map_size = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - MapSize ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 22
      if field.id == cur_idx:
        self.player_infos = H5_RoomInfo.read_player_infos(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 23
      if field.id == cur_idx and field.size == 4:
        self.game_version = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - GameVersion ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 24
      if field.id == cur_idx and field.size == 1:
        self.is_saved = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - IsSaved ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 25
      # static 16 bytes, assuming IPv4
      if field.id == cur_idx and field.size == 16:
        pt1 = read_u32(field.data)
        pt2 = read_u32(field.data[4:])
        pt3 = read_u32(field.data[8:])
        pt4 = read_u32(field.data[12:])
        self.some_ip = f"{pt1}.{pt2}.{pt3}.{pt4}"
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - UnknownIP ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 26
      if field.id == cur_idx and field.size == 1:
        self.ubi_send_results_wait = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - SendResults ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 27
      if field.id == cur_idx:
        self.options = H5_RoomInfo.read_options(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Options ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 28
      if field.id == cur_idx and field.size == 1:
        self.is_arena = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - IsArena ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 29
      if field.id == cur_idx and field.size == 4:
        self.host_checksum = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - HostChecksum ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 30
      if field.id == cur_idx and field.size == 4:
        self.adventure_type = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - AdventureType ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 31
      if field.id == cur_idx:
        self.map_desc_tag = H5_RoomInfo.read_nested_string(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - MapDescTag ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 32
      if field.id == cur_idx and field.size > 0:
        self.map_goal = field.data.decode("utf-8")
      elif field.size == 0:
        self.map_goal = ""
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - MapGoal ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 33
      if field.id == cur_idx and field.size > 0:
        self.arena_map_name = field.data.decode("utf-8")
      elif field.size == 0:
        self.arena_map_name = ""
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - ArenaMapName ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 37
      if field.id == cur_idx and field.size == 4:
        self.int104 = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Int104 ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 38
      if field.id == cur_idx and field.size == 4:
        self.int108 = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Int108 ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 39
      if field.id == cur_idx and field.size == 4:
        self.combat_turn_speed = read_u32(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - CombatTurnSpeed ({cur_idx})")
      pos += len(field)

      field = H5_Stream(buf[pos:])
      cur_idx = 40
      if field.id == cur_idx and field.size == 1:
        self.flag110 = field.data[0] != 0
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - Flag110 ({cur_idx})")
      pos += len(field)

  @staticmethod
  def read_nested_string(buf: bytes):
    """Reads a string nested inside idx 2 field."""
    # nested field
    inner_field = H5_Stream(buf)
    idx = 2
    if inner_field.id == idx and inner_field.size > 0:
      return inner_field.data.decode("utf-8")
    elif inner_field.size == 0:
      return ""
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - String.Value ({idx})")

  @staticmethod
  def read_uints(buf: bytes):
    """Reads a list of LE uint32s."""
    # nested field - idx 1 (entry count)
    field = H5_Stream(buf)
    if field.id == 1 and field.size == 4:
      # nested field - idx 2 (entries)
      field = H5_Stream(buf[len(field):])
      if field.id == 2:
        return read_as_u32_list(field.data)
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - IDs.Entries (2)")
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - IDs.Count (1)")

  @staticmethod
  def read_player_infos(buf: bytes):
    """Reads a list of player info structs."""
    # nested field - idx 3 (entry count)
    field = H5_Stream(buf)
    if field.id == 3 and field.size == 4:
      count = read_u32(field.data)
      pos = len(field)
      field = H5_Stream(buf[pos:])
      if field.id == 4 and field.size == 4:
        mode_setting_2 = read_u32(field.data)
        # idx 1 - sizes
        pos += len(field)
        sizes: list[int] = []
        for _ in range(count):
          field = H5_Stream(buf[pos:])
          if field.id == 1 and field.size == 4:
            sizes.append(read_u32(field.data))
          else:
            raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.Count (1)")  
          pos += len(field)

        player_infos: list[H5_PlayerInfo] = []
        for _ in range(count):
          field = H5_Stream(buf[pos:])
          if field.id == 2:
            player_infos.append(H5_PlayerInfo(field.data))
          else:
            raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.PlayerInfo (2)")  
          pos += len(field)
        return player_infos
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.ModeSetting2 (4)")  
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.ModeSetting1 (3)")

  @staticmethod
  def read_options(buf: bytes):
    """Reads options (`map<string, int32, string>`)."""
    # nested field - idx 3 (entry count)
    field = H5_Stream(buf)
    if field.id == 3 and field.size == 4:
      count = read_u32(field.data)
      pos = len(field)
      field = H5_Stream(buf[pos:])
      if field.id == 4 and field.size == 4:
        # unknown value, 0xD (13)
        mode_setting_2 = read_u32(field.data)
        # a number of idx 1 key (string) followed by a list of (idx 2 + idx 3) value tuples (int32, utf16 string)
        options: dict[str, tuple[int, str]] = {}
        keys: list[str] = []
        pos += len(field)
        for _ in range(count):
          field = H5_Stream(buf[pos:])
          if field.id == 1:
            keys.append(field.data.decode("utf-8"))
          else:
            raise ValueError(f"RoomInfo: missing/invalid field - Options.Key (1)")
          pos += len(field)
        
        values: list[tuple[int, str]] = []
        for _ in range(count):
          field = H5_Stream(buf[pos:])
          # nested field - idx 2
          if field.id == 2:
            int_value, str_value = H5_RoomInfo.read_option_values(field.data)
          else:
            raise ValueError(f"RoomInfo: missing/invalid field - Options.IntValue (2)")
          values.append((int_value, str_value))
          pos += len(field)

        for idx in range(count):
          options[keys[idx]] = (values[idx][0], values[idx][1])

        return options
      else:
        raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.ModeSetting2 (4)")  
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - PlayerInfos.ModeSetting1 (3)")

  @staticmethod
  def read_option_values(buf: bytes):
    """Reads `<int, str>` value pair; the string value is in UTF-16."""
    pos = 0
    field = H5_Stream(buf)
    if field.id == 2:
      int_value = read_u32(field.data)
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - Options.IntValue (2)")
    pos += len(field)
    field = H5_Stream(buf[pos:])
    if field.id == 3:
      str_value = field.data.decode("utf-16-le")
    else:
      raise ValueError(f"RoomInfo: missing/invalid field - Options.StringValue (3)")
    return int_value, str_value

  @staticmethod
  def write_nested_string(string: str):
    """Writes a string as nested inside idx 2 field."""
    field = H5_Stream()
    field.id = 2
    field.data = string.encode("utf-8")
    field.size = len(field.data)
    return field.write()

  @staticmethod
  def write_uints(lst: list[int]):
    """Writes a list of ints as LE uint32s."""
    buf = bytearray()
    # count - idx 1
    field = H5_Stream()
    field.id = 1
    field.data = write_u32(len(lst))
    field.size = len(field.data)
    buf.extend(field.write())

    # data - idx 2
    field.id = 2
    field.data = write_u32_list(lst)
    field.size = len(field.data)
    buf.extend(field.write())
    return bytes(buf)

  @staticmethod
  def write_player_infos(infos: list[H5_PlayerInfo]):
    """Writes a list of player info structs."""
    buf = bytearray()
    # count - idx 3
    field = H5_Stream()
    field.id = 3
    field.data = write_u32(len(infos))
    field.size = len(field.data)
    buf.extend(field.write())
    # unknown value 13 - idx 4
    field.id = 4
    field.data = write_u32(13)
    field.size = len(field.data)
    buf.extend(field.write())
    data = bytearray()
    some_id = 0
    for info in infos:
      # info entries - idx 2
      field.id = 2
      field.data = info.serialize()
      field.size = len(field.data)
      data.extend(field.write())
      # either ids (starting at 0), positions or zeroes - idx 1
      field.id = 1
      field.data = write_u32(some_id)
      field.size = len(field.data)
      buf.extend(field.write())
      some_id += 1
    
    buf.extend(data)
    return bytes(buf)

  @staticmethod
  def write_options(options: dict[str, tuple[int, str]]):
    """Writes options (`map<string, int32, string>`)."""
    buf = bytearray()
    # count - idx 3
    field = H5_Stream()
    field.id = 3
    field.data = write_u32(len(options))
    field.size = len(field.data)
    buf.extend(field.write())
    # unknown value 13 - idx 4
    field.id = 4
    field.data = write_u32(13)
    field.size = len(field.data)
    buf.extend(field.write())
    data = bytearray()
    for key in options:
      # keys - idx 1
      field.id = 1
      field.data = key.encode("utf-8")
      field.size = len(field.data)
      buf.extend(field.write())
      # values - idx 2
      field.id = 2
      field.data = H5_RoomInfo.write_option_values(options[key])
      field.size = len(field.data)
      data.extend(field.write())

    buf.extend(data)
    return bytes(buf)

  @staticmethod
  def write_option_values(values: tuple[int, str]):
    """Writes `<int, str>` value pair; the string value is in UTF-16."""
    buf = bytearray()
    field = H5_Stream()

    field.id = 2
    field.data = write_u32(values[0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 3
    field.data = values[1].encode("utf-16-le")
    field.size = len(field.data)
    buf.extend(field.write())

    return bytes(buf)
  
  def serialize(self):
    """Returns a serialized buffer."""
    buf = bytearray()
    field = H5_Stream()

    field.id = 2
    field.data = write_u32(c_uint32(self.group_id).value)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 3
    field.data = write_u32(c_uint32(self.lobby_srv_id).value)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 4
    field.data = H5_Serializer.write_ipv4(self.host_ip, True)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 6
    field.data = bytes([1 if self.host_logic_init else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 7
    field.data = self.group_name.encode("utf-16-le")
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 8
    field.data = self.password.encode("utf-16-le")
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 9
    field.data = bytes([1 if self.is_pwd_protected else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 10
    field.data = bytes([1 if self.ghost_mode else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 11
    field.data = bytes([1 if self.quick_combat else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 12
    field.data = bytes([1 if self.fast_combat_turns else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 13
    field.data = write_u32(c_uint32(self.time_limit).value)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 14
    field.data = write_u32(self.difficulty_id)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 15
    field.data = H5_RoomInfo.write_nested_string(self.map_desc)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 19
    field.data = H5_RoomInfo.write_uints(self.teams)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 20
    field.data = write_u32(self.max_players)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 21
    field.data = write_u32(self.map_size)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 22
    field.data = H5_RoomInfo.write_player_infos(self.player_infos)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 23
    field.data = write_u32(self.game_version)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 24
    field.data = bytes([1 if self.is_saved else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 25
    nbs = self.some_ip.split(".")
    if len(nbs) != 4:
      raise ValueError(f"RoomInfo: invalid SomeIP ({field.id}), serialization failed")
    ip_buf = bytearray()
    ip_buf.extend(write_u32(int(nbs[0])))
    ip_buf.extend(write_u32(int(nbs[1])))
    ip_buf.extend(write_u32(int(nbs[2])))
    ip_buf.extend(write_u32(int(nbs[3])))
    field.data = bytes(ip_buf)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 26
    field.data = bytes([1 if self.ubi_send_results_wait else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 27
    field.data = H5_RoomInfo.write_options(self.options)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 28
    field.data = bytes([1 if self.is_arena else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 29
    field.data = write_u32(self.host_checksum)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 30
    field.data = write_u32(self.adventure_type)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 31
    field.data = H5_RoomInfo.write_nested_string(self.map_desc_tag)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 32
    field.data = self.map_goal.encode("utf-8")
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 33
    field.data = self.arena_map_name.encode("utf-8")
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 37
    field.data = write_u32(self.int104)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 38
    field.data = write_u32(self.int108)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 39
    field.data = write_u32(self.combat_turn_speed)
    field.size = len(field.data)
    buf.extend(field.write())

    field.id = 40
    field.data = bytes([1 if self.flag110 else 0])
    field.size = len(field.data)
    buf.extend(field.write())

    return bytes(buf)

class H5_Room:
  """Full room information matchmaking object, includes game-specific data."""
  def __init__(self, room: Room, info: H5_RoomInfo):
    self.gs_room = room
    self.room_info = info

class H5_Serializer:
  """Equivalent to the original `CStructureSaver` serializer (HoMM5)."""
  def __init__(self):
    self.streams: dict[str, H5_Stream] = {}

  def serialize_roominfo(self, room_info: H5_RoomInfo):
    """Serializes `CRoomInfo` structure into a `group.Room.group_info` buffer."""
    # stream 0 - empty
    struct_stream = H5_Stream()
    struct_stream.id = H5_STREAM_TYPE.STRUCTURE.value
    struct_stream.size_4b = False
    struct_stream.size = 0
    
    # stream 1 - room info
    data_stream = H5_Stream()
    data_stream.id = H5_STREAM_TYPE.COMPRESSED_DATA.value
    data_stream.data = room_info.serialize()
    data_stream.size = len(data_stream.data)
    # the limit for 1B size is 127
    data_stream.size_4b = data_stream.size > 127

    # stream 2 - empty
    raw_data_stream = H5_Stream()
    raw_data_stream.id = H5_STREAM_TYPE.RAW_DATA.value
    raw_data_stream.size_4b = False
    raw_data_stream.size = 0

    # stream 4 - serialization mode (4)
    mode_stream = H5_Stream()
    mode_stream.id = H5_STREAM_TYPE.SERIALIZATION_MODE.value
    mode_stream.size_4b = False
    mode_stream.size = 4
    mode_stream.data = write_u32(4)

    # stream 5 - empty
    table_stream = H5_Stream()
    table_stream.id = H5_STREAM_TYPE.LOOKUP_TABLE.value
    table_stream.size_4b = False
    table_stream.size = 0

    self.streams = {
      H5_STREAM_TYPE.STRUCTURE.name: struct_stream,
      H5_STREAM_TYPE.COMPRESSED_DATA.name: data_stream,
      H5_STREAM_TYPE.RAW_DATA.name: raw_data_stream,
      H5_STREAM_TYPE.SERIALIZATION_MODE.name: mode_stream,
      H5_STREAM_TYPE.LOOKUP_TABLE.name: table_stream
    }

    buf = bytearray(self.streams[H5_STREAM_TYPE.SERIALIZATION_MODE.name].write())
    buf.extend(self.streams[H5_STREAM_TYPE.COMPRESSED_DATA.name].write())
    buf.extend(self.streams[H5_STREAM_TYPE.STRUCTURE.name].write())
    buf.extend(self.streams[H5_STREAM_TYPE.RAW_DATA.name].write())
    buf.extend(self.streams[H5_STREAM_TYPE.LOOKUP_TABLE.name].write())
    return bytes(buf)

  def deserialize_roominfo(self, buf: bytes) -> H5_RoomInfo:
    """Reads `CRoomInfo` structure from a serialized `group.Room.group_info` buffer."""
    size = len(buf)
    pos = 0
    # streams
    while (pos < size):
      stream = H5_Stream(buf)
      bts_read = len(stream)
      pos += bts_read
      self.streams[H5_STREAM_TYPE(stream.id).name] = stream
      buf = buf[bts_read:]

    data_stream = self.streams[H5_STREAM_TYPE.COMPRESSED_DATA.name]
    if data_stream is None:
      raise ValueError("Data stream missing in RoomInfo buffer.")

    room_info = H5_RoomInfo(data_stream.data)
    print(room_info.__dict__)
    return room_info

  @staticmethod
  def read_ipv4(buf: bytes, room_info: bool):
    """Reads IPv4 address encoded on 16B. Shared between `RoomInfo` and `PlayerInfo`."""
    # nested field - idx 2
    field = H5_Stream(buf)
    if field.id == 2 and field.size == 16:
      pt1 = read_u32(field.data)
      pt2 = read_u32(field.data[4:])
      pt3 = read_u32(field.data[8:])
      pt4 = read_u32(field.data[12:])
      return f"{pt1}.{pt2}.{pt3}.{pt4}"
    else:
      cl_name = "RoomInfo" if room_info else "PlayerInfo"
      raise ValueError(f"{cl_name}: missing/invalid field - HostIP (2)")

  @staticmethod
  def write_ipv4(ip: str, room_info: bool):
    """Writes IPv4 address encoded on 16B. Shared between `RoomInfo` and `PlayerInfo`."""
    # nested field - idx 2
    field = H5_Stream()
    field.id = 2
    nbs = ip.split(".")
    if len(nbs) != 4:
      cl_name = "RoomInfo" if room_info else "PlayerInfo"
      raise ValueError(f"{cl_name}: invalid IPv4 ({field.id}), serialization failed")
    buf = bytearray()
    buf.extend(write_u32(int(nbs[0])))
    buf.extend(write_u32(int(nbs[1])))
    buf.extend(write_u32(int(nbs[2])))
    buf.extend(write_u32(int(nbs[3])))
    field.data = bytes(buf)
    field.size = len(field.data)
    return field.write()
