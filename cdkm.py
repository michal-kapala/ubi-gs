import utils
from enum import Enum
from blowfish import Cipher
from data import List

class MESSAGE_TYPE(Enum):
  NEWUSERREQUEST = 1
  CONNECTIONREQUEST = 2
  PLAYERNEW = 3
  DISCONNECTION = 4
  PLAYERREMOVED = 5
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
  BEGINCLIENTHOSTGAME = 205
  LOBBY_MSG = 209
  LOBBYSERVERLOGIN = 210
  SETGROUPSZDATA = 211
  GROUPSZDATA = 212

class REQUEST_TYPE(Enum):
  """CD-Key service requests."""
  CHALLENGE = 1
  ACTIVATION = 2
  AUTH = 3
  VALIDATION = 4
  PLAYER_STATUS = 5

BLOWFISH = Cipher("SKJDHF$0maoijfn4i8$aJdnv1jaldifar93-AS_dfo;hjhC4jhflasnF3fnd")

class CDKeyMessage:
  def __init__(self, bts: bytes):
    self.type = bts[0]
    self.size = utils.read_u32_be(bts[1:5])
    self.dl: List = List.from_buf(bytearray(BLOWFISH.decrypt(bts[5:])))
    if len(self.dl.lst) < 4:
      raise BufferError("Received incomplete message")
    self.msg_id = int(self.dl.lst[0])
    self.req_type = REQUEST_TYPE(int(self.dl.lst[1]))
    self.unknown = int(self.dl.lst[2])
    self.inner_dl = self.dl.lst[3]
    
  def __repr__(self) -> str:
    return f"<{self.req_type.name}:\t{str(self.dl)}>"

class Response:
  """Base class for CDKM responses."""
  def __init__(self, req: CDKeyMessage):
    self.type = req.type
    self.size = 0
    self.dl = List([str(req.msg_id), str(req.req_type.value), str(req.unknown), []])

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
    hash_size = "2"
    hash = "hi"
    res_data = [hash_size, hash]
    self.dl.lst[3].append(str(self.msg_type.value))
    self.dl.lst[3].append(res_data)

  def __repr__(self):
    return f"<CHALLENGE RES:\t{str(self.dl)}>"
