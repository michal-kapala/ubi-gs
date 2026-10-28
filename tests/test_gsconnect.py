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

  def test_expansion_servers(self):
    # gsinit ids of Hammers of Fate 2.1 and Tribes of the East 3.1 (the `dp` their H5_Game.exe sends)
    for dp in ['HEROES_f4609f85d388479e', 'HEROES_29988429c481f219']:
      res = self.client.get(f'/gsinit.php?dp={dp}')
      self.assertEqual(res.status_code, 200, dp)
      self.assertIn(b'RouterPort0=7777', res.data)

  def test_no_debugger_console(self):
    self.assertEqual(self.client.get('/console').status_code, 400)
    self.assertFalse(gsconnect.app.debug)

  def test_missing_game_id(self):
    self.assertEqual(self.client.get('/gsinit.php').status_code, 400)

  def test_unknown_game_id(self):
    self.assertEqual(self.client.get('/gsinit.php?dp=NOPE').status_code, 400)

  def test_debug_off_by_default(self):
    sys.argv = ['gsconnect.py']
    args = gsconnect.get_args()
    self.assertFalse(args.debug)
    self.assertEqual(args.host, '0.0.0.0')
    self.assertEqual(args.port, 80)

  def test_env_overrides(self):
    sys.argv = ['gsconnect.py']
    os.environ['GSCONNECT_HOST'], os.environ['GSCONNECT_PORT'] = '127.0.0.1', '8080'
    try:
      args = gsconnect.get_args()
    finally:
      del os.environ['GSCONNECT_HOST'], os.environ['GSCONNECT_PORT']
    self.assertEqual((args.host, args.port), ('127.0.0.1', 8080))

if __name__ == '__main__':
  unittest.main()
