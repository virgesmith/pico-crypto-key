import os
import shutil
import subprocess
from pathlib import Path

import pytest
import toml
import typer

app = typer.Typer()

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


def _check_config(config: dict[str, str], key: str, check_exists: bool = False) -> bool:
    print(f"Checking {key} ", end="")

    if key in config:
        print(f"= {config[key]}", end="")
        if check_exists:
            path = Path(config[key])
            if path.is_file():
                print(" [connected]")
            else:
                print(" [not found]")
        else:
            print()
        return True
    else:
        print("NOT FOUND")
        return False


@app.command()
def check():
    """Check the project configuration."""
    ok = True
    config = toml.load("./pyproject.toml")["pico"]
    ok &= _check_symlink("./pico-sdk")
    ok &= _check_symlink("./pico-sdk/lib/tinyusb")
    ok &= _check_symlink("./mbedtls")
    ok &= _check_config(config["build"], "PICO_IMAGE")
    ok &= _check_config(config["build"], "PICO_RESET_PIN")

    if not os.getenv("PICO_CRYPTO_KEY_PIN"):
        print("PICO_CRYPTO_KEY_PIN not set in env, PIN will have to be entered manually")

    print("check ok" if ok else "configuration errors found")


@app.command()
def clean() -> None:
    """Clean intermediate build files."""
    if _build_dir.exists():
        shutil.rmtree(_build_dir)


@app.command()
def build() -> str:
    """Build the pico-crypto-key image."""
    config = toml.load("./pyproject.toml")["pico"]["build"]

    # check build dir exists and create if necessary
    _build_dir.mkdir(exist_ok=True)

    sdk_dir = Path("./pico-sdk")
    print(f"Pico SDK points to {os.readlink(sdk_dir)}")
    print(f"Mbed TLS points to {os.readlink('./mbedtls')}")

    # assumes SDK level with project dir and tinyusb present
    cmake_args = [
        f"-DPICO_SDK_PATH={sdk_dir.resolve()}",
        f"-DPICO_IMAGE={config['PICO_IMAGE']}",
        f"-DPICO_RESET_PIN={config['PICO_RESET_PIN']}",
        "-DPICO_BOARD=pico"
    ]

    # ensure we have the latest pico_sdk_import.cmake
    sdk_import = Path("./pico_sdk_import.cmake")
    shutil.copy(Path(sdk_dir / "external" / sdk_import), sdk_import)

    result = subprocess.run(["cmake", "..", *cmake_args], cwd="./build")
    assert result.returncode == 0

    result = subprocess.run(["make", "-j"], cwd="./build")
    assert result.returncode == 0

    return f"{config['PICO_IMAGE']}.uf2"


@app.command()
def install(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/user/RPI-RP2"),
) -> None:
    """Install the pico-crypto-key image. The device must be mounted with BOOTSEL pressed."""

    config = toml.load("./pyproject.toml")["pico"]["build"]

    if not Path(device_path).exists():
        print(f"No device not mounted at {device_path}")
        return

    result = subprocess.run(["cp", f"{config['PICO_IMAGE']}.uf2", device_path], cwd="./build")
    assert result.returncode == 0


@app.command()
def reset_pin(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/user/RPI-RP2"),
) -> None:
    """
    Installs a binary that resets the flash memory storing the pin hash.
    The device must be mounted with BOOTSEL pressed.
    """

    config = toml.load("./pyproject.toml")["pico"]["build"]

    if not Path(device_path).exists():
        print(f"No device not mounted at {device_path}")
        return

    result = subprocess.run(["cp", f"{config['PICO_RESET_PIN']}.uf2", device_path], cwd="./build")
    assert result.returncode == 0


@app.command()
def test():
    """Run unit tests. PIN must be set in PICO_CRYPTO_KEY_PIN env var"""
    assert os.getenv("PICO_CRYPTO_KEY_PIN"), "Tests require PICO_CRYPTO_KEY_PIN to be set"
    assert pytest.main() == 0
