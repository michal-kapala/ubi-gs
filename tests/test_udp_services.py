import sys, os, socket, threading, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'homm5'))
import cdkey, cdkm, gsnat, utils
from data import List

def free_udp_port():
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(('127.0.0.1', 0))
    return sock.getsockname()[1]

def cdkey_request(msg_id: str, req_type: cdkm.REQUEST_TYPE, data: list = None):
  """Builds a game CD-Key request."""
  lst = [msg_id, str(req_type.value)] if data is None else [msg_id, str(req_type.value), '1', data]
  dl = bytearray(bytes(List(lst)))
  dl.pop(0)
  dl.pop()
  enc = cdkm.BLOWFISH.encrypt(bytes(dl))
  return bytes([1]) + utils.write_u32_be(len(enc)) + enc

def start(service):
  service.SERVER_ADDRESS = ('127.0.0.1', free_udp_port())
  threading.Thread(target=service.start_server, daemon=True).start()
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.settimeout(2)
  return sock

class UdpServiceTests(unittest.TestCase):
  """UDP services survive bad packets."""
  def test_cdkey_bad_packets(self):
    sock = start(cdkey)
    threading.Event().wait(0.2)
    try:
      sock.sendto(b'\x01\x00', cdkey.SERVER_ADDRESS)
      sock.sendto(cdkey_request('1', cdkm.REQUEST_TYPE.PLAYER_STATUS, []), cdkey.SERVER_ADDRESS)
      # sent by the game on every clean logout: [..., '6', '1', [authId]]
      sock.sendto(cdkey_request('1', cdkm.REQUEST_TYPE.DISCONNECT_USER, [bytes(20)]), cdkey.SERVER_ADDRESS)
      sock.sendto(cdkey_request('2', cdkm.REQUEST_TYPE.CHALLENGE, []), cdkey.SERVER_ADDRESS)
      res = cdkm.CDKeyMessage(sock.recv(1024))
      self.assertEqual(res.req_type, cdkm.REQUEST_TYPE.CHALLENGE)
    finally:
      sock.close()

  def test_gsnat_bad_segment(self):
    sock = start(gsnat)
    threading.Event().wait(0.2)
    try:
      # SRP header and a truncated window/message
      sock.sendto(bytes(14), gsnat.SERVER_ADDRESS)
      sock.sendto(bytes([0, 0, 1, 0, 8, 0, 0x42, 0x30, 0, 0, 0, 0, 10, 0, 1, 0, 0xB7, 0x1A, 0x18, 0x02]), gsnat.SERVER_ADDRESS)
      # SYN+ACK
      self.assertEqual(len(sock.recv(1024)), 20)
    finally:
      sock.close()

if __name__ == '__main__':
  unittest.main()
