import socket, sys, os
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import srp, client, utils

SERVER_ADDRESS = ('localhost', 7781)
"""Address of the NAT service."""

CLIENTS: list[client.NatClient] = []
"""Global list of connected game clients."""

def handle_game_req(data: bytes):
  """Handler for non-SRP NAT traffic."""
  # ip address
  if len(data) == 4:
    ip = utils.read_ipv4(data)
    print(f"<REQ: IP>\n{ip}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SERVER_ADDRESS)

print(f"GSNAT server is listening on port {SERVER_ADDRESS[1]}")

while True:
  data, address = sock.recvfrom(1024)
  clt = client.NatClient.find(address, CLIENTS)
  packet_size = len(data)
  if packet_size < srp.SRP_HEADER_SIZE:
    handle_game_req(data)
  else:
    req = srp.SRPRequest(data)
    print(req)
    if clt is None and srp.SRPHeaderFlags.FIN.name not in req.segment.header.flags:
      clt = client.NatClient(address, None, None)
      CLIENTS.append(clt)
      print(f'added client {clt.addr}:{clt.port}')
    
    # ConnectHost (SYN) or NAT message
    if req.segment.window or req.segment.msg:
      res = srp.SRPResponse(req, clt, SERVER_ADDRESS[1])
      sock.sendto(bytes(res), address)
      print(res)
    # Disconnect (FIN)
    if srp.SRPHeaderFlags.FIN.name in req.segment.header.flags:
      if clt is not None and client.NatClient.find((clt.addr, clt.port), CLIENTS):
        CLIENTS.remove(clt)
        print(f'removed client {clt.addr}:{clt.port}')
