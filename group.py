from abc import ABC, abstractmethod
from enum import Enum

class GROUP_TYPE(Enum):
  """Type of a group."""
  LOBBY = 0
  ROOM = 1

class GAME_MODE(Enum):
  """Heroes of Might and Magic 5 game mode."""
  STANDARD = 0
  RATING = 1
  DUEL = 2
  DUEL2 = 3

class Group(ABC):
  """Base class for lobbies and rooms."""
  def __init__(self, id: int, name: str, master: str, game_mode: GAME_MODE):
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
    self.event_id = game_mode.value

  @abstractmethod
  def to_list(self) -> list:
    """Returns the structure as ordered list."""
    pass

class Lobby(Group):
  """Top-level group (server list)."""
  def __init__(self, id: int, name: str, master: str, game_mode: GAME_MODE):
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

class Room(Group):
  """Represents a group of players waiting for a game to begin."""
  def __init__(self, id: int, name: str, master: str, game_mode: GAME_MODE):
    super().__init__(id, name, master, game_mode)
    self.group_type = GROUP_TYPE.ROOM.value
    self.nb_players = 0
    self.max_players = 8
    self.nb_visitors = 0
    self.max_visitors = 8
    self.game_version = ""
    self.gs_version = ""
    self.ip_addr = ""
    self.alt_ip_addr = ""

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
      str(self.max_players),
      str(self.nb_players),
      str(self.max_visitors),
      str(self.nb_visitors),
      self.game_version,
      self.gs_version,
      self.ip_addr,
      self.alt_ip_addr
    ]
