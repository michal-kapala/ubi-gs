import utils
from enum import Enum
from blowfish import Cipher
from data import List, Bin
from gsm import MESSAGE_TYPE

class CDKEY_PLAYER_STATUS(Enum):
  """Player status."""
  E_PLAYER_UNKNOWN = 0
  E_PLAYER_INVALID = 1
  E_PLAYER_VALID = 2

class REQUEST_TYPE(Enum):
  """CD-Key service requests."""
  CHALLENGE = 1
  ACTIVATION = 2
  AUTH = 3
  VALIDATION = 4
  PLAYER_STATUS = 5
  DISCONNECT_USER = 6
  STILL_ALIVE = 7

BLOWFISH = Cipher("SKJDHF$0maoijfn4i8$aJdnv1jaldifar93-AS_dfo;hjhC4jhflasnF3fnd")

class CDKeyMessage:
  def __init__(self, bts: bytes):
    self.type = bts[0]
    self.size = utils.read_u32_be(bts[1:5])
    self.dl: List = List.from_buf(bytearray(BLOWFISH.decrypt(bts[5:])))
    self.msg_id = int(self.dl.lst[0])
    self.req_type = REQUEST_TYPE(int(self.dl.lst[1]))
    if self.req_type != REQUEST_TYPE.STILL_ALIVE:
      self.unknown = int(self.dl.lst[2])
      self.inner_dl = self.dl.lst[3]
    
  def __repr__(self) -> str:
    return f"<{self.req_type.name}:\t{str(self.dl)}>"

class Response:
  """Base class for CDKM responses."""
  def __init__(self, req: CDKeyMessage):
    self.type = req.type
    self.req_type = req.req_type
    self.size = 0
    self.dl = List([str(req.msg_id), str(req.req_type.value), str(req.unknown), []])

  def __repr__(self):
    return f"<{self.req_type.name} RES:\t{str(self.dl)}>"

  def to_buf(self) -> bytes:
    """Serializes the response into a CDKeyMessage buffer."""
    buf = bytearray()
    buf.append(self.type)
    dl = bytearray(bytes(self.dl))
    dl.pop(0)
    dl.pop()
    dl = BLOWFISH.encrypt(bytes(dl))
    self.size = len(dl)
    buf.extend(utils.write_u32_be(self.size))
    buf.extend(dl)
    return buf

class ChallengeResponse(Response):
  def __init__(self, req: CDKeyMessage):
    super().__init__(req)
    self.msg_type = MESSAGE_TYPE.GSSUCCESS
    hash = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff\x01\x02\x03\x04'
    res_data = [bytes(Bin(hash))]
    self.dl.lst[3].append(str(self.msg_type.value))
    self.dl.lst[3].append(res_data)

class ActivationResponse(Response):
  def __init__(self, req: CDKeyMessage):
    super().__init__(req)
    self.msg_type = MESSAGE_TYPE.GSSUCCESS
    activation_id = b'\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33'
    buf2 = b'\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44'
    res_data = [bytes(Bin(activation_id)), bytes(Bin(buf2))]
    self.dl.lst[3].append(str(self.msg_type.value))
    self.dl.lst[3].append(res_data)

class AuthResponse(Response):
  def __init__(self, req: CDKeyMessage):
    super().__init__(req)
    self.msg_type = MESSAGE_TYPE.GSSUCCESS
    auth_id = b'\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55'
    res_data = [bytes(Bin(auth_id))]
    self.dl.lst[3].append(str(self.msg_type.value))
    self.dl.lst[3].append(res_data)

class ValidationResponse(Response):
  def __init__(self, req: CDKeyMessage):
    super().__init__(req)
    self.msg_type = MESSAGE_TYPE.GSSUCCESS
    status = CDKEY_PLAYER_STATUS.E_PLAYER_VALID
    buf = b'\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66'
    res_data = [str(status.value), bytes(Bin(buf))]
    self.dl.lst[3].append(str(self.msg_type.value))
    self.dl.lst[3].append(res_data)
