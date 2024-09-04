import struct, typing
from enum import Enum
from utils import write_u16
import gsm, client

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
    if SRPHeaderFlags.FIN.name in self.segment.header.flags:
      return "<DISCONNECT>"
    result = ""
    for flag in self.segment.header.flags:
      if flag != SRPHeaderFlags.SRP_ID.name:
        if len(result) > 0:
          result += f'+{flag}'
        else:
          result += flag
    msg = self.segment.msg if self.segment.msg else ""
    if msg != "":
      msg = f'\n{msg}'
    return f'<REQ: {result if result != "" else "MSG"}>{msg}'

class SRPSegment:
  """SRP packet."""
  def __init__(self, data: bytes):
    self.size = len(data)
    self.header = SRPHeader(data[:SRP_HEADER_SIZE])
    self.window = None
    self.msg = None
    if len(data) > SRP_HEADER_SIZE:
      data = data[SRP_HEADER_SIZE:SRP_HEADER_SIZE + self.header.data_size]
      if len(data) == SRP_WINDOW_SIZE:
        self.window = SRPWindow(data)
      else:
        self.msg = gsm.Message(data, b'')

  def __repr__(self):
    result = str(self.header)
    if self.window is not None:
      result += str(self.window)
    if self.msg is not None:
      result += str(self.msg)
    return result
  
  def __bytes__(self):
    result = bytearray(bytes(self.header))
    if self.size > SRP_HEADER_SIZE:
      if self.size > SRP_HEADER_SIZE + SRP_WINDOW_SIZE:
        result.extend(bytes(self.msg))
      else:
        result.extend(bytes(self.window))
    return bytes(result)
  
class SRPResponse:
  """SRP response."""
  def __init__(self, req: SRPRequest, clt: client.NatClient):
    # save window data on SYN
    if req.segment.window is not None:
      clt.checksum_init = req.segment.window.checksum_init_val
      clt.sender_sig = req.segment.window.sender_sig
    # msg
    self.msg = None
    if req.segment.msg is not None:
      self.msg = gsm.NatResponse(req.segment.msg, gsm.NAT_MSG.ADDRESS, clt)
      msg = bytes(self.msg)
    # header  
    checksum = write_u16(clt.checksum_init)
    signature = write_u16(clt.sender_sig)
    size = SRP_WINDOW_SIZE
    if self.msg:
      size = len(msg)
    data_size = write_u16(size)
    flags = SRPHeaderFlags.SRP_ID.value | SRPHeaderFlags.ACK.value
    if SRPHeaderFlags.SYN.name in req.segment.header.flags:
      flags |= SRPHeaderFlags.SYN.value
    flags = write_u16(flags)
    seg = write_u16(req.segment.header.seg + 1)
    ack = write_u16(req.segment.header.seg)
    header = bytearray(checksum + signature + data_size + flags + seg + ack)
    self.header = SRPHeader(bytes(header))
    # window
    self.window = None
    if req.segment.window is not None:
      tail = write_u16(10)
      sender_sig = write_u16(2)
      checksum_init = write_u16(0)
      window_buf_size = write_u16(0x218)
      window = bytes(tail + sender_sig + checksum_init + window_buf_size)
      self.window = SRPWindow(window)

    if self.msg:
      header.extend(msg)
    elif self.window:
      header.extend(window)
    checksum = SRPResponse.__make_checksum(bytes(header))
    self.header.checksum = checksum[0] + (checksum[1] << 8)

  def __repr__(self):
    result = ""
    for flag in self.header.flags:
      if flag != SRPHeaderFlags.SRP_ID.name:
        if len(result) > 0:
          result += f'+{flag}'
        else:
          result += f'{flag}'
    msg = self.msg if self.msg else ""
    if msg != "":
      msg = f'\n{msg}'
    return f'<RES: {result if result != SRPHeaderFlags.ACK.name else "MSG"}>{msg}'

  def __bytes__(self):
    result = bytearray(bytes(self.header))
    if self.msg:
      result.extend(bytes(self.msg))
    elif self.window:
      result.extend(bytes(self.window))
    return bytes(result)

  def __make_checksum(data: bytes):
    """Calculates SRP checksum for the segment (u16)."""
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
