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

  def __del__(self):
    if hasattr(self, "device"):
      print("closing serial connection")
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
    self.device.write(str.encode('v'))
    self.device.write(hash + b"\n")
    self.device.write(sig + b"\n")
    self.device.write(pubkey + b"\n")
    result = int(self.device.readline().rstrip())
    return (result == 0, result)

  def pubkey(self):
    self.device.write(str.encode('k'))
    pubkey = self.device.readline().rstrip()
    return pubkey #b64decode(pubkey).hex()
    #print("[D] pubkey: %s" % )

def b64_to_hex_str(b64bytes):
  return b64decode(b64bytes).hex()
