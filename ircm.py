from blowfish import Cipher
import utils

BLOWFISH_KEY = bytes([
  0x06, 0xE2, 0xC8, 0x46, 0x01, 0x90, 0x55, 0x7C,
  0x3C, 0xA1, 0xCD, 0xA3, 0xE3, 0xA1, 0x10, 0x6C
])
"""Static Blowfish key for IRC service."""

BLOWFISH = Cipher(BLOWFISH_KEY)

IRCM_HEADER_SIZE = 2
"""Length of `IRCMessage` header in bytes."""

class IRCMessage:
  """IRC message."""
  def __init__(self, bts: bytes):
    self.size = utils.read_u16_be(bts[:IRCM_HEADER_SIZE])
    self.payload = BLOWFISH.decrypt(bts[IRCM_HEADER_SIZE:])

  def __repr__(self) -> str:
    return self.payload.hex(' ')
