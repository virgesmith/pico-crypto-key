from __future__ import annotations

from types import TracebackType
from typing import Any
import os
from io import BytesIO
import serial  # type: ignore
from base64 import b64encode, b64decode

CHUNK_SIZE = 4096

class CryptoKey:

  def __init__(self, *, device: str, pin: str) -> None:
    self.have_repl = False # tracks whether repl entered (i.e. pin was correct)
    self.device_path = device
    self.device_pin = pin
    self.__device: Any = None

  def __enter__(self) -> "CryptoKey":
    self.reset()
    return self

  def __exit__(self, exc_type: type[BaseException] | None,
                     exc_value: BaseException | None,
                     _exc_stack: TracebackType | None) -> None:
    # print("CryptoKey.__exit__")
    if exc_type:
      print(f"{exc_type.__name__}: {exc_value}")
    # if self.have_repl:
    #   self.reset()
    self.__device.close()

  def __hash(self, file: str) -> bytes:
    with open(file, "rb") as fd:
      while True:
        raw = fd.read(CHUNK_SIZE)
        if not raw: break
        b = b64encode(raw)
        self.__device.write(bytearray(b) + b"\n")
      self.__device.write(b"\n")
      return self.__device.readline().rstrip()

  def help(self) -> None:
    self.__device.write(str.encode('H'))
    while True:
      l = self.__device.readline().rstrip()
      print(l.decode("utf-8"))
      if l == b'': break

  def hash(self, file: str) -> bytes:
    assert self.have_repl
    self.__device.write(str.encode('h'))
    return self.__hash(file)

  def encrypt(self, data: BytesIO) -> bytearray:
    assert self.have_repl
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
    assert self.have_repl
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

  def sign(self, file: str) -> tuple[bytes, bytes]:
    assert self.have_repl
    self.__device.write(str.encode('s'))
    hash = self.__hash(file)
    sig = self.__device.readline().rstrip()
    return (hash, sig)

  def verify(self, hash: bytes, sig: bytes, pubkey: bytes) -> int:
    """
    return value:
    0:      successfully verified
    -19968: not verified
    any other value means something else went wrong e.g. data formats are incorrect
    """
    assert self.have_repl
    self.__device.write(str.encode('v'))
    self.__device.write(hash + b"\n")
    self.__device.write(sig + b"\n")
    self.__device.write(pubkey + b"\n")
    return int(self.__device.readline().rstrip())

  def pubkey(self) -> bytes:
    assert self.have_repl
    self.__device.write(str.encode('k'))
    pubkey = self.__device.readline().rstrip()
    return pubkey

  def reset(self) -> None:
    # only send reset request if we have repl
    if self.have_repl:
      self.__device.write(str.encode('r'))
      self.have_repl = False
    if not os.path.exists(self.device_path):
      raise FileNotFoundError("usb device not found")
    self.__device = serial.Serial(self.device_path, 115200)
    self.__device.write(str.encode(self.device_pin) + b"\n")
    resp = self.__device.readline().rstrip()
    if resp != b'pin ok':
      raise ValueError("pin incorrect")
    self.have_repl = True


def b64_to_hex_str(b64bytes: bytes) -> str:
  return b64decode(b64bytes).hex()

def hex_str_to_b64(hex_str: str) -> bytes:
  return b64encode(bytes.fromhex(hex_str))