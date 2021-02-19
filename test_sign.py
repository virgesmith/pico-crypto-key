import sys
import serial
from base64 import b64encode, b64decode
from hashlib import sha256

CHUNK_SIZE = 16384

def main(ser, file):
  print("[H] 'k'")
  ser.write(str.encode('k'))

  resp = b64decode(ser.readline()).hex()
  print("[D] pubkey:" + resp)

  with open(file, "rb") as fd:
    print("[H] 's' %s" % file)
    ser.write(str.encode('s'))

    hasher = sha256()
    while True:
      raw = fd.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      hasher.update(raw)

      print("[H] %d bytes -> %d bytes" % (len(raw), len(b)))
      ser.write(bytearray(b) + b"\n")
      # resp = ser.readline().decode("utf-8")[:-1]#.strip("\n")
      # print("[D] " + resp)
    ser.write(b"\n")
    print("[H] reading sig")
    resp = b64decode(ser.readline()).hex()
    #resp = ser.readline()
    print("[D] %s" % resp)



if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  assert len(sys.argv) == 2
  try:
    main(ser, sys.argv[1])
  except Exception as e:
    print(e)
  ser.close()

