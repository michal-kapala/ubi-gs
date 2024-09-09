from enum import Enum

ENDPOINTS = {
  "router": ('localhost', 7777),
  "irc": ('localhost', 7779),
  "cdkey": ('localhost', 7780),
  "nat": ('localhost', 7781),
  "router_wm": ('localhost', 7782),
  "pers_proxy": ('localhost', 7783),
  "pers_proxy_wm": ('localhost', 7784),
  "lobby": ('localhost', 7785),
  "ladder_proxy": ('localhost', 7786),
  "ladder_proxy_wm": ('localhost', 7787)
}
"""Service endpoints for the Game Service network."""

class PROXY_MODULE(Enum):
  """Proxy server IDs for proxy modules."""
  PERSISTENT_DATA = 1
  LADDER_QUERY = 2
  REMOTE_ALGORITHM = 3
  CLAN_SERVICE = 4

class GAME_MODE(Enum):
  """Heroes of Might and Magic 5 game mode."""
  STANDARD = 0
  RATING = 1
  DUEL = 2
  DUEL2 = 3
  """Same as `DUEL`."""
