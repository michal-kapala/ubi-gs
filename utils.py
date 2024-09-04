import array, socket

def read_u16_be(bts: bytes):
  """Reads a big endian u16."""
  return (bts[0] << 8) + bts[1]

def write_u16_be(number: int):
  """Serializes 16-bit integer into a BE buffer."""
  return number.to_bytes(2, 'big')

def write_u16(number: int):
  """Serializes 16-bit integer into a LE buffer."""
  return number.to_bytes(2, 'little')

def read_as_i16_list(bts: bytes):
  """Converts a LE buffer into a list of i16."""
  if len(bts) % 2 != 0:
    raise BufferError("Unpadded buffer cast to i16 list.")
  arr = array.array('h')
  arr.frombytes(bts)
  return arr.tolist()

def write_u24_be(number: int):
  """Serializes 24-bit integer into a LE buffer."""
  return number.to_bytes(3, 'big')

def read_as_u32_list(bts: bytes):
  """Converts a LE buffer into a list of u32."""
  result: list[int] = []
  size = len(bts)
  if size % 4 != 0:
    raise BufferError("Unpadded buffer cast to u32 list.")
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

def read_u32(bts: bytes):
  """Reads a little endian u32."""
  return bts[0] + (bts[1] << 8) + (bts[2] << 16) + (bts[3] << 24)

def write_u32(number: int):
  """Writes a little endian u32."""
  return number.to_bytes(4, 'little')

def read_u32_be(bts: bytes):
  """Reads a big endian u32."""
  return (bts[0] << 24) + (bts[1] << 16) + (bts[2] << 8) + bts[3]

def write_u32_be(nb: int):
  """Writes a big endian u32."""
  return bytes([(nb >> 24) & 0xFF, (nb >> 16) & 0xFF, (nb >> 8) & 0xFF, nb & 0xFF])

def read_bigint_be(bts: bytes, size: int):
  """Reads an arbitrarily large big-endian uint from the buffer."""
  if len(bts) < size:
    raise BufferError(f'Buffer too small ({len(bts)}B < {size}B).')
  
  rev = bytearray(bts)
  rev.reverse()
  result = 0
  for i in range(size):
    result += rev[i] << (i * 8)
  return result

def write_bigint_be(bigint: int, size: int):
  """Writes an arbitrarily large big-endian uint to the buffer."""
  return bigint.to_bytes(size, 'big')

def ipv4_to_u32(ip: str):
  """Converts IPv4 address into integer representation."""
  result = socket.inet_aton(ip)
  return read_u32(result)
