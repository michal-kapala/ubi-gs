import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import gsm, client, h5
from group import Room, LSM, MemberInfo

SERVER_ADDRESS = h5.ENDPOINTS["lobby"]
"""Address of the lobby service."""

g_clients: list[client.TcpClient] = []
"""Global list of connected game clients."""

g_rooms: list[Room] = []
"""Global list of active rooms (player-viewed lobbies)."""

next_room_id = 1000
"""Global room id assignment counter."""

def handle_req(clt: client.TcpClient, req: gsm.Message):
  """Handler for `gsm.Message` requests."""
  global next_room_id
  res = None
  match req.header.type:
    case gsm.MESSAGE_TYPE.STILLALIVE:
      pass
    case gsm.MESSAGE_TYPE.LOGINWAITMODULE:
      clt.username = req.dl.lst[0]
      res = gsm.LoginWaitModuleResponse(req)
    case gsm.MESSAGE_TYPE.LOBBYSERVERLOGIN:
      clt.username = req.dl.lst[0]
      res = gsm.LobbyServerLoginResponse(req)
    case gsm.MESSAGE_TYPE.LOBBY_MSG:
      subtype = gsm.LOBBY_MSG(int(req.dl.lst[0]))
      match subtype:
        case gsm.LOBBY_MSG.JOIN_SERVER:
          res = gsm.JoinLobbyServerResponse(req, SERVER_ADDRESS)
        case gsm.LOBBY_MSG.GROUP_INFO_GET:
          group_id = int(req.dl.lst[1][0])
          res = gsm.GetGroupInfoResponse(req)
        case gsm.LOBBY_MSG.CREATE_ROOM:
          room_id = next_room_id
          next_room_id = next_room_id + 1
          res = gsm.CreateRoomResponse(req, g_rooms, room_id, clt.username)
        case gsm.LOBBY_MSG.LOGIN:
          game_name = req.dl.lst[1][0]
          res = gsm.LobbyMsgResponse(req)
        case gsm.LOBBY_MSG.JOIN_LOBBY:
          res = gsm.JoinLobbyResponse(req)
        case gsm.LOBBY_MSG.JOIN_ROOM:
          group_id = int(req.dl.lst[1][0])
          room = next((r for r in g_rooms if r.group_id == group_id), None)
          res = gsm.JoinRoomResponse(req)
          # GROUP_INFO notification
          if room is not None:
            header = gsm.GSMessageHeader.from_params(gsm.PROPERTY.GS, 1, gsm.MESSAGE_TYPE.LOBBY_MSG, gsm.SENDER_RECEIVER.S, gsm.SENDER_RECEIVER.P)
            flags = int(req.dl.lst[1][2]) # LSM (iconfig, group flags)
            # homm5 always requests all info
            if flags == LSM.LSM_ALLINFO.value:
              subtype = str(gsm.LOBBY_MSG.GROUP_INFO.value)
              # subroom children are not a feature
              subrooms: list[Room] = []
              group_members: list[MemberInfo] = MemberInfo(clt.username, str(group_id)).to_list()
              dl = gsm.List([subtype, [str(group_id), str(flags), room.to_list(), subrooms, group_members]])
              msg = gsm.Message(clt.sv_bf_key, header=header, dl=dl)
              notif = gsm.GSMNotification(msg)
              print(notif)
              notif.send_tcp(clt)
            else:
              raise NotImplementedError(f"Unexpected GROUP_INFO iconfig value: {flags}.")
          else:
            raise ValueError("Failed to find the requested room on join.")
        case gsm.LOBBY_MSG.GROUP_CONFIG_UPDATE_RES:
          group_id = int(req.dl.lst[1][0])
          room = next((r for r in g_rooms if r.group_id == group_id), None)
          res = gsm.GroupConfigUpdateResultResponse(req, room)
          # GAME_STARTED notification
          if room is not None:
            header = gsm.GSMessageHeader.from_params(gsm.PROPERTY.GS, 1, gsm.MESSAGE_TYPE.LOBBY_MSG, gsm.SENDER_RECEIVER.S, gsm.SENDER_RECEIVER.P)
            subtype = str(gsm.LOBBY_MSG.GAME_STARTED.value)
            ip = str(clt.addr[0])
            alt_ip = ""
            # tcp 6668, udp 8888?
            port = "8888"
            dl = gsm.List([subtype, [str(group_id), b"", port, ip, alt_ip]])
            msg = gsm.Message(clt.sv_bf_key, header=header, dl=dl)
            notif = gsm.GSMNotification(msg)
            print(notif)
            notif.send_tcp(clt)
          else:
            raise ValueError("Failed to find the requested room on config update.")
        case _:
          raise NotImplementedError(f'No request handler for {subtype.name} lobby message.')
    case _:
      raise NotImplementedError(f"No request handler for {req.header.type.name} messages.")
  return res

def start_server():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print(f"Lobby server is listening on port {SERVER_ADDRESS[1]}")
  sock.bind(SERVER_ADDRESS)
  sock.listen(5)
    
  while True:
    clt = client.TcpClient(sock.accept())
    g_clients.append(clt)
    print(f"Connection from {clt.addr}")
    try:
      while True:
        data = clt.conn.recv(4096)
        if data:
          req = gsm.Message(clt.sv_bf_key, in_buf=data)
          if req.header.size < len(data):
            bundle = gsm.GSMessageBundle(req, data[req.header.size:], clt)
            print(bundle)
            for msg in bundle.msgs:
              print(msg)
              res = handle_req(clt, msg)
              if res:
                print(res)
                clt.conn.sendall(bytes(res))
              elif req.header.type != gsm.MESSAGE_TYPE.STILLALIVE:
                clt.conn.sendall(data)
          else:
            print(req)
            res = handle_req(clt, req)
            if res:
              print(res)
              clt.conn.sendall(bytes(res))
            elif req.header.type != gsm.MESSAGE_TYPE.STILLALIVE:
              clt.conn.sendall(data)
        else:
          print("No more data from", clt.addr)
          break
    finally:
      clt.conn.close()
      g_clients.remove(clt)

if __name__ == "__main__":
    start_server()
