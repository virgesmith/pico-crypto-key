

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

  del(device) # resets the device

  device = Device("/dev/ttyACM0")
  device.help()

except Exception as e:
  print("test error: %s" % e)

