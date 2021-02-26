# use case 4:
# print the device "API" help

from crypto_device import Device

if __name__ == "__main__":
  device = Device("/dev/ttyACM0")
  device.help()

