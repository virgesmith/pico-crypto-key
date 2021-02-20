import sys
import serial
from base64 import b64encode, b64decode
from hashlib import sha256

CHUNK_SIZE = 16384

def main(ser, file):
  print("[H] 'k'")
  ser.write(str.encode('k'))
  pubkey = b64decode(ser.readline()).hex()
  #pubkey = ser.readline().decode("utf-8")[:-1]
  print("[D] pubkey: %s" % pubkey)

  with open(file, "rb") as fd:
    print("[H] 's' %s" % file)
    ser.write(str.encode('s'))

    while True:
      raw = fd.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      ser.write(bytearray(b) + b"\n")
    ser.write(b"\n")
    hash = b64decode(ser.readline()).hex()
    print("[D] hash: " + hash)
    print("[H] reading sig")
    sig = b64decode(ser.readline())#.hex()
    print("[D] sig: %s" % sig.hex())

    # # verify
    # ser.write(str.encode('v'))
    # ser.write(hash + b"\n")
    # ser.write(sig + b"\n")
    # ser.write(pubkey + b"\n")



if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  assert len(sys.argv) == 2
  try:
    main(ser, sys.argv[1])
  except Exception as e:
    print(e)
  ser.close()

