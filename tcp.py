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
