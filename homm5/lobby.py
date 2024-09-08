import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import gsm, client

SERVER_ADDRESS = ('localhost', 7785)
"""Address of the lobby service."""

CLIENTS: list[client.TcpClient] = []
"""Global list of connected game clients."""

def handle_req(clt: client.TcpClient, req: gsm.Message):
  """Handler for `gsm.Message` requests."""
  res = None
  match req.header.type:
    case gsm.MESSAGE_TYPE.STILLALIVE:
      pass
    case gsm.MESSAGE_TYPE.LOGINWAITMODULE:
      clt.username = req.dl.lst[0]
      res = gsm.LoginWaitModuleResponse(req)
    case gsm.MESSAGE_TYPE.LOBBYSERVERLOGIN:
      res = gsm.LobbyServerLoginResponse(req)
    case gsm.MESSAGE_TYPE.LOBBY_MSG:
      subtype = gsm.LOBBY_MSG(int(req.dl.lst[0]))
      match subtype:
        case gsm.LOBBY_MSG.JOIN_SERVER:
          res = gsm.JoinLobbyServerResponse(req, SERVER_ADDRESS)
        case gsm.LOBBY_MSG.GROUP_INFO_GET:
          group_id = int(req.dl.lst[1][0])
          res = gsm.GetGroupInfoResponse(req)
        case gsm.LOBBY_MSG.LOGIN:
          game_name = req.dl.lst[1][0]
          res = gsm.LobbyMsgResponse(req)
        case gsm.LOBBY_MSG.JOIN_LOBBY:
          res = gsm.JoinLobbyResponse(req)
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
    CLIENTS.append(clt)
    print(f"Connection from {clt.addr}")
    try:
      while True:
        data = clt.conn.recv(4096)
        if data:
          req = gsm.Message(data, clt.sv_bf_key)
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
      CLIENTS.remove(clt)

if __name__ == "__main__":
    start_server()
