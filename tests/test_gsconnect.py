import sys, os, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'gsconnect'))
import gsconnect

class GSConnectTests(unittest.TestCase):
  """Tests for the gsconnect web service."""
  def setUp(self):
    self.client = gsconnect.app.test_client()

  def test_homm5_servers(self):
    res = self.client.get('/gsinit.php?dp=HEROES_657d2c2ebadc6a1d')
    self.assertEqual(res.status_code, 200)
    self.assertIn(b'NATServerPort0=7781', res.data)

  def test_missing_game_id(self):
    self.assertEqual(self.client.get('/gsinit.php').status_code, 400)

  def test_unknown_game_id(self):
    self.assertEqual(self.client.get('/gsinit.php?dp=NOPE').status_code, 400)

  def test_debug_off_by_default(self):
    sys.argv = ['gsconnect.py']
    args = gsconnect.get_args()
    self.assertFalse(args.debug)
    self.assertEqual(args.host, '0.0.0.0')

if __name__ == '__main__':
  unittest.main()
