import os
from io import BytesIO
import serial
from base64 import b64encode, b64decode

CHUNK_SIZE = 4096

class Device:

  def __init__(self, dev = "/dev/ttyACM0"):
    if not os.path.exists(dev):
      raise FileNotFoundError("usb device not found")
    self.device = serial.Serial(dev, 115200)
    pin = os.environ.get("PICO_CRYPTO_KEY_PIN")
    if not pin:
      raise KeyError("PICO_CRYPTO_KEY_PIN not set")
    print("[H] pin '%s'" % pin)
    self.have_repl = False # tracks whether repl entered (i.e. pin was correct)
    self.device.write(str.encode(pin) + b"\n")
    resp = self.device.readline().rstrip()
    if resp != b'pin ok':
      raise ValueError("PICO_CRYPTO_KEY_PIN incorrect")
    self.have_repl = True


  def __del__(self):
    # ony reset if we have repl
    if hasattr(self, "device") and self.have_repl:
      self.device.write(str.encode('r'))
      self.device.close()

  def __hash(self, file):
    with open(file, "rb") as fd:
      while True:
        raw = fd.read(CHUNK_SIZE)
        if not raw: break
        b = b64encode(raw)
        self.device.write(bytearray(b) + b"\n")
      self.device.write(b"\n")
      return self.device.readline().rstrip()

  def hash(self, file):
    self.device.write(str.encode('h'))
    return self.__hash(file)

  def encrypt(self, data: BytesIO) -> bytearray:

    self.device.write(str.encode('e'))
    data_enc = bytearray()
    while True:
      raw = data.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      self.device.write(bytearray(b) + b"\n")
      resp = b64decode(self.device.readline())
      data_enc.extend(resp)
    self.device.write(b"\n")
    return data_enc
    # with open(file + ".enc", "wb") as ofd:
    #   ofd.write(e)

  def decrypt(self, data: BytesIO) -> bytearray:
    # This returns garbage if the device isn't the one that encrypted it

    self.device.write(str.encode('d'))
    data_dec = bytearray()
    while True:
      raw = data.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      self.device.write(bytearray(b) + b"\n")
      resp = b64decode(self.device.readline())
      data_dec.extend(resp)
    self.device.write(b"\n")
    return data_dec

  def sign(self, file):
    self.device.write(str.encode('s'))
    hash = self.__hash(file)
    sig = self.device.readline().rstrip()
    return (hash, sig)

  def verify(self, hash, sig, pubkey):
    """
    return value:
    0:      successfully verified
    -19968: not verified
    any other value means something else went wrong e.g. data formats are incorrect
    """
    self.device.write(str.encode('v'))
    self.device.write(hash + b"\n")
    self.device.write(sig + b"\n")
    self.device.write(pubkey + b"\n")
    return int(self.device.readline().rstrip())

  def pubkey(self):
    self.device.write(str.encode('k'))
    pubkey = self.device.readline().rstrip()
    return pubkey

def b64_to_hex_str(b64bytes):
  return b64decode(b64bytes).hex()

def hex_str_to_b64(hex_str):
  return b64encode(bytes.fromhex(hex_str))