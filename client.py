import rsa, socket, typing

class TcpClient:
  """Connected game client."""
  def __init__(self, conn: tuple[socket.socket, typing.Any]):
    self.conn = conn[0]
    self.addr = conn[1]
    self.game_pubkey: rsa.PublicKey = None
    self.sv_pubkey: rsa.PublicKey = None
    self.sv_privkey: rsa.PrivateKey = None
    self.game_bf_key: bytes = None
    self.sv_bf_key: bytes = None
    self.username: str = None

class UdpClient:
  """Connected game client."""
  def __init__(self, addr: tuple[str, int]):
    self.addr = addr[0]
    self.port = addr[1]

class NatClient(UdpClient):
  """Connected game client."""
  def __init__(self, addr: tuple[str, int], checksum_init: int, sender_sig: int):
    super().__init__(addr)
    self.checksum_init = checksum_init
    self.sender_sig = sender_sig

  def find(addr: tuple[str, int], clients: list[typing.Self]):
    """Searches for the address in the list and returns the client if found."""
    return next((cl for cl in clients if cl.addr == addr[0] and cl.port == addr[1]), None)
