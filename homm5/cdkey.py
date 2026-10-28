import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import cdkm, h5

NOTIFS = [cdkm.REQUEST_TYPE.DISCONNECT_USER, cdkm.REQUEST_TYPE.STILL_ALIVE]
SERVER_ADDRESS = h5.ENDPOINTS["cdkey"]
"""Address of the CD-Key service."""

def handle_packet(data: bytes):
  """Handles a CD-Key request, returns the response buffer if there is one."""
  req = cdkm.CDKeyMessage(data)
  print(req)
  match req.req_type:
    case cdkm.REQUEST_TYPE.CHALLENGE:
      res = cdkm.ChallengeResponse(req)
    case cdkm.REQUEST_TYPE.ACTIVATION:
      res = cdkm.ActivationResponse(req)
    case cdkm.REQUEST_TYPE.AUTH:
      res = cdkm.AuthResponse(req)
    case cdkm.REQUEST_TYPE.VALIDATION:
      res = cdkm.ValidationResponse(req)
    case _:
      # player status requests are unsupported, the rest are notifications
      if req.req_type not in NOTIFS:
        print(f"Unsupported request: {req.req_type.name}")
      return None
  print(res)
  return bytes(res)

def start_server():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(SERVER_ADDRESS)
  print(f"CD Key server is listening on port {SERVER_ADDRESS[1]}")

  while True:
    data, address = sock.recvfrom(1024)
    # one bad packet must not stop the service
    try:
      res = handle_packet(data)
    except Exception as err:
      print(f"Bad packet from {address[0]}:{address[1]}: {err!r}")
      continue
    if res is not None:
      sock.sendto(res, address)

if __name__ == "__main__":
  start_server()
