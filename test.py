import sys
import serial
from base64 import b64encode, b64decode
from hashlib import sha256

def main(ser, file):

  with open(file, "rb") as fd:
    raw = fd.read()
    b = b64encode(raw)
    h = sha256(raw).hexdigest()

    print("[H] sending 'h'")
    ser.write(str.encode('h'))

    print("[H] sending data: %d bytes -> %d bytes" % (len(raw), len(b)))
    ser.write(bytearray(b) + b"\n")
    resp = ser.readline().decode("utf-8")[:-1]#.strip("\n")
    print("[D] " + resp)

    print("[H] reading hash")
    resp = b64decode(ser.readline()).hex() #encode("utf-8") #.hex() # read(n)
    print("[D] " + resp)
    print("[H] " + h)
    assert resp == h

if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  assert len(sys.argv) == 2
  try:
    main(ser, sys.argv[1])
  except Exception as e:
    print(e)
  ser.close()
