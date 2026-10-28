import sys, os, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import client, gsm

class BundleTests(unittest.TestCase):
  """Packets with several messages."""
  def test_zero_size_message(self):
    # a second message claiming 0 bytes used to loop forever
    data = bytes([0, 0, 6, 0, 58, 0x24]) + bytes([0, 0, 0, 0, 58, 0x24])
    first = gsm.Message(None, in_buf=data)
    with self.assertRaises(BufferError):
      gsm.GSMessageBundle(first, data[first.header.size:], client.TcpClient((None, None)))

  def test_short_message(self):
    with self.assertRaises(BufferError):
      gsm.Message(None, in_buf=bytes([0, 0, 6]))

  def test_two_keepalives(self):
    data = bytes([0, 0, 6, 1, 58, 0x42]) * 2
    first = gsm.Message(None, in_buf=data)
    bundle = gsm.GSMessageBundle(first, data[first.header.size:], client.TcpClient((None, None)))
    self.assertEqual(len(bundle.msgs), 2)

if __name__ == '__main__':
  unittest.main()
