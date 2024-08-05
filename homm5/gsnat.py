import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
from srp import SRPHeaderFlags, SRPRequest, SRPResponse

SERVER_ADDRESS = ('localhost', 7781)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDRESS)

print(f"GSNAT server is listening on port {SERVER_ADDRESS[1]}")

while True:
  data, address = sock.recvfrom(1024)
  req = SRPRequest(data)
  print(f"Received {req.segment.size} bytes from {address}")
  # ConnectHost (SYN)
  if SRPHeaderFlags.SYN.name in req.segment.header.flags:
    print(req)
    res = SRPResponse(req)
    sock.sendto(bytes(res), address)
    print(f"Sent response to {address}:")
    print(res)
