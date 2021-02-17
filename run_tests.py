
import serial
from test import main

ser = serial.Serial("/dev/ttyACM0", 115200)

main(ser, "./test.txt")
main(ser, "./test2.txt")
main(ser, "./test3.txt")
main(ser, "./test4.bin")

ser.close()

