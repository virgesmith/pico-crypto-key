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

    if board not in cfg:
        raise KeyError(f"no configuration for board '{board}'")

    return cfg["default"] | cfg[board]


def _check_symlink(path: str) -> bool:
    path = Path(path)
    print(f"Checking {path} ", end="")
    if path.is_symlink():
        # doesnt check link points to something that exists
        link = os.readlink(path)
        print(f"-> {link}")
        return True
    elif path.is_dir():
        print("")
        return True
    else:
        print("NOT FOUND")
        return False


@app.command(no_args_is_help=True)
def check(board: str = typer.Option(help="the target board")):
    """Check the project configuration."""

    _get_config(board)  # load config just to check board name is valid
    print(f"picobuild {__version__}")
    print(f"Board: {board}")
    ok = True
    config = _get_config(board)

    arch, gcc = ("riscv", "riscv32-unknown-elf-gcc") if "riscv" in board else ("arm", "arm-none-eabi-gcc")
    print(f"Arch: {arch}")

    build_dir = _build_dir(board)
    build_dir.mkdir(exist_ok=True)
    print(f"Build directory: {build_dir}")

    compiler = Path(config["PICO_TOOLCHAIN_PATH"]) / f"bin/{gcc}"
    print(f'C++ Compiler={compiler}: {"exists" if compiler.is_file() else "MISSING"}')
    ok &= compiler.is_file()

    sdk = build_dir / config["PICO_SDK_PATH"]
    print(f'PICO_SDK_PATH={config["PICO_SDK_PATH"]}: {"exists" if sdk.is_dir() else "MISSING"}')
    ok &= sdk.is_dir()

    picotool = shutil.which("picotool")
    print(f"picotool: {picotool or 'NOT FOUND'}")
    ok &= picotool is not None

    ok &= _check_symlink("./mbedtls")
    ok &= _check_symlink(sdk / "lib/tinyusb")
    if board in ["pico_w", "pico2_w"]:
        ok &= _check_symlink(sdk / "lib/cyw43-driver")

    if not os.getenv("PICO_CRYPTO_KEY_PIN"):
        print("PICO_CRYPTO_KEY_PIN not set in env, PIN will have to be entered manually")

    print("check ok" if ok else "configuration errors found")


@app.command(no_args_is_help=True)
def clean(board: str = typer.Option(help="the target board")) -> None:
    """Clean intermediate build files."""
    _get_config(board)  # load config just to check board name is valid

    if _build_dir(board).exists():
        shutil.rmtree(_build_dir(board))


@app.command(no_args_is_help=True)
def build(board: str = typer.Option(help="the target board")) -> None:
    """Build the pico-crypto-key image."""

    # check build dir exists and create if necessary
    build_dir = _build_dir(board)
    build_dir.mkdir(exist_ok=True)

    config = _get_config(board)

    sdk_dir = build_dir / Path(config["PICO_SDK_PATH"])
    print(f"Mbed TLS points to {os.readlink('./mbedtls')}")

    # assumes SDK level with project dir and tinyusb present
    cmake_args = [f"-D{k}={v}" for k, v in config.items()] + [f"-DPCK_VER={__version__}"]

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


@app.command(no_args_is_help=True)
def install(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/${USER}/RPI-RP2"),
    board: str = typer.Option(help="the target board"),
) -> None:
    """Install the pico-crypto-key image. The device must be mounted with BOOTSEL pressed."""

    _get_config(board)  # load config just to check board name is valid

    build_dir = _build_dir(board)

    if not Path(device_path).exists():
        print(f"No device mounted at {device_path}")
        return

    image = "crypto-key.uf2"
    print(f"Installing {image}")
    result = subprocess.run(["cp", image, device_path], cwd=build_dir)
    assert result.returncode == 0


@app.command(no_args_is_help=True)
def reset_pin(
    device_path: str = typer.Argument(..., help="the path to the device storage, e.g. /media/${USER}/RPI-RP2"),
    board: str = typer.Option(help="the target board"),
) -> None:
    """
    Installs a binary that resets the flash memory storing the pin hash.
    The device must be mounted with BOOTSEL pressed.
    """

    _get_config(board)  # load config just to check board name is valid

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
