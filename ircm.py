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
  """GS implementation of IRC message."""
  def __init__(self, bts = bytes()):
    if len(bts) > 0:
      self.size = utils.read_u16_be(bts[:IRCM_HEADER_SIZE])
      self.payload = BLOWFISH.decrypt(bts[IRCM_HEADER_SIZE:])

  def __repr__(self):
    return self.payload.decode()

  def __bytes__(self):
    """Encrypts and serializes the message to buffer."""
    payload = BLOWFISH.encrypt(self.payload)
    size = len(payload) + IRCM_HEADER_SIZE
    result = bytearray(utils.write_u16_be(size))
    result.extend(payload)
    return bytes(result)

  def from_str(text: str):
    """Creates an instance from plaintext."""
    msg = IRCMessage()
    msg.payload = text.encode()
    msg.size = len(msg.payload) + IRCM_HEADER_SIZE
    return msg

