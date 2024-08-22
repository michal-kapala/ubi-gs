import rsa, utils

MAX_RSA_MODULUS_LEN = 128
"""Max length of modulus (n) in bytes."""

PUBLIC_KEY_LEN = 512
"""Public key length in bits."""

class RsaPublicKey:
  """Interface for public RSA key serialization."""
  def __init__(self, bits: int, n: int, e: int):
    self.bits = bits
    self.modulus = n
    self.exponent = e

  def __repr__(self):
    return f"RsaPublicKey({self.modulus}, {self.exponent})"
  
  def from_buf(bts: bytes):
    """Reads the public key from a buffer."""
    key = RsaPublicKey(PUBLIC_KEY_LEN, 0, 0)
    key.bits = utils.read_u32(bts[:4])
    key.modulus = utils.read_bigint_be(bts[4:MAX_RSA_MODULUS_LEN + 4], MAX_RSA_MODULUS_LEN)
    key.exponent = utils.read_bigint_be(bts[MAX_RSA_MODULUS_LEN + 4:2 * MAX_RSA_MODULUS_LEN + 4], MAX_RSA_MODULUS_LEN)
    return key
  
  def __bytes__(self):
    """Writes the public key to a buffer."""
    result = bytearray()
    result.extend(utils.write_u32(self.bits))
    result.extend(utils.write_bigint_be(self.modulus, MAX_RSA_MODULUS_LEN))
    result.extend(utils.write_bigint_be(self.exponent, MAX_RSA_MODULUS_LEN))
    return bytes(result)

  def to_pubkey(self):
    """Conversion to `rsa.PublicKey`."""
    return rsa.PublicKey(self.modulus, self.exponent)
  
  def from_pubkey(key: rsa.PublicKey):
    """Conversion from `rsa.PublicKey`."""
    return RsaPublicKey(PUBLIC_KEY_LEN, key.n, key.e)

def keygen():
  return rsa.newkeys(PUBLIC_KEY_LEN, exponent=3)

def encrypt(data: bytes, key: rsa.PublicKey):
  return rsa.encrypt(data, key)

def decrypt(data: bytes, key: rsa.PrivateKey):
  return rsa.decrypt(data, key)
