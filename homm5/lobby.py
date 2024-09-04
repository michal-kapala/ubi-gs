import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import gsm, tcp

SERVER_ADDRESS = ('localhost', 7785)
"""Address of the lobby service."""

CLIENTS: list[tcp.TcpClient] = []
"""Global list of connected game clients."""

def handle_req(client: tcp.TcpClient, req: gsm.Message):
  """Handler for `gsm.Message` requests."""
  res = None
  match req.header.type:
    case gsm.MESSAGE_TYPE.STILLALIVE:
      pass
    case gsm.MESSAGE_TYPE.LOGINWAITMODULE:
      client.username = req.dl.lst[0]
      res = gsm.LoginWaitModuleResponse(req)
    case _:
      raise NotImplementedError(f"No request handler for {req.header.type.name} messages.")
  return res

def start_server():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print(f"Lobby server is listening on port {SERVER_ADDRESS[1]}")
  sock.bind(SERVER_ADDRESS)
  sock.listen(5)
    
  while True:
    client = tcp.TcpClient(sock.accept())
    CLIENTS.append(client)
    print(f"Connection from {client.addr}")
    try:
      while True:
        data = client.conn.recv(4096)
        if data:
          req = gsm.Message(data, client.sv_bf_key)
          if req.header.size < len(data):
            bundle = gsm.GSMessageBundle(req, data[req.header.size:], client)
            print(bundle)
            for msg in bundle.msgs:
              print(msg)
              res = handle_req(client, msg)
              if res:
                print(res)
                client.conn.sendall(bytes(res))
              elif req.header.type != gsm.MESSAGE_TYPE.STILLALIVE:
                client.conn.sendall(data)
          else:
            print(req)
            res = handle_req(client, req)
            if res:
              print(res)
              client.conn.sendall(bytes(res))
            elif req.header.type != gsm.MESSAGE_TYPE.STILLALIVE:
              client.conn.sendall(data)
        else:
          print("No more data from", client.addr)
          break
    finally:
      client.conn.close()
      CLIENTS.remove(client)

if __name__ == "__main__":
    start_server()
