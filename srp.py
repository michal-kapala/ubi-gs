import struct
from enum import Enum
from utils import write_u16

SRP_HEADER_SIZE = 12
"""Length of SRP header in bytes."""

SRP_WINDOW_SIZE = 8
"""Length of SRP window data in bytes."""

class SRPHeaderFlags(Enum):
  """Flags of SRPHeader."""
  FIN = 1
  SYN = 2
  ACK = 4
  URG = 8
  SRP_ID = 0x3040

HEADER_FLAGS = {flag.name: flag.value for flag in SRPHeaderFlags}
"""SRPHeaderFlags enum wrapper."""

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
  
  def __bytes__(self):
    result = bytearray()
    result.extend(write_u16(self.checksum))
    result.extend(write_u16(self.signature))
    result.extend(write_u16(self.data_size))
    flags = 0
    for flag in self.flags:
      flags |= HEADER_FLAGS[flag]
    result.extend(write_u16(flags))
    result.extend(write_u16(self.seg))
    result.extend(write_u16(self.ack))
    return bytes(result)
  
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
      wndSize:\t{self.wnd_buf_size:x}
    """
  
  def __bytes__(self):
    result = bytearray(write_u16(self.tail))
    result.extend(write_u16(self.sender_sig))
    result.extend(write_u16(self.checksum_init_val))
    result.extend(write_u16(self.wnd_buf_size))
    return bytes(result)
  
class SRPRequest:
  """SRP request."""
  def __init__(self, data: bytes):
    self.segment = SRPSegment(data)

  def __repr__(self):
    return str(self.segment)

class SRPSegment:
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
  
  def __bytes__(self):
    result = bytearray(bytes(self.header))
    if self.size > SRP_HEADER_SIZE:
      result.extend(bytes(self.window))
    return bytes(result)
  
  def from_req(req: SRPRequest):
    # header
    checksum = write_u16(req.segment.window.checksum_init_val)
    signature = bytes([(req.segment.window.sender_sig & 0xff), (req.segment.window.sender_sig >> 8)])
    data_size = bytes([SRP_WINDOW_SIZE, 0x00])
    flags = write_u16(SRPHeaderFlags.SRP_ID.value | SRPHeaderFlags.SYN.value | SRPHeaderFlags.ACK.value)
    seg = write_u16(req.segment.header.seg + 1)
    ack = write_u16(req.segment.header.seg)
    data = bytearray(checksum + signature + data_size + flags + seg + ack)
    # window
    tail = bytes([0x0A, 0x00])
    sender_sig = bytes([0x02, 0x00])
    checksum_init = bytes([0x00, 0x00])
    window_buf_size = bytes([0x18, 0x02])
    data.extend(tail + sender_sig + checksum_init + window_buf_size)

    segment = SRPSegment(bytes(data))
    checksum = segment.__make_checksum(bytes(data))
    segment.header.checksum = checksum[0] + (checksum[1] << 8)
    return segment
  
  def __make_checksum(self, data: bytes):
    """Calculates SRP checksum of the segment (u16)."""
    trunc_pos = 0
    check_base = 0
    half_len = len(data) >> 1
    odd_len = len(data) % 2 == 1
    
    if odd_len:
      # Add the first byte as extra
      check_base += data[0]
      trunc_pos += 1

    if half_len > 0:
      for _ in range(half_len):
        check_base += struct.unpack_from('<H', data, trunc_pos)[0]
        trunc_pos += 2
    checksum = check_base & 0xFFFF
    checksum += check_base >> 16
    checksum += checksum >> 16
    checksum = ~checksum & 0xFFFF
    return write_u16(checksum)
  
class SRPResponse:
  """SRP response."""
  def __init__(self, req: SRPRequest):
    self.segment = SRPSegment.from_req(req)

  def __repr__(self):
    return str(self.segment)

  def __bytes__(self):
    return bytes(self.segment)
