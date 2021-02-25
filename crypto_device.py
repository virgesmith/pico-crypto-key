import os
from io import BytesIO
import serial
from base64 import b64encode, b64decode

CHUNK_SIZE = 4096

class Device:

  def __init__(self, dev = "/dev/ttyACM0"):
    if not os.path.exists(dev):
      raise FileNotFoundError("usb device not found")
    self.__device = serial.Serial(dev, 115200)
    pin = os.environ.get("PICO_CRYPTO_KEY_PIN")
    if not pin:
      raise KeyError("PICO_CRYPTO_KEY_PIN not set")
    self.have_repl = False # tracks whether repl entered (i.e. pin was correct)
    self.__device.write(str.encode(pin) + b"\n")
    resp = self.__device.readline().rstrip()
    if resp != b'pin ok':
      raise ValueError("PICO_CRYPTO_KEY_PIN incorrect")
    self.have_repl = True

  def __del__(self):
    if hasattr(self, "device"):
      self.reset()
      self.__device.close()

  def __hash(self, file):
    with open(file, "rb") as fd:
      while True:
        raw = fd.read(CHUNK_SIZE)
        if not raw: break
        b = b64encode(raw)
        self.__device.write(bytearray(b) + b"\n")
      self.__device.write(b"\n")
      return self.__device.readline().rstrip()

  def help(self):
    self.__device.write(str.encode('H'))
    while True:
      l = self.__device.readline().rstrip()
      print(l.decode("utf-8"))
      if l == b'': break

  def hash(self, file):
    self.__device.write(str.encode('h'))
    return self.__hash(file)

  def encrypt(self, data: BytesIO) -> bytearray:

    self.__device.write(str.encode('e'))
    data_enc = bytearray()
    while True:
      raw = data.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      self.__device.write(bytearray(b) + b"\n")
      resp = b64decode(self.__device.readline())
      data_enc.extend(resp)
    self.__device.write(b"\n")
    return data_enc

  def decrypt(self, data: BytesIO) -> bytearray:
    # This returns garbage if the device isn't the one that encrypted it
    self.__device.write(str.encode('d'))
    data_dec = bytearray()
    while True:
      raw = data.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      self.__device.write(bytearray(b) + b"\n")
      resp = b64decode(self.__device.readline())
      data_dec.extend(resp)
    self.__device.write(b"\n")
    return data_dec

  def sign(self, file):
    self.__device.write(str.encode('s'))
    hash = self.__hash(file)
    sig = self.__device.readline().rstrip()
    return (hash, sig)

  def verify(self, hash, sig, pubkey):
    """
    return value:
    0:      successfully verified
    -19968: not verified
    any other value means something else went wrong e.g. data formats are incorrect
    """
    self.__device.write(str.encode('v'))
    self.__device.write(hash + b"\n")
    self.__device.write(sig + b"\n")
    self.__device.write(pubkey + b"\n")
    return int(self.__device.readline().rstrip())

  def pubkey(self):
    self.__device.write(str.encode('k'))
    pubkey = self.__device.readline().rstrip()
    return pubkey

  def reset(self):
    # ony reset if we have repl
    if self.have_repl:
      self.__device.write(str.encode('r'))

def b64_to_hex_str(b64bytes):
  return b64decode(b64bytes).hex()

def hex_str_to_b64(hex_str):
  return b64encode(bytes.fromhex(hex_str))