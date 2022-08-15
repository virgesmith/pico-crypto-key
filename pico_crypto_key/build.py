import os
import shutil
import subprocess
from pathlib import Path

import toml


def build(config: dict[str, str]) -> str:

    # check build dir exists and create if necessary
    build_dir = Path("./build")
    if not build_dir.exists():
        build_dir.mkdir()

    sdk_dir = Path("./pico-sdk")
    print(f"Pico SDK points to {os.readlink(sdk_dir)}")
    print(f"Mbed TLS points to {os.readlink('./mbedtls')}")

    # assumes SDK level with project dir and tinyusb present
    cmake_args = [
        f"-DPICO_SDK_PATH={sdk_dir.resolve()}",
        f"-DPICO_IMAGE={config['PICO_IMAGE']}",
    ]

    # ensure we have the latest pico_sdk_import.cmake
    sdk_import = Path("./pico_sdk_import.cmake")
    shutil.copy(Path(sdk_dir / "external" / sdk_import), sdk_import)

    result = subprocess.run(["cmake", "..", *cmake_args], cwd="./build")
    assert result.returncode == 0

    result = subprocess.run(["make", "-j"], cwd="./build")
    assert result.returncode == 0

    return f"{config['PICO_IMAGE']}.uf2"


def install(image: str, config: dict[str, str]) -> None:

    if not Path(config["DEVICE_PATH"]).exists():
        raise FileNotFoundError("device not mounted for image loading")

    result = subprocess.run(["cp", image, config["DEVICE_PATH"]], cwd="./build")
    assert result.returncode == 0


def main() -> None:
    try:
        config = toml.load("./pyproject.toml")["pico"]
        image = build(config["build"])
        install(image, config["install"])

    except Exception as e:
        print(f"{e.__class__.__name__}: {str(e)}")
