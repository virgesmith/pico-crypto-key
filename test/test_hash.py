import sys
from hashlib import sha256
from pico_crypto_key import Device, b64_to_hex_str

def main(device, file):

    print("[H] hash %s" % file)
    hash = b64_to_hex_str(device.hash(file))
    print("[D] " + hash)

    with open(file, "rb") as fd:
      hash2 = sha256(fd.read()).hexdigest()

    # check hash matches haslib's sha256
    assert hash == hash2

if __name__ == "__main__":
  device = Device("/dev/ttyACM0")
  assert len(sys.argv) == 2
  try:
    main(device, sys.argv[1])
  except Exception as e:
    print(e)
