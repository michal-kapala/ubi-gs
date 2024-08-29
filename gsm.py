from enum import Enum
import blowfish, gsxor, pkc, tcp, utils
from data import List

GSMSG_HEADER_SIZE = 6
"""Length of `GSMessageHeader` in bytes."""

class MESSAGE_TYPE(Enum):
  """Type of `GSMessage` or its result."""
  NEWUSERREQUEST = 1
  CONNECTIONREQUEST = 2
  PLAYERNEW = 3
  DISCONNECTION = 4
  PLAYERREMOVED = 5
  EVENT_UDPCONNECT = 6
  NEWS = 7
  SEARCHPLAYER = 8
  REMOVEACCOUNT = 9
  SERVERSLIST = 11
  SESSIONLIST = 13
  PLAYERLIST = 15
  GETGROUPINFO = 16
  GROUPINFO = 17
  GETPLAYERINFO = 18
  PLAYERINFO = 19
  CHATALL = 20
  CHATLIST = 21
  CHATSESSION = 22
  CHAT = 24
  CREATESESSION = 26
  SESSIONNEW = 27
  JOINSESSION = 28
  JOINNEW = 31
  LEAVESESSION = 32
  JOINLEAVE = 33
  SESSIONREMOVE = 34
  GSSUCCESS = 38
  GSFAIL = 39
  BEGINGAME = 40
  UPDATEPLAYERINFO = 45
  MASTERCHANGED = 48
  UPDATESESSIONSTATE = 51
  URGENTMESSAGE = 52
  NEWWAITMODULE = 54
  KILLMODULE = 55
  STILLALIVE = 58
  PING = 59
  PLAYERKICK = 60
  PLAYERMUTE = 61
  ALLOWGAME = 62
  FORBIDGAME = 63
  GAMELIST = 64
  UPDATEADVERTISMEMENTS = 65
  UPDATENEWS = 66
  VERSIONLIST = 67
  UPDATEVERSIONS = 68
  UPDATEDISTANTROUTERS = 70
  ADMINLOGIN = 71
  STAT_PLAYER = 72
  STAT_GAME = 73
  UPDATEFRIEND = 74
  ADDFRIEND = 75
  DELFRIEND = 76
  LOGINWAITMODULE = 77
  LOGINFRIENDS = 78
  ADDIGNOREFRIEND = 79
  DELIGNOREFRIEND = 80
  STATUSCHANGE = 81
  JOINARENA = 82
  LEAVEARENA = 83
  IGNORELIST = 84
  IGNOREFRIEND = 85
  GETARENA = 86
  GETSESSION = 87
  PAGEPLAYER = 88
  FRIENDLIST = 89
  PEERMSG = 90
  PEERPLAYER = 91
  DISCONNECTFRIENDS = 92
  JOINWAITMODULE = 93
  LOGINSESSION = 94
  DISCONNECTSESSION = 95
  PLAYERDISCONNECT = 96
  ADVERTISEMENT = 97
  MODIFYUSER = 98
  STARTGAME = 99
  CHANGEVERSION = 100
  PAGER = 101
  LOGIN = 102
  PHOTO = 103
  LOGINARENA = 104
  SQLCREATE = 106
  SQLSELECT = 107
  SQLDELETE = 108
  SQLSET = 109
  SQLSTAT = 110
  SQLQUERY = 111
  ROUTEURLIST = 127
  DISTANCEVECTOR = 131
  WRAPPEDMESSAGE = 132
  CHANGEFRIEND = 133
  NEWRELFRIEND = 134
  DELRELFRIEND = 135
  NEWIGNOREFRIEND = 136
  DELETEIGNOREFRIEND = 137
  ARENACONNECTION = 138
  ARENADISCONNECTION = 139
  ARENAWAITMODULE = 140
  ARENANEW = 141
  NEWBASICGROUP = 143
  ARENAREMOVED = 144
  DELETEBASICGROUP = 145
  SESSIONSBEGIN = 146
  GROUPDATA = 148
  ARENA_MESSAGE = 151
  ARENALISTREQUEST = 157
  ROUTERPLAYERNEW = 158
  BASEGROUPREQUEST = 159
  UPDATEPLAYERPING = 166
  UPDATEGROUPSIZE = 169
  SLEEP = 179
  WAKEUP = 180
  SYSTEMPAGE = 181
  SESSIONOPEN = 189
  SESSIONCLOSE = 190
  LOGINCLANMANAGER = 192
  DISCONNECTCLANMANAGER = 193
  CLANMANAGERPAGE = 194
  UPDATECLANPLAYER = 195
  PLAYERCLANS = 196
  GETPERSISTANTGROUPINFO = 199
  UPDATEGROUPPING = 202
  DEFERREDGAMESTARTED = 203
  PROXY_HANDLER = 204
  BEGINCLIENTHOSTGAME = 205
  LOBBY_MSG = 209
  LOBBYSERVERLOGIN = 210
  SETGROUPSZDATA = 211
  GROUPSZDATA = 212
  KEY_EXCHANGE = 219
  REQUESTPORTID = 221

class SENDER_RECEIVER(Enum):
  """GSMessage sender/receiver types."""
  R = 1
  S = 2
  W = 3
  P = 4
  AP = 5
  B = 6
  LP = 7
  UNK = 8
  G = 9
  A = 10
  PROXY = 11

class PROPERTY(Enum):
  """Used implementation of the message."""
  GS = 0
  GAME = 1
  GS_ENCRYPT = 2

class GSMessageHeader:
  """Header for `GSMessage` and `GSEncryptMessage`."""
  def __init__(self, bts: bytes):
    self.size = (bts[0] << 16) + (bts[1] << 8) + bts[2]
    self.property = PROPERTY(bts[3] >> 6)
    self.priority = bts[3] & 0x3F
    self.type = MESSAGE_TYPE(bts[4])
    self.sender = SENDER_RECEIVER(bts[5] >> 4)
    self.receiver = SENDER_RECEIVER(bts[5] & 0x0F)

  def __bytes__(self):
    result = bytearray(GSMSG_HEADER_SIZE)
    size = utils.write_u24_be(self.size)
    result[0] = size[0]
    result[1] = size[1]
    result[2] = size[2]
    result[3] &= 0x1F
    result[3] |= self.property.value << 6
    result[3] |= self.priority & 0x20
    result[4] = self.type.value
    result[5] &= 0xF
    result[5] |= 0x10 * self.sender.value
    result[5] &= 0xF0
    result[5] |= self.receiver.value & 0xF
    return bytes(result)

class Message:
  """Common message implementation."""
  def __init__(self, bts: bytes, bf_key: bytes):
    self.header = GSMessageHeader(bts[:GSMSG_HEADER_SIZE])
    self.dl = None
    match self.header.property:
      case PROPERTY.GS:
        if self.header.size > GSMSG_HEADER_SIZE:
          dec = gsxor.decrypt(bts[GSMSG_HEADER_SIZE:self.header.size])
          self.dl: List = List.from_buf(bytearray(dec))
      case PROPERTY.GAME:
        pass
      case PROPERTY.GS_ENCRYPT:
        dec = blowfish.Cipher(bf_key).decrypt(bts[GSMSG_HEADER_SIZE:self.header.size])
        self.dl: List = List.from_buf(bytearray(dec))

  def __repr__(self):
    payload = self.dl or ""
    return f"<{self.header.type.name}\t{self.header.property.name}\t{self.header.sender.name}->{self.header.receiver.name}\t{self.header.size}B>\n{payload}"

class GSMessageBundle:
  """Packet containing 2 or more GS messages."""
  def __init__(self, first: Message, data: bytes, client: tcp.TcpClient):
    self.msgs = [first]
    while len(data) > 0:
      msg = Message(bytes(data), client.sv_bf_key)
      self.msgs.append(msg)
      data = data[msg.header.size:]

  def __repr__(self):
    result = f"<BUNDLE: {self.msgs[0].header.type.name}"
    for i in range(1, len(self.msgs), 1):
      result += f" + {self.msgs[i].header.type.name}"
    return result + ">"

class GSMResponse:
  """Base class for GS message responses."""
  def __init__(self, req: Message):
    self.header = req.header
    self.header.sender, self.header.receiver = self.header.receiver, self.header.sender
    self.dl: List = None

  def __bytes__(self):
    bts = bytearray()
    dl = None
    if self.dl is not None:
      dl = bytearray(bytes(self.dl))
      dl.pop(0)
      dl.pop()
      match self.header.property:
        case PROPERTY.GS:
          dl = gsxor.encrypt(bytes(dl))
          self.header.size = GSMSG_HEADER_SIZE + len(dl)
        case PROPERTY.GS_ENCRYPT:
          raise NotImplementedError("GS_ENCRYPT message serialization unsupported.")

    bts.extend(bytes(self.header))
    if dl is not None:
      bts.extend(dl)
    return bytes(bts)

  def __repr__(self):
    payload = self.dl or ""
    return f"<{self.header.type.name} RES\t{self.header.property.name}\t{self.header.sender.name}->{self.header.receiver.name}\t{self.header.size}B>\n{payload}"

class KeyExchangeResponse(GSMResponse):
  """Response to `KEY_EXCHANGE` messages."""
  def __init__(self, req: Message, client: tcp.TcpClient):
    if req.header.type != MESSAGE_TYPE.KEY_EXCHANGE:
      raise TypeError(f"KeyExchangeResponse constructed from {req.header.type} request.")
    super().__init__(req)
    req_id = int(req.dl.lst[0])
    match req_id:
      case 1:
        self.dl = List(['1', ['1']])
        pub_key: pkc.RsaPublicKey = pkc.RsaPublicKey.from_pubkey(client.sv_pubkey)
        buf = bytes(pub_key)
        self.dl.lst[1].append(str(len(buf)))
        self.dl.lst[1].append(buf)
      case 2:
        self.dl = List(['2', ['1']])
        bf_key = blowfish.Cipher.keygen(16)
        client.sv_bf_key = bf_key
        enc_key = pkc.encrypt(bf_key, client.game_pubkey)
        self.dl.lst[1].append(str(len(enc_key)))
        self.dl.lst[1].append(enc_key)
      case 3:
        raise NotImplementedError("KEY_EXCHANGE disconnections are not implemented.")
      case _:
        raise BufferError(f"KEY_EXCHANGE request with req_id={req_id}.")

class LoginResponse(GSMResponse):
  """Response to `LOGIN` messages."""
  def __init__(self, req: Message):
    if req.header.type != MESSAGE_TYPE.LOGIN:
      raise TypeError(f"LoginResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.GSSUCCESS
    msg_id = MESSAGE_TYPE.LOGIN.value
    self.dl = List([msg_id.to_bytes(1, 'little')])

class JoinWaitModuleResponse(GSMResponse):
  """Response to `JOINWAITMODULE` messages."""
  def __init__(self, req: Message, wait_module: tuple[str, int]):
    if req.header.type != MESSAGE_TYPE.JOINWAITMODULE:
      raise TypeError(f"JoinWaitModuleResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.GSSUCCESS
    msg_id = MESSAGE_TYPE.JOINWAITMODULE.value
    self.dl = List([msg_id.to_bytes(1, 'little'), [wait_module[0], utils.write_u32(wait_module[1])]])

class LoginWaitModuleResponse(GSMResponse):
  """Response to `LOGINWAITMODULE` messages."""
  def __init__(self, req: Message):
    if req.header.type != MESSAGE_TYPE.LOGINWAITMODULE:
      raise TypeError(f"LoginWaitModuleResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.GSSUCCESS
    msg_id = MESSAGE_TYPE.LOGINWAITMODULE.value
    self.dl = List([msg_id.to_bytes(1, 'little')])

class PlayerInfoResponse(GSMResponse):
  """Response to `PLAYERINFO` messages."""
  def __init__(self, req: Message):
    if req.header.type != MESSAGE_TYPE.PLAYERINFO:
      raise TypeError(f"PlayerInfoResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.GSSUCCESS
    msg_id = MESSAGE_TYPE.PLAYERINFO.value
    player_data = ['findme1', 'findme2', 'findme3', 'findme4', 'findme5', 'findme6', 'findme7']
    self.dl = List([msg_id.to_bytes(1, 'little'), player_data])

class ProxyHandlerResponse(GSMResponse):
  """Response to `PROXY_HANDLER` messages."""
  def __init__(self, req: Message, proxy_addr: tuple[str, int]):
    if req.header.type != MESSAGE_TYPE.PROXY_HANDLER:
      raise TypeError(f"ProxyHandlerResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.PROXY_HANDLER
    result = str(MESSAGE_TYPE.GSSUCCESS.value)
    subtype = req.dl.lst[0]
    match subtype:
      case "1":
        module_info = ["persistantdata", "0", "0"]
        proxy_info_key = "1"
        proxy_info = [[proxy_info_key, proxy_addr[0], str(proxy_addr[1])]]
        module_info.append(proxy_info)
        self.dl = List([result, [subtype, module_info]])
      case "2":
        self.dl = List([result, [subtype, ["1"]]])
      case _:
        raise BufferError(f"Unknown PROXY_HANDLER message subtype {subtype}")

class ProxyLoginResponse(GSMResponse):
  """Response to `LOGIN` messages for proxy service."""
  def __init__(self, req: Message):
    if req.header.type != MESSAGE_TYPE.LOGIN:
      raise TypeError(f"ProxyLoginResponse constructed from {req.header.type} request.")
    super().__init__(req)
    self.header.property = PROPERTY.GS
    self.header.type = MESSAGE_TYPE.GSSUCCESS
    msg_id = MESSAGE_TYPE.LOGIN.value
    self.dl = List([msg_id.to_bytes(1, 'little'), []])
