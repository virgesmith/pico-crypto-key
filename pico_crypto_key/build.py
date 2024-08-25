import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import pytest
import tomllib
import typer

from pico_crypto_key import __version__

app = typer.Typer()


def _build_dir(board: str) -> Path:
    return Path(f"build-{board}")


def _get_config(board: str) -> dict[str, str]:
    with open("config/boards.toml", "rb") as fd:
        cfg = tomllib.load(fd)

    return cfg["default"] | cfg[board]


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


@app.command()
def check(board: str = typer.Option(default="pico", help="the target board")):
    """Check the project configuration."""
    print(f"Board: {board}")
    print(f"Software version: {__version__}")
    ok = True
    # TODO... check config
    # ok &= _check_symlink("./pico-sdk")
    ok &= _check_symlink("./pico-sdk/lib/tinyusb")
    ok &= _check_symlink("./mbedtls")
    if board == "pico_w":
        ok &= _check_symlink("./pico-sdk/lib/cyw43-driver")

    compiler = shutil.which("arm-none-eabi-g++")
    print(f"Compiler: {compiler or 'not found'}")
    ok &= compiler is not None

    if not os.getenv("PICO_CRYPTO_KEY_PIN"):
        print("PICO_CRYPTO_KEY_PIN not set in env, PIN will have to be entered manually")

    print("check ok" if ok else "configuration errors found")


@app.command()
def clean(board: str = typer.Option(default="pico", help="the target board")) -> None:
    """Clean intermediate build files."""
    if _build_dir(board).exists():
        shutil.rmtree(_build_dir(board))


@app.command()
def build(board: str = typer.Option(default="pico", help="the target board")) -> None:
    """Build the pico-crypto-key image."""

    # check build dir exists and create if necessary
    build_dir = _build_dir(board)
    build_dir.mkdir(exist_ok=True)

    config = _get_config(board)

    sdk_dir = build_dir / Path(config["PICO_SDK_PATH"])
    print(f"Mbed TLS points to {os.readlink('./mbedtls')}")

    # assumes SDK level with project dir and tinyusb present
    cmake_args = [
        f"-D{k}={v}" for k, v in config.items()
    ] + [
        f"-DPCK_VER={__version__}"
    ]

    print("cmake args:")
    for arg in cmake_args:
        print(f"  {arg}")

    # # ensure we have the latest pico_sdk_import.cmake
    sdk_import = Path("./pico_sdk_import.cmake")
    shutil.copy(sdk_dir / "external" / sdk_import, sdk_import)

    result = subprocess.run(["cmake", "..", *cmake_args], cwd=build_dir)
    assert result.returncode == 0

    result = subprocess.run(["make", "-j"], cwd=build_dir)
    assert result.returncode == 0


@app.command()
def install(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/${USER}/RPI-RP2"),
    board: str = typer.Option(default="pico", help="the target board"),
) -> None:
    """Install the pico-crypto-key image. The device must be mounted with BOOTSEL pressed."""

    build_dir = _build_dir(board)

    if not Path(device_path).exists():
        print(f"No device mounted at {device_path}")
        return

    image = "crypto-key.uf2"
    print(f"Installing {image}")
    result = subprocess.run(["cp", image, device_path], cwd=build_dir)
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

    result = subprocess.run(["cp", "reset-pin.uf2", device_path], cwd=_build_dir(board))
    assert result.returncode == 0


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def test(
    ctx: typer.Context,
    pin: Optional[str] = typer.Option(default=None, help="pin (optional, can use env var PICO_CRYPTO_KEY_PIN)"),  # noqa: UP007
) -> None:  # noqa: UP007
    """Run unit tests. PIN must either be passed as an option or set in PICO_CRYPTO_KEY_PIN env var"""
    assert pin or os.getenv(
        "PICO_CRYPTO_KEY_PIN"
    ), "Tests require pin to be specified as option (--pin ...) or PICO_CRYPTO_KEY_PIN in env"
    if pin:
        os.environ["PICO_CRYPTO_KEY_PIN"] = pin
    assert pytest.main(ctx.args) == 0, "tests failed, see logs"
