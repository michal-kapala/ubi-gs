from enum import Enum

SRP_HEADER_SIZE = 12
"""Length of SRP header in bytes."""

class SRPHeaderFlags(Enum):
  """Flags of SRPHeader."""
  FIN = 1
  SYN = 2
  ACK = 4
  URG = 8
  SRP_ID = 0x3040

class SRPHeader:
  """SRP header with packet type and connection info."""
  def __init__(self, data: bytes):
    self.checksum = data[0] + (data[1] << 8)
    self.signature = data[2] + (data[3] << 8)
    self.data_size = data[4] + (data[5] << 8)
    self.flags = self.__read_flags(data[6] + (data[7] << 8))
    self.seg = data[8] + (data[9] << 8)
    self.ack = data[10] + (data[11] << 8)

  def __repr__(self):
    return f"""
      checksum:\t{self.checksum:x}
      sig:\t{self.signature:x}
      dataSize: {self.data_size:x}
      flags:\t{self.flags}
      seg:\t{self.seg:x}
      ack:\t{self.ack:x}
    """
  
  def __read_flags(self, flags: int):
    flag_list: list[str] = []
    for flag in SRPHeaderFlags:
      if flags & flag.value > 0:
        flag_list.append(flag.name)
    return flag_list

class SRPWindow:
  """Window data of an SRP segment."""
  def __init__(self, data: bytes):
    self.tail = data[0] + (data[1] << 8)
    self.sender_sig = data[2] + (data[3] << 8)
    self.checksum_init_val = data[4] + (data[5] << 8)
    self.wnd_buf_size = data[6] + (data[7] << 8)

  def __repr__(self) -> str:
    return f"""
      tail:\t{self.tail:x}
      sndSig:\t{self.sender_sig:x}
      initVal:\t{self.checksum_init_val:x}
      wndSize:\t{self.wnd_buf_size}
    """

class Segment:
  """SRP packet."""
  def __init__(self, data: bytes):
    self.size = len(data)
    self.header = SRPHeader(data[:SRP_HEADER_SIZE])
    if len(data) > SRP_HEADER_SIZE:
      self.window = SRPWindow(data[SRP_HEADER_SIZE:])

  def __repr__(self):
    result = str(self.header)
    if self.size > SRP_HEADER_SIZE:
      result += str(self.window)
    return result