from abc import ABC, abstractmethod
from enum import Enum

class DATA_TYPE(Enum):
  """Serializable data type."""
  STR = 1,
  BIN = 2,
  LIST = 3,
  LONG = 4,
  STR_REF = 5,
  REF = 6

class Data(ABC):
  """`clData` interface."""
  def __init__(self, type: DATA_TYPE):
    self.type = type

  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def __bytes__(self) -> bytes:
    pass

  @abstractmethod
  def from_buf(self, buf: bytearray):
    """Creates an instance from the buffer."""
    pass
  
class String(Data):
  """`clDataStr` implementation."""
  def __init__(self, string: str = ""):
    super().__init__(DATA_TYPE.STR)
    self.string = string

  def __str__(self):
    return self.string
  
  def __bytes__(self):
    bts = bytearray([0x73])
    bts.extend(bytes(self.string, 'utf8'))
    bts.append(0x00)
    return bytes(bts)
    
  
  def from_buf(buf: bytearray):
    result = String()
    if buf[0] != 0x73: # delimiter
      return None
    buf.pop(0) # s
    while buf[0] != 0x00 and len(buf) > 1:
      result.string += chr(buf.pop(0))
    buf.pop(0) # \0
    return result

class List(Data):
  """`clDataList` implementation."""
  def __init__(self, lst: list[any] = []):
    super().__init__(DATA_TYPE.LIST)
    self.lst = lst

  def __str__(self):
    return str(self.lst)
  
  def __bytes__(self):
    bts = bytearray([0x5B])
    for data in self.lst:
      match str(type(data)):
        case "<class 'str'>":
          bts.extend(bytes(String(data)))
        case "<class 'bytes'>":
          raise NotImplementedError('Binary type serialization not implemented yet')
        case "<class 'list'>":
          bts.extend(bytes(List(data)))
        case "<class 'int'>":
          raise NotImplementedError('Long type serialization not implemented yet')
        case _:
          raise BufferError(f'Unsupported type {type(data)} serialized in list')
    bts.append(0x5D)
    return bytes(bts)
  
  def to_buf(self, outer = True):
    """Serialize list."""
    result = bytearray(bytes(self))
    if not outer:
      return bytes(result)
    # remove outer brackets
    result.pop(0) 
    result.pop()
    return bytes(result)
  
  def from_buf(buf: bytearray, outer = True):
    """Deserialize list."""
    result = List([])
    # [
    if not outer and buf[0] == 0x5B:
      buf.pop(0)

    # ] (empty list)
    if buf[0] == 0x5D:
      buf.pop(0)
      # print(len(result.lst))
      return result
    
    while len(buf) > 1 and buf[0] != 0x5D:
      match(chr(buf[0])):
        case 'b':
          raise NotImplementedError('Binary type not implemented yet')
        case 's':
          result.lst.append(String.from_buf(buf).string)
        case 'L':
          raise NotImplementedError('Long type not implemented yet')
        case '[':
          result.lst.append(List.from_buf(buf, False).lst)
        case _:
          raise BufferError('Corrupted buffer or unknown type delimiter')
    
    # ]
    if not outer and buf[0] == 0x5D:
      buf.pop(0)
    return result
