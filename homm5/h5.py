from enum import Enum

ENDPOINTS = {
  "router": ('localhost', 7777),
  "irc": ('localhost', 7779),
  "cdkey": ('localhost', 7780),
  "nat": ('localhost', 7781),
  "router_wm": ('localhost', 7782),
  "proxy": ('localhost', 7783),
  "proxy_wm": ('localhost', 7784),
  "lobby": ('localhost', 7785)
}
"""Service endpoints for the Game Service network."""

class GAME_MODE(Enum):
  """Heroes of Might and Magic 5 game mode."""
  STANDARD = 0
  RATING = 1
  DUEL = 2
  DUEL2 = 3
  """Same as `DUEL`."""
