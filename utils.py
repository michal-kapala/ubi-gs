def write_u16(number: int):
  """Serializes 16-bit integer into a LE buffer."""
  return number.to_bytes(2, 'little')

def read_as_u32_list(bts: bytes):
  """Converts a LE buffer into a list of u32."""
  result: list[int] = []
  if len(bts) % 4 != 0:
    raise BufferError("Unpadded buffer cast to u32 list.")
  size = len(bts)
  for i in range(0, size, 4):
    nb = (bts[i] & 0xFF) + ((bts[i+1] << 8) & 0xff00) + ((bts[i+2] << 16) & 0xff0000) + ((bts[i+3] << 24) & 0xff000000)
    result.append(nb)
  return result

def write_u32_list(ints: list[int]):
  """Serializes u32 list into a LE buffer."""
  bts = bytearray()
  for i in ints:
    bts.append(i & 0xff)
    bts.append((i >> 8) & 0xff)
    bts.append((i >> 16) & 0xff)
    bts.append((i >> 24) & 0xff)
  return bytes(bts)
