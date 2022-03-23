from io import BytesIO
import sys
from pico_crypto_key import Device, b64_to_hex_str

def main(device, file):
  encrypted_file = file + ".enc"
  print("[H] encrypt %s" % file)
  with open(file, "rb") as fd:
    data = BytesIO(fd.read())
    data_enc = BytesIO(device.encrypt(data))
    print("[H] decrypt encrypted data")
    data_dec = device.decrypt(data_enc)
    assert data.getbuffer() == data_dec
    print("[H] round-trip ok")

if __name__ == "__main__":
  device = Device("/dev/ttyACM0")
  assert len(sys.argv) == 2
  try:
    main(device, sys.argv[1])
  except Exception as e:
    print(e)
