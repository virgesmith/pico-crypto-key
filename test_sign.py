import sys
import serial
from base64 import b64encode, b64decode
from hashlib import sha256

CHUNK_SIZE = 16384

wrong_hash = b'S1L93ZmizMM7zScSFiQDqdWzF3FYj0SACivbiiY/Bdk='
wrong_sig = b'MEQCIFSHjtLevnv268DYt57j0zbXThO/RtpxBC6kaW6a1B2aAiBl71b4mEH5yUMGkPpMwFAF/XZ+2//LABB0puHi19HvKg=='
wrong_pubkey = b'BPqvnhfp83ao7n2oWpwIPBW2TBH6LylpG32Rab10n0qUXjzJ4cLdaZY2+n94KQ7PZsvx+iigW62xL/vru2D0Jn4='


def main(ser, file):
  print("[H] 'k'")
  ser.write(str.encode('k'))
  pubkey = ser.readline().rstrip()
  print("[D] pubkey: %s" % b64decode(pubkey).hex())

  with open(file, "rb") as fd:
    print("[H] 's' %s" % file)
    ser.write(str.encode('s'))

    while True:
      raw = fd.read(CHUNK_SIZE)
      if not raw: break
      b = b64encode(raw)
      ser.write(bytearray(b) + b"\n")
    ser.write(b"\n")
    hash = ser.readline().rstrip()
    print("[D] hash: " + b64decode(hash).hex())
    print("[H] reading sig")
    sig = ser.readline().rstrip()
    print("[D] sig: %s" % b64decode(sig).hex())

    # verify
    ser.write(str.encode('v'))
    ser.write(hash + b"\n")
    ser.write(sig + b"\n")
    ser.write(pubkey + b"\n")
    ok = int(ser.readline().rstrip())
    assert ok == 0
    print("[D] verify: %s" % ok)

    # wrong hash
    ser.write(str.encode('v'))
    ser.write(wrong_hash + b"\n")
    ser.write(sig + b"\n")
    ser.write(pubkey + b"\n")
    ok = int(ser.readline().rstrip())
    assert ok != 0
    print("[D] verify: %s" % ok)

    # wrong sig
    ser.write(str.encode('v'))
    ser.write(hash + b"\n")
    ser.write(wrong_sig + b"\n")
    ser.write(pubkey + b"\n")
    ok = int(ser.readline().rstrip())
    assert ok != 0
    print("[D] verify: %s" % ok)

    # wrong pubkey
    ser.write(str.encode('v'))
    ser.write(hash + b"\n")
    ser.write(sig + b"\n")
    ser.write(wrong_pubkey + b"\n")
    ok = int(ser.readline().rstrip())
    assert ok != 0
    print("[D] verify: %s" % ok)


if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  assert len(sys.argv) == 2
  try:
    main(ser, sys.argv[1])
  except Exception as e:
    print(e)
  ser.close()

