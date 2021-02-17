import os
import sys
import serial
import filecmp
from base64 import b64encode, b64decode
from hashlib import sha256

CHUNK_SIZE = 16384

def encrypt(ser, file):

  with open(file, "rb") as fd:
    print("[H] sending 'e'")
    ser.write(str.encode('e'))

    e = bytearray()
    while True:
      raw = fd.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      print("[H] sending data: %d bytes -> %d bytes" % (len(raw), len(b)))
      ser.write(bytearray(b) + b"\n")
      resp = b64decode(ser.readline())
      e.extend(resp)
    ser.write(b"\n")
    with open(file + ".enc", "wb") as ofd:
      ofd.write(e)

def decrypt(ser, file):

  with open(file, "rb") as fd:
    print("[H] sending 'd'")
    ser.write(str.encode('d'))

    e = bytearray()
    while True:
      raw = fd.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      print("[H] sending data: %d bytes -> %d bytes" % (len(raw), len(b)))
      ser.write(bytearray(b) + b"\n")
      resp = b64decode(ser.readline())
      e.extend(resp)
    ser.write(b"\n")
    with open(file + ".dec", "wb") as ofd:
      ofd.write(e)

def main(ser, file):
  encrypt(ser, file)
  decrypt(ser, file + ".enc")
  assert filecmp.cmp(file, file + ".enc.dec")
  os.remove(file + ".enc")
  os.remove(file + ".enc.dec")


if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  assert len(sys.argv) == 2
  try:
    main(ser, sys.argv[1])
  except Exception as e:
    print(e)
  ser.close()
