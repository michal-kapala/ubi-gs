import math

def encrypt(input: bytes):
  """GS XOR encryption algorithm."""
  size = len(input)
  result = bytearray(input)
  for i in range(size):
    result[i] ^= (i - 119) & 0xff

  size_root = int(math.sqrt(size))
  if size_root ** 2 < size:
    size_root += 1

  new_size = 2 * size_root ** 2
  buf = bytearray(new_size)
  for i in range(new_size):
    buf[i] = 0xff

  a = b = 0
  for i in range(size):
    if a < size_root:
      if b < 0:
        b = a
        a = 0
    else:
      a = b + 2
      b = size_root - 1
    buf[a + size_root * b] = result[i]
    a += 1
    b -= 1
  
  idx = 0
  for j in range(size_root):
    for k in range(size_root):
      if buf[k + size_root * j] != 0xff:
        result[idx] = buf[k + size_root * j]
        idx += 1

  return bytes(result)

def decrypt(input: bytes):
  """GS XOR decryption algorithm."""
  size = len(input)
  result = bytearray(input)
  root = math.sqrt(size)
  size_root = int(root)
  if float(size_root) < root:
    size_root += 1
  new_size = size_root ** 2
  buf = bytearray(new_size)

  a = b = 0
  if size > 0:
    size_cpy = size
    while size_cpy > 0:
      if b < size_root:
        if a < 0:
          a = b
          b = 0
      else:
        b = a + 2
        a = size_root - 1
      buf[b + size_root * a] = 1
      a -= 1
      b += 1
      size_cpy -= 1

  c = d = 0
  if size > 0:
    count = 0
    while d < size:
      if c >= size_root:
        count += size_root
        c = 0
      if buf[count + c] > 0:
        buf[count + c] = input[d]
        d += 1
      c += 1
  
  e = f = 0
  for idx in range(size):
    if f < size_root:
      if e < 0:
        e = f
        f = 0
    else:
      f = e + 2
      e = size_root - 1
    result[idx] = buf[f + size_root * e]
    e -= 1
    f += 1

  for i in range(size):
    result[i] ^= (i - 119) & 0xff

  return bytes(result)
