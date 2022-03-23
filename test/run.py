import toml

from pico_crypto_key import CryptoKey
import test_hash
import test_encryption
import test_sign

test_files = ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"]

# TODO use pytest...

def main(device_path: str, pin: str) -> None:
  with CryptoKey(device=device_path, pin=pin) as device:

    for file in test_files:
      test_hash.main(device, file)
      test_encryption.main(device, file)
      test_sign.main(device, file)

    device.help()


if __name__ == "__main__":
  try:
    config = toml.load("./config.toml")["run"]

    main(config["DEST_SERIAL"], config["PICO_CRYPTO_KEY_PIN"])

  except Exception as e:
    print("test error: %s" % e)

