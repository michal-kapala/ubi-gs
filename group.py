from abc import ABC, abstractmethod
from enum import Enum
from typing import TypedDict

class LSM(Enum):
  """Lobby Service Mask"""
  LSM_PRIVATE = 1
  """Group is password-protected."""
  LSM_NEEDMASTER = 2
  """Group needs a master."""
  LSM_ETERNEL = 4
  """Group is not deleted when empty."""
  LSM_ACTIVE = 8
  """Group is active."""
  LSM_OPEN = 0x10
  """Group is open."""
  LSM_STARTABLE = 0x20
  """Group can start a game."""
  LSM_GROUPINFO = 0x40
  """Request group info on join."""
  LSM_GROUPMEMBERS = 0x80
  """Request group members on join."""
  LSM_CHILDGROUPINFO = 0x100
  """Request child group info on join."""
  LSM_ALLINFO = LSM_GROUPINFO | LSM_GROUPMEMBERS | LSM_CHILDGROUPINFO
  """Request all group infos on join."""
  LSM_CREATE_SUBLOBBY = 0x200
  """Group can have child lobbies."""
  LSM_OPEN_WHEN_ACTIVE = 0x400
  """Group stays open while active."""
  LSM_SCORES_SUBMISSION = 0x800
  """Group allows score submissions."""
  LSM_MATCHACTIVE = 0x1000
  """Group has a match in progress."""
  LSM_REGISTERSERVER = 0x2000
  """Undocumented flag."""
  LSM_DEDICATEDSERVER = 0x4000
  """Group represents a dedicated server."""
  LSM_JOINRULE = 0x8000
  """Group access is protected with a rule (passport)."""
  LSM_CREATERULE = 0x10000
  """Group creation us protected with a rule (passport)."""

class GROUP_TYPE(Enum):
  """Type of a group."""
  LOBBY = 0
  ROOM_DIRECTPLAY_CLIENTSERVER = 1
  ROOM_DIRECTPLAY_P2P = 2
  ROOM_HYBRID = 3
  ROOM_HYBRID_REGSERVER = 4
  ROOM_UBI_CLIENTHOST = 5
  ROOM_UBI_CLIENTHOST_REGSERVER = 6
  ROOM_UBI_P2P = 7
  ROOM_UBI_GAMESERVER = 8
  ROOM_UBI_GAMESERVER_REGSERVER = 9
  ROOM_REGSERVER = 10
  """REGISTER_SERVER"""

class PLAYER_STATUS(Enum):
  """Player's online status."""
  PS_SILENT = 1
  """The player is limited (doesn't have access to chat, page, etc)."""
  PS_GAMECONNECTED = 2
  """The player is playing a game."""
  PS_GAMEREADY = 4
  """Not implemented."""
  PS_MATCHREADY = 8
  """Not implemented."""
  PS_MATCHPLAYING = 16
  """The player is playing a match."""

class ROOM_UPDATE_FLAGS(Enum):
  """Main flags used by `LOBBY_MSG.GROUP_CONFIG_UPDATE_RES` requests."""
  OPEN = 2
  """Room is open for joins. Only sent for DS."""
  SCORE_SUBMISSION = 4
  """Room submits scores. Only sent for DS."""
  MAX_PLAYERS = 8
  """Max players number update."""
  MAX_VISITORS = 0x10
  """Max visitors number update."""
  PASSWORD = 0x20
  """Room password update."""
  GROUP_INFO = 0x40
  """Room group info data update."""
  DEDICATED_SERVER = 0x200
  """Room host is a dedicated server."""
  DS_FLAGS = OPEN | SCORE_SUBMISSION | DEDICATED_SERVER
  """Dedicated server flags update. See `DS_ROOM_UPDATE_FLAGS`."""
  ALT_GROUP_INFO = 0x400
  """Alternative group info data update."""

class DS_ROOM_UPDATE_FLAGS(Enum):
  """Dedicated server flags used by `LOBBY_MSG.GROUP_CONFIG_UPDATE_RES` requests."""
  OPEN = 0x10
  """Room is open for joins."""
  SCORE_SUBMISSION = 0x800
  """Room submits scores."""
  DEDICATED_SERVER = 0x4000
  """Room host is a dedicated server."""

class Group(ABC):
  """Base class for lobbies and rooms."""
  def __init__(self, id: int, name: str, master: str, event_id: int):
    self.group_type = GROUP_TYPE.LOBBY.value
    self.group_name = name
    self.group_id = id
    self.lobby_sv_id = 1
    self.parent_id = 0
    self.config = 0
    self.group_level = 1
    self.master = master
    self.allowed_games = ""
    self.games = ""
    self.info = b''
    self.event_id = event_id

  @abstractmethod
  def to_list(self) -> list:
    """Returns the structure as ordered list."""
    pass

class Lobby(Group):
  """Top-level group (server list)."""
  def __init__(self, id: int, name: str, master: str, game_mode: int):
    super().__init__(id, name, master, game_mode)
    self.group_type = GROUP_TYPE.LOBBY.value
    self.nb_members = 0
    self.max_members = 8

  def to_list(self):
    return [
      str(self.group_type),
      self.group_name,
      str(self.group_id),
      str(self.lobby_sv_id),
      str(self.parent_id),
      str(self.config),
      str(self.group_level),
      self.master,
      self.allowed_games,
      self.games,
      self.info,
      str(self.event_id),
      str(self.max_members),
      str(self.nb_members)
    ]

class RoomCreateData(TypedDict):
  """Received via `LOBBY_MSG.CREATE_ROOM` requests. Integer types are stored as strings, need conversion if used by the server."""
  parent_id: int
  room_name: str
  game_title: str
  room_type: int
  max_players: int
  max_visitors: int
  group_info: bytes
  room_password: str
  game_version: str
  gs_version: str
  alt_group_info: bytes

class Room(Group):
  """Represents a group of players."""
  def __init__(self, room_data: RoomCreateData, room_id: int, master: str):
    room_name = room_data["room_name"]
    event_id = room_data["event_id"]
    super().__init__(room_id, room_name, master, event_id)
    self.group_type = GROUP_TYPE.ROOM_UBI_P2P.value # homm5
    self.game_title = room_data["game_title"]
    self.parent_id = room_data["parent_id"]
    self.max_players = room_data["max_players"]
    self.max_visitors = room_data["max_visitors"]
    self.group_info = room_data["group_info"]
    self.room_password = room_data["room_password"]
    self.game_version = room_data["game_version"]
    self.gs_version = room_data["gs_version"]
    self.alt_group_info = room_data["alt_group_info"]
    self.nb_players = 0
    self.nb_visitors = 0
    self.ip_addr = "127.0.0.1"
    self.alt_ip_addr = ""
    self.config = LSM.LSM_ALLINFO.value
    if self.room_password != "":
      self.config |= LSM.LSM_PRIVATE.value

  def to_list(self):
    """Serialization to `RoomInfo` struct."""
    return [
      str(self.group_type),
      self.group_name,
      str(self.group_id),
      str(self.lobby_sv_id),
      str(self.parent_id),
      str(self.config),
      str(self.group_level),
      self.master,
      self.allowed_games,
      self.games,
      self.group_info,
      str(self.event_id),
      str(self.max_players),
      str(self.nb_players),
      str(self.max_visitors),
      str(self.nb_visitors),
      self.game_version,
      self.gs_version,
      self.ip_addr,
      self.alt_ip_addr
    ]

class MemberInfo:
  """Group member info."""
  def __init__(self, username: str, group_id: str):
    self.username = username
    self.is_visitor = False
    self.ip_addr = "127.0.0.1"
    self.alt_ip_addr = "127.0.0.1"
    self.player_data = b''
    self.group_ids = [group_id]
    self.ping = -1
    self.status = int(PLAYER_STATUS.PS_SILENT.value)

  def to_list(self):
    """Serialization to `MemberJoined` struct."""
    return [
      self.username,
      "1" if self.is_visitor else "0",
      self.ip_addr,
      self.alt_ip_addr,
      self.player_data,
      self.group_ids,
      str(self.ping),
      str(self.status)
    ]
