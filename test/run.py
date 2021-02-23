

from crypto_device import Device
import serial
import test_hash
import test_encryption
import test_sign

test_files = ["./test/test.txt", "./test/test2.txt", "./test/test3.txt", "./test/test4.bin"]

try:
  device = Device("/dev/ttyACM0")

  for file in test_files:
    test_hash.main(device, file)
    test_encryption.main(device, file)
    test_sign.main(device, file)

except Exception as e:
  print(e)

