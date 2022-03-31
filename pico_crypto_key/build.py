# pico-crypto-key builder

import os
import subprocess
from pathlib import Path
import toml
import shutil


def build(config: dict) -> None:

  # check build dir exists and create if necessary
  build_dir = Path("./build")
  if not build_dir.exists():
    build_dir.mkdir()

  sdk_dir = Path(f"../pico-sdk-{config['PICO_SDK_VERSION']}")

  # assumes SDK level with project dir and tinyusb present
  cmake_args = [
    f"-DPICO_SDK_PATH={sdk_dir.resolve()}",
    f"-DMBED_TLS_VERSION={config['MBED_TLS_VERSION']}",
    f"-DPICO_IMAGE={config['PICO_IMAGE']}"
  ]

  # check we have pico_sdk_import.cmake
  sdk_import = Path("./pico_sdk_import.cmake")
  if not sdk_import.exists():
    #shutil.copy(Path(os.getenv("PICO_SDK_PATH")) / "external/pico_sdk_import.cmake", sdk_import)
    shutil.copy(Path(os.getenv("PICO_SDK_PATH")) / "external" / sdk_import, sdk_import)

  result = subprocess.run(["cmake", "..", *cmake_args], cwd="./build")
  assert result.returncode == 0

  result = subprocess.run(["make", "-j"], cwd="./build")
  assert result.returncode == 0

  return f"{config['PICO_IMAGE']}.uf2"


def install(image, config):

  if not Path(config["DEST_DEVICE"]).exists():
    raise FileNotFoundError("device not mounted for image loading")

  result = subprocess.run(["cp", image, config["DEST_DEVICE"]], cwd="./build")
  assert result.returncode == 0


if __name__ == "__main__":

  try:
    config = toml.load("./pyproject.toml")["pico"]
    image = build(config["build"])
    install(image, config["install"])

  except Exception as e:
    print(f"{e.__class__.__name__}: {str(e)}")
