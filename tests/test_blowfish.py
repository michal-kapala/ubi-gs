import sys, os, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
from blowfish import Blowfish, Cipher

class BlowfishTests(unittest.TestCase):
  """Tests for Blowfish encryption algorithm."""
  def test_bf(self):
    L = 1
    R = 2
    bf = Blowfish("TESTKEY")
    encL, encR = bf.encrypt(L, R)
    self.assertEqual((encL, encR), (0xdf333fd2, 0x30a71bb4))
    decL, decR = bf.decrypt(encL, encR)
    self.assertEqual((decL, decR), (L, R))

  def test_cipher(self):
    cipher = Cipher("SKJDHF$0maoijfn4i8$aJdnv1jaldifar93-AS_dfo;hjhC4jhflasnF3fnd")
    DATA = b's2\0s1\0s1\0[]'
    enc = cipher.encrypt(DATA)
    self.assertEqual(enc, b'\xa3"\xb1-s@\x9f\xa3\xf4\xfc\xf8\n\x03\xf1q\xd2\x0b\x00')
    dec = cipher.decrypt(enc)
    self.assertEqual(dec, DATA)

if __name__ == '__main__':
  unittest.main()
