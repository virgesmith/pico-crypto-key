import os
import sys
import filecmp
from crypto_device import Device, b64_to_hex_str
#from base64 import b64encode, b64decode

# def encrypt(ser, file):

#   with open(file, "rb") as fd:
#     print("[H] sending 'e'")
#     ser.write(str.encode('e'))

#     e = bytearray()
#     while True:
#       raw = fd.read(CHUNK_SIZE)
#       if not raw: break
#       b = b64encode(raw)
#       print("[H] sending data: %d bytes -> %d bytes" % (len(raw), len(b)))
#       ser.write(bytearray(b) + b"\n")
#       resp = b64decode(ser.readline())
#       e.extend(resp)
#     ser.write(b"\n")
#     with open(file + ".enc", "wb") as ofd:
#       ofd.write(e)

# def decrypt(ser, file):

#   with open(file, "rb") as fd:
#     print("[H] sending 'd'")
#     ser.write(str.encode('d'))

#     e = bytearray()
#     while True:
#       raw = fd.read(CHUNK_SIZE)
#       if not raw: break
#       b = b64encode(raw)
#       print("[H] sending data: %d bytes -> %d bytes" % (len(raw), len(b)))
#       ser.write(bytearray(b) + b"\n")
#       resp = b64decode(ser.readline())
#       e.extend(resp)
#     ser.write(b"\n")
#     with open(file + ".dec", "wb") as ofd:
#       ofd.write(e)

def main(device, file):
  encrypted_file = file + ".enc"
  print("[H] encrypt %s -> %s" % (file, encrypted_file))
  device.encrypt(file)
  decrypted_file = encrypted_file + ".dec"
  print("[H] decrypt %s -> %s" % (encrypted_file,  decrypted_file))
  device.decrypt(file + ".enc")
  assert filecmp.cmp(file, file + ".enc.dec")
  print("[H] ok, removing %s, %s" % (encrypted_file,  decrypted_file))
  os.remove(file + ".enc")
  os.remove(file + ".enc.dec")


if __name__ == "__main__":
  device = Device("/dev/ttyACM0")
  assert len(sys.argv) == 2
  try:
    main(device, sys.argv[1])
  except Exception as e:
    print(e)
