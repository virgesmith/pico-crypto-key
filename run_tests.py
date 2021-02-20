
import serial
import test_hash
import test_encryption
import test_sign

ser = serial.Serial("/dev/ttyACM0", 115200)

test_files = ["./test.txt", "./test2.txt", "./test3.txt", "./test4.bin"]

for file in test_files:
  test_hash.main(ser, file)
  test_encryption.main(ser, file)
  test_sign.main(ser, file)

ser.close()

