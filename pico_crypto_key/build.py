import os
import shutil
import subprocess
from pathlib import Path

import pytest
import typer

app = typer.Typer()

# might need different build dirs for different hardware. For now use the target name to differentiate
_build_dir = Path("./build")


@app.command()
def configure():
    """Configure the project."""
    raise NotImplementedError("TODO...")


def _check_symlink(path: str) -> bool:
    link = Path(path)
    print(f"Checking {path} ", end="")
    if link.is_dir() or link.is_symlink():
        print(f" -> {os.readlink(link)}")
        return True
    else:
        print("NOT FOUND")
        return False


# def _check_config(config: dict[str, str], key: str, check_exists: bool = False) -> bool:
#     print(f"Checking {key} ", end="")

#     if key in config:
#         print(f"= {config[key]}", end="")
#         if check_exists:
#             path = Path(config[key])
#             if path.is_file():
#                 print(" [connected]")
#             else:
#                 print(" [not found]")
#         else:
#             print()
#         return True
#     else:
#         print("NOT FOUND")
#         return False


@app.command()
def check(board: str = typer.Option(default="pico", help="the target board")):
    """Check the project configuration."""
    print(f"Board: {board}")
    ok = True
    ok &= _check_symlink("./pico-sdk")
    ok &= _check_symlink("./pico-sdk/lib/tinyusb")
    ok &= _check_symlink("./mbedtls")
    if board == "pico_w":
        ok &= _check_symlink("./pico-sdk/lib/cyw43-driver")

    if not os.getenv("PICO_CRYPTO_KEY_PIN"):
        print("PICO_CRYPTO_KEY_PIN not set in env, PIN will have to be entered manually")

    print("check ok" if ok else "configuration errors found")


@app.command()
def clean() -> None:
    """Clean intermediate build files."""
    if _build_dir.exists():
        shutil.rmtree(_build_dir)


@app.command()
def build(board: str = typer.Option(default="pico", help="the target board")) -> None:
    """Build the pico-crypto-key image."""

    # check build dir exists and create if necessary
    _build_dir.mkdir(exist_ok=True)

    sdk_dir = Path("./pico-sdk")
    print(f"Pico SDK points to {os.readlink(sdk_dir)}")
    print(f"Mbed TLS points to {os.readlink('./mbedtls')}")

    # assumes SDK level with project dir and tinyusb present
    cmake_args = [f"-DPICO_SDK_PATH={sdk_dir.resolve()}", f"-DPICO_BOARD={board}"]

    # ensure we have the latest pico_sdk_import.cmake
    sdk_import = Path("./pico_sdk_import.cmake")
    shutil.copy(Path(sdk_dir / "external" / sdk_import), sdk_import)

    result = subprocess.run(["cmake", "..", *cmake_args], cwd="./build")
    assert result.returncode == 0

    result = subprocess.run(["make", "-j"], cwd="./build")
    assert result.returncode == 0


@app.command()
def install(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/${USER}/RPI-RP2"),
    board: str = typer.Option(default="pico", help="the target board"),
) -> None:
    """Install the pico-crypto-key image. The device must be mounted with BOOTSEL pressed."""

    if not Path(device_path).exists():
        print(f"No device not mounted at {device_path}")
        return

    image = f"{board}-crypto-key.uf2"
    print(f"Installing {image}")
    result = subprocess.run(["cp", image, device_path], cwd="./build")
    assert result.returncode == 0


@app.command()
def reset_pin(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/${USER}/RPI-RP2"),
    board: str = typer.Option(default="pico", help="the target board"),
) -> None:
    """
    Installs a binary that resets the flash memory storing the pin hash.
    The device must be mounted with BOOTSEL pressed.
    """

    if not Path(device_path).exists():
        print(f"No device not mounted at {device_path}")
        return

    result = subprocess.run(["cp", f"{board}-reset-pin.uf2", device_path], cwd="./build")
    assert result.returncode == 0


@app.command()
def test():
    """Run unit tests. PIN must be set in PICO_CRYPTO_KEY_PIN env var"""
    assert os.getenv("PICO_CRYPTO_KEY_PIN"), "Tests require PICO_CRYPTO_KEY_PIN to be set"
    assert pytest.main() == 0
