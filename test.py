import sys
import serial

# test.txt: works
# test2.txt: wrong hash
# comms.h : wrong hash
# test.py: hangs
# CMakeLists.txt: wrong hash, then hangs

def main(ser, file):

  fd = open(file, "rb")
  b = bytearray(fd.read())

  print("[H] sending 'h'")
  ser.write(str.encode('h'))

  print("[H] sending size")
  ser.write(len(b).to_bytes(4, byteorder='little'))
  resp = ser.readline().decode("utf-8")[:-1]#.strip("\n")
  print("[D] " + resp)
  resp = ser.readline().decode("utf-8")[:-1]#.strip("\n")
  print("[D] " + resp)

  print("[H] sending data")
  ser.write(b)
  resp = ser.readline().decode("utf-8")[:-1]#.strip("\n")
  print("[D] " + resp)

  print("[H] reading hash")
  resp = ser.readline().decode("utf-8") # read(n)
  print("[D] " + resp)

  ser.flushInput()
  ser.flushOutput()


if __name__ == "__main__":
  ser = serial.Serial("/dev/ttyACM0", 115200)
  main(ser, sys.argv[1])
  ser.close()
