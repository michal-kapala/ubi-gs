import sys, os, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import cdkm, gsm, utils
from data import List

def login_buf(fields: list):
  """Serialized `LOGIN` message as the game sends it."""
  header = gsm.GSMessageHeader.from_params(gsm.PROPERTY.GS, 1, gsm.MESSAGE_TYPE.LOGIN, gsm.SENDER_RECEIVER.P, gsm.SENDER_RECEIVER.R)
  return bytes(gsm.GSMNotification(gsm.Message(None, header=header, dl=List(fields))))

def cdkey_buf(req_type: cdkm.REQUEST_TYPE, data: list):
  """Serialized CD-Key request."""
  dl = bytearray(bytes(List(['1', str(req_type.value), '1', data])))
  dl.pop(0)
  dl.pop()
  enc = cdkm.BLOWFISH.encrypt(bytes(dl))
  return bytes([1]) + utils.write_u32_be(len(enc)) + enc

class GSRedactionTests(unittest.TestCase):
  """GS message logs leave out passwords."""
  def test_router_login(self):
    text = repr(gsm.Message(None, in_buf=login_buf(['alice', 'secret', 'HEROES_c83663d1c69a2024', b'\x01'])))
    self.assertIn('alice', text)
    self.assertIn('HEROES_c83663d1c69a2024', text)
    self.assertNotIn('secret', text)

  def test_proxy_login(self):
    # [user, game name], nothing to hide
    text = repr(gsm.Message(None, in_buf=login_buf(['alice', 'HEROES_657d2c2ebadc6a1d'])))
    self.assertIn('HEROES_657d2c2ebadc6a1d', text)

  def test_payload_untouched(self):
    msg = gsm.Message(None, in_buf=login_buf(['alice', 'secret', 'HEROES_c83663d1c69a2024']))
    self.assertEqual(msg.dl.lst[1], 'secret')

class CDKeyRedactionTests(unittest.TestCase):
  """CD-Key logs leave out key-derived data."""
  def test_key_data(self):
    for req_type in cdkm.KEY_DATA_REQUESTS:
      text = repr(cdkm.CDKeyMessage(cdkey_buf(req_type, [b'KEYDERIVEDDATA'])))
      self.assertNotIn('KEYDERIVED', text, req_type.name)
      self.assertIn(req_type.name, text)

  def test_challenge(self):
    self.assertIn('CHALLENGE', repr(cdkm.CDKeyMessage(cdkey_buf(cdkm.REQUEST_TYPE.CHALLENGE, []))))

if __name__ == '__main__':
  unittest.main()
