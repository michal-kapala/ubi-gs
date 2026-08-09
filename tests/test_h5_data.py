import sys, os, unittest
# relative module import stuff
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
import h5_data, utils

class H5_SerializerTests(unittest.TestCase):
  """Tests for `H5_RoomInfo` data buffer serialization."""
  def test_serialize(self):
    ref_buf = b"\x04\x08\x04\x00\x00\x00\x01%\x03\x00\x00\x02\x08\xff\xff\xff\xff\x03\x08\xff\xff\xff\xff\x04$\x02 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x02\x00\x070m\x00i\x00m\x00a\x00k\x00'\x00s\x00 \x00G\x00a\x00m\x00e\x00\x08,t\x00h\x00e\x00p\x00a\x00s\x00s\x00w\x00o\x00r\x00d\x00\t\x02\x01\n\x02\x00\x0b\x02\x00\x0c\x02\x00\r\x08\xff\xff\xff\xff\x0e\x08\x01\x00\x00\x00\x0ff\x02b/Maps/Multiplayer/L4/L4.xdb#xpointer(/AdvMapDesc)\x13@\x01\x08\x06\x00\x00\x00\x020\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x14\x08\x06\x00\x00\x00\x15\x08\x03\x00\x00\x00\x16\x18\x03\x08\x00\x00\x00\x00\x04\x08\r\x00\x00\x00\x17\x08<\x00\x01\x00\x18\x02\x00\x19 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x02\x00\x1bT\x03\x08\x01\x00\x00\x00\x04\x08\r\x00\x00\x00\x01 autosave_enabled\x02\x14\x02\x08\x00\x00\x00\x00\x03\x040\x00\x1c\x02\x00\x1d\x08\xb1\xaf\xdd\xc8\x1e\x08\x01\x00\x00\x00\x1fv\x02r/Maps/Multiplayer/L4/map-tag.xdb#xpointer(/AdvMapDescTag) \ngoal3!\x00%\x08\x00\x00\x00\x00&\x08\x00\x00\x00\x00'\x08\x00\x00\x00\x00(\x02\x00\x00\x00\x02\x00\x05\x00"
    info = h5_data.H5_RoomInfo()
    info.group_id = -1
    info.lobby_srv_id = -1
    info.host_ip = "0.0.0.0"
    info.host_logic_init = False
    info.group_name = "mimak's Game"
    info.password = "thepassword"
    info.is_pwd_protected = True
    info.ghost_mode = False
    info.quick_combat = False
    info.fast_combat_turns = False
    info.time_limit = -1
    info.difficulty_id = 1
    info.map_desc = "/Maps/Multiplayer/L4/L4.xdb#xpointer(/AdvMapDesc)"
    info.teams = [1, 1, 1, 1, 1, 1]
    info.max_players = 6
    info.map_size = 3
    info.player_infos = []
    info.game_version = 0x1003C # 1.60
    info.is_saved = False
    info.some_ip = "0.0.0.0"
    info.ubi_send_results_wait = False
    info.options = {"autosave_enabled": (0, "0")}
    info.is_arena = False
    info.host_checksum = 0xC8DDAFB1
    info.adventure_type = 1
    info.map_desc_tag = "/Maps/Multiplayer/L4/map-tag.xdb#xpointer(/AdvMapDescTag)"
    info.map_goal = "goal3"
    info.arena_map_name = ""
    info.int104 = 0
    info.int108 = 0
    info.combat_turn_speed = 0
    info.flag110 = False

    buf = h5_data.H5_Serializer().serialize_roominfo(info)
    self.assertEqual(buf, ref_buf)

  def test_deserialize(self):
    data = b"\x04\x08\x04\x00\x00\x00\x01\xf9\x02\x00\x00\x02\x08\xe8\x03\x00\x00\x03\x08\x01\x00\x00\x00\x04$\x02 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x02\x01\x070m\x00i\x00m\x00a\x00k\x00'\x00s\x00 \x00G\x00a\x00m\x00e\x00\x08\x00\t\x02\x00\n\x02\x00\x0b\x02\x00\x0c\x02\x00\r\x08\xff\xff\xff\xff\x0e\x08\x01\x00\x00\x00\x0ff\x02b/Maps/Multiplayer/L4/L4.xdb#xpointer(/AdvMapDesc)\x13@\x01\x08\x06\x00\x00\x00\x020\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x14\x08\x06\x00\x00\x00\x15\x08\x03\x00\x00\x00\x16\x18\x03\x08\x00\x00\x00\x00\x04\x08\r\x00\x00\x00\x17\x08<\x00\x01\x00\x18\x02\x00\x19 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x02\x00\x1bT\x03\x08\x01\x00\x00\x00\x04\x08\r\x00\x00\x00\x01 autosave_enabled\x02\x14\x02\x08\x00\x00\x00\x00\x03\x040\x00\x1c\x02\x00\x1d\x08\xb1\xaf\xdd\xc8\x1e\x08\x01\x00\x00\x00\x1fv\x02r/Maps/Multiplayer/L4/map-tag.xdb#xpointer(/AdvMapDescTag) \ngoal3!\x00%\x08\x00\x00\x00\x00&\x08\x00\x00\x00\x00'\x08\x00\x00\x00\x00(\x02\x00\x00\x00\x02\x00\x05\x00"
    serializer = h5_data.H5_Serializer()
    room_info = serializer.deserialize_roominfo(data)

    # top-level streams, as-written order
    stream_serial_mode = serializer.streams[h5_data.H5_STREAM_TYPE.SERIALIZATION_MODE.name]
    self.assertEqual(stream_serial_mode.size_4b, False)
    self.assertEqual(stream_serial_mode.size, 4)
    self.assertEqual(utils.read_u32(stream_serial_mode.data), 4)

    stream = serializer.streams[h5_data.H5_STREAM_TYPE.COMPRESSED_DATA.name]
    self.assertEqual(stream.size_4b, True)
    self.assertEqual(stream.size, 380)

    stream = serializer.streams[h5_data.H5_STREAM_TYPE.STRUCTURE.name]
    self.assertEqual(stream.size_4b, False)
    self.assertEqual(stream.size, 0)

    stream = serializer.streams[h5_data.H5_STREAM_TYPE.RAW_DATA.name]
    self.assertEqual(stream.size_4b, False)
    self.assertEqual(stream.size, 0)

    stream = serializer.streams[h5_data.H5_STREAM_TYPE.LOOKUP_TABLE.name]
    self.assertEqual(stream.size_4b, False)
    self.assertEqual(stream.size, 0)

    self.assertRaises(KeyError, lambda: serializer.streams[h5_data.H5_STREAM_TYPE.METADATA.name])

    # data
    self.assertEqual(room_info.group_id, 1000)
    self.assertEqual(room_info.lobby_srv_id, 1)
    self.assertEqual(room_info.host_ip, "0.0.0.0")
    self.assertEqual(room_info.host_logic_init, True)
    self.assertEqual(room_info.group_name, "mimak's Game")
    self.assertEqual(room_info.password, "")
    self.assertEqual(room_info.is_pwd_protected, False)
    self.assertEqual(room_info.ghost_mode, False)
    self.assertEqual(room_info.quick_combat, False)
    self.assertEqual(room_info.fast_combat_turns, False)
    self.assertEqual(room_info.time_limit, -1)
    self.assertEqual(room_info.difficulty_id, 1)
    self.assertEqual(room_info.map_desc, "/Maps/Multiplayer/L4/L4.xdb#xpointer(/AdvMapDesc)")
    self.assertEqual(room_info.teams, [1, 1, 1, 1, 1, 1])
    self.assertEqual(room_info.max_players, 6)
    self.assertEqual(room_info.map_size, 3)
    self.assertEqual(room_info.player_infos, [])
    self.assertEqual(room_info.game_version, 0x1003C) # 1.60
    self.assertEqual(room_info.is_saved, False)
    self.assertEqual(room_info.some_ip, "0.0.0.0")
    self.assertEqual(room_info.ubi_send_results_wait, False)
    self.assertEqual(room_info.options, {"autosave_enabled": (0, "0")})
    self.assertEqual(room_info.is_arena, False)
    self.assertEqual(room_info.host_checksum, 0xC8DDAFB1)
    self.assertEqual(room_info.adventure_type, 1)
    self.assertEqual(room_info.map_desc_tag, "/Maps/Multiplayer/L4/map-tag.xdb#xpointer(/AdvMapDescTag)")
    self.assertEqual(room_info.map_goal, "goal3")
    self.assertEqual(room_info.arena_map_name, "")
    self.assertEqual(room_info.int104, 0)
    self.assertEqual(room_info.int108, 0)
    self.assertEqual(room_info.combat_turn_speed, 0)
    self.assertEqual(room_info.flag110, False)

  def test_e2e(self):
    input = b'\x04\x08\x04\x00\x00\x00\x01{\x03\x00\x00\x02\x08\xe8\x03\x00\x00\x03\x08\x01\x00\x00\x00\x04$\x02 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x02\x01\x070m\x00i\x00m\x00a\x00k\x00\'\x00s\x00 \x00G\x00a\x00m\x00e\x00\x08\x00\t\x02\x00\n\x02\x00\x0b\x02\x00\x0c\x02\x00\r\x08\xff\xff\xff\xff\x0e\x08\x01\x00\x00\x00\x0ff\x02b/Maps/Multiplayer/L4/L4.xdb#xpointer(/AdvMapDesc)\x13@\x01\x08\x06\x00\x00\x00\x020\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x14\x08\x06\x00\x00\x00\x15\x08\x03\x00\x00\x00\x16\x9a\x03\x08\x01\x00\x00\x00\x04\x08\r\x00\x00\x00\x01\x08\x00\x00\x00\x00\x02r\x02\nmimak\x03$\x02 \x02\x00\x1ee\x01\x00\x00\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x04,\x02\x04\xb8"\x03 \xc0\xa8\x05i\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x08\xff\xff\xff\xff\x17\x08<\x00\x01\x00\x18\x02\x00\x19 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x02\x00\x1bT\x03\x08\x01\x00\x00\x00\x04\x08\r\x00\x00\x00\x01 autosave_enabled\x02\x14\x02\x08\x00\x00\x00\x00\x03\x040\x00\x1c\x02\x00\x1d\x08\xb1\xaf\xdd\xc8\x1e\x08\x01\x00\x00\x00\x1fv\x02r/Maps/Multiplayer/L4/map-tag.xdb#xpointer(/AdvMapDescTag) \ngoal3!\x00%\x08\x00\x00\x00\x00&\x08\x00\x00\x00\x00\'\x08\x00\x00\x00\x00(\x02\x00\x00\x00\x02\x00\x05\x00'
    print("input:")
    print(input.hex(' '))
    info = h5_data.H5_Serializer().deserialize_roominfo(input)
    output = h5_data.H5_Serializer().serialize_roominfo(info)
    print("output:")
    print(output.hex(' '))
    self.assertEqual(input, output)

if __name__ == '__main__':
  unittest.main()
