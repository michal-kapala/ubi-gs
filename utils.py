def write_u16(number: int):
  """Serializes 16-bit integer into a LE buffer."""
  return number.to_bytes(2, 'little')
