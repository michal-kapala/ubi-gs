import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import cdkm

SERVER_ADDRESS = ('localhost', 7780)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDRESS)
print(f"CD Key server is listening on port {SERVER_ADDRESS[1]}")

while True:
  data, address = sock.recvfrom(1024)
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
    case cdkm.REQUEST_TYPE.PLAYER_STATUS:
      raise NotImplementedError("Player status requests are unsupported")

  print(res)
  sock.sendto(res.to_buf(), address)
