import os
import sys
import toml
sys.path.append(".")

from crypto_device import Device
import test_hash
import test_encryption
import test_sign

test_files = ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"]

# TODO use pytest

def main(device_path):
  device = Device(device_path)

  for file in test_files:
    test_hash.main(device, file)
    test_encryption.main(device, file)
    test_sign.main(device, file)

  del(device) # resets the device

  print()
  device = Device(device_path)
  device.help()


if __name__ == "__main__":
  try:
    config = toml.load("./config.toml")["run"]

    os.environ["PICO_CRYPTO_KEY_PIN"] = config["PICO_CRYPTO_KEY_PIN"]
    main(config["DEST_SERIAL"])

  except Exception as e:
    print("test error: %s" % e)

