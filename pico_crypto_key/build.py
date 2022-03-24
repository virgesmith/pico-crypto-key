# pico-crypto-key builder

import os
import subprocess
from pathlib import Path
import toml
import shutil


def main(config: dict) -> None:

  # check build dir exists and create if necessary
  build_dir = Path("./build")
  if not build_dir.exists():
    build_dir.mkdir()

  sdk_dir = Path(f"../pico-sdk-{config['PICO_SDK_VERSION']}")

  # assumes SDK level with project dir and tinyusb present
  os.environ["PICO_SDK_PATH"] = str(sdk_dir.resolve())

  # check we have pico_sdk_import.cmake
  sdk_import = Path("./pico_sdk_import.cmake")
  if not sdk_import.exists():
    #shutil.copy(Path(os.getenv("PICO_SDK_PATH")) / "external/pico_sdk_import.cmake", sdk_import)
    shutil.copy(Path(os.getenv("PICO_SDK_PATH")) / "external" / sdk_import, sdk_import)


  result = subprocess.run(["cmake", ".."], cwd="./build")
  assert result.returncode == 0

  result = subprocess.run(["make", "-j"], cwd="./build")
  assert result.returncode == 0

  assert Path(config["DEST_DEVICE"]).exists(), "device not mounted for image loading"

  result = subprocess.run(["cp", config["PICO_IMAGE"], config["DEST_DEVICE"]], cwd="./build")
  assert result.returncode == 0


if __name__ == "__main__":

  try:
    config = toml.load("./config.toml")
    main(config["build"])
  except Exception as e:
    print(f"{e.__class__.__name__}: {str(e)}")
