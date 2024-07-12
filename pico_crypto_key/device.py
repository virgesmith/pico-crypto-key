from __future__ import annotations

import os
from base64 import b64encode
from datetime import datetime, timezone
from pathlib import Path
from struct import pack, unpack
from types import TracebackType
from typing import Any

import usb.core  # type: ignore[import-untyped]
import usb.util  # type: ignore[import-untyped]
from pwinput import pwinput  # type: ignore[import-untyped]


class CryptoKeyNotFoundError(ConnectionError):
    pass


def _read_pin_from_stdin() -> str:
    return pwinput("PIN:")


class CryptoKey:
    CHUNK_SIZE = 2048
    HASH_BYTES = 32
    ECDSA_PUBKEY_BYTES = 33  # short form with 02/03 prefix
    VERIFY_FAILED = 2**32 - 19968  # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED

    reattach: bool

    def __init__(self) -> None:
        """Create device object for use in context manager."""
        self.have_repl = False  # tracks whether repl entered (i.e. pin was correct)
        self.device: Any = None

    def __enter__(self) -> CryptoKey:
        """Initialised the device's repl."""
        self.init()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        _exc_stack: TracebackType | None,
    ) -> None:
        """Disconnect from the device's repl."""
        self.reset()
        if exc_type:
            print(f"{exc_type.__name__}: {exc_value}")

        usb.util.dispose_resources(self.device)
        # It may raise USBError if there's e.g. no kernel driver loaded at all
        try:
            if self.reattach:
                self.device.attach_kernel_driver(0)
        except usb.core.USBError:
            pass

    def hash(self, filename: Path) -> bytes:
        """
        Computes the SHA256 hash of a file

        Parameters
        ----------
        filename: str
            The name of the file

        Returns
        -------
        bytes
            The hash digest
        """
        assert self.have_repl
        self._write(b"h")
        file_length = os.stat(filename).st_size
        self._write_uint32(file_length)
        with open(filename, "rb") as fd:
            write_remaining = file_length
            while write_remaining > 0:
                write_chunk_length = min(write_remaining, self.CHUNK_SIZE)
                data = fd.read(write_chunk_length)
                ret = self._write(data)
                write_remaining -= ret
        return self._read(CryptoKey.HASH_BYTES)

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts data using AES256

        Parameters
        ----------
        data: bytes
            Some binary data

        Returns
        -------
        bytes
            The encrpted data
        """
        assert self.have_repl
        self._write(b"e")

        length = len(data)
        self._write_uint32(length)

        output = bytearray()
        for pos in range(0, length, self.CHUNK_SIZE):
            chunk_length = min(length - pos, self.CHUNK_SIZE)
            # write a chunk
            bytes_written = self._write(data[pos : pos + chunk_length])
            chunk = self._read(bytes_written)
            output += chunk
        return bytes(output)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts data using AES256

        Parameters
        ----------
        data: bytes
            Some encrypted binary data

        Returns
        -------
        bytes
            The decrypted data (if the device is the same as the encrypting device, random bytes otherwise)
        """
        assert self.have_repl
        self._write(b"d")

        length = len(data)
        self._write_uint32(length)

        output = bytearray()
        for pos in range(0, length, self.CHUNK_SIZE):
            chunk_length = min(length - pos, self.CHUNK_SIZE)
            # write a chunk
            bytes_written = self._write(data[pos : pos + chunk_length])
            chunk = self._read(bytes_written)
            output += chunk
        return bytes(output)

    def sign(self, filename: str) -> tuple[bytes, bytes]:
        """
        Computes the hash of a file and its and ECDSA signature

        Parameters
        ----------
        filename: str
            The name of the file

        Returns
        -------
        tuple[bytes, bytes]
            The hash digest and the signature
        """
        assert self.have_repl
        self._write(b"s")
        file_length = os.stat(filename).st_size
        self._write_uint32(file_length)
        with open(filename, "rb") as fd:
            write_remaining = file_length
            while write_remaining > 0:
                write_chunk_length = min(write_remaining, self.CHUNK_SIZE)
                data = fd.read(write_chunk_length)
                ret = self._write(data)
                write_remaining -= ret
        # somehow separates hash and sig even when length not specified
        digest = self._read(CryptoKey.HASH_BYTES)
        siglen = self._read_uint32()
        sig = self._read(siglen)
        return digest, sig

    def verify(self, digest: bytes, sig: bytes, pubkey: bytes) -> int:
        """
        Checks the ECDSA signature given a hash and the ECDSA public key of the signer
        Checking the hash corresponds to the original data is a separate step

        Parameters
        ----------
        digest: bytes
            The SHA256 hash for the original data (can confirm by re-hashing)
        sig: bytes
            The ECDSA signature
        pubkey:


        Returns
        -------
        int
            0 if the signature verifies
            4294947328 (-0x480) if not
            any other nonzero value indicates an error
        """

        assert self.have_repl
        self._write(b"v")
        self._write(digest)
        self._write_uint32(len(sig))
        self._write(sig)
        self._write_uint32(len(pubkey))
        self._write(pubkey)
        return self._read_uint32()

    def pubkey(self) -> bytes:
        """
        Computes the hash of a file and its and ECDSA signature

        Parameters
        ----------

        Returns
        -------
        bytes
            The long-form ECDSA public key
        """
        assert self.have_repl
        self._write(b"k")
        pubkey = self._read(CryptoKey.ECDSA_PUBKEY_BYTES)
        return pubkey

    def register(self, relying_party: str, user: str) -> bytes:
        """
        Returns dynamically generated ECDSA public key
        """
        assert self.have_repl
        userdata = f"{user}@{relying_party}".encode()
        self._write(b"r")
        self._write_uint32(len(userdata))
        self._write(userdata)
        pubkey = self._read(CryptoKey.ECDSA_PUBKEY_BYTES)
        return pubkey

    def auth(self, relying_party: str, user: str, challenge: bytes) -> bytes:
        """
        Time-limited authentication
        Appends challenge with current minute timestamp, hashes and signs
        Returns base64-encoded signature
        """
        assert self.have_repl
        userdata = f"{user}@{relying_party}".encode()
        self._write(b"a")
        self._write_uint32(len(userdata))
        self._write(userdata)
        self._write_uint32(len(challenge))
        self._write(challenge)
        length = self._read_uint32()
        sig = self._read(length)
        return b64encode(sig)

    def info(self) -> tuple[str, datetime]:
        """
        Returns board information: board type, firmware version, timestamp
        """
        assert self.have_repl
        self._write(b"i")
        length = self._read_uint32()
        raw = self._read(length)
        version = raw[:-8].decode()
        timestamp = datetime.fromtimestamp(unpack("Q", raw[-8:])[0] / 1000, tz=timezone.utc)
        return version, timestamp

    def set_pin(self) -> None:
        """
        Sets a new device pin

        Parameters
        ----------

        Returns
        -------
        bool
            Whether PIN change was successful
        """
        print("Resetting device (old PIN will need to be reentered)...")
        if "PICO_CRYPTO_KEY_PIN" in os.environ:
            # ensure pin is entered manually
            del os.environ["PICO_CRYPTO_KEY_PIN"]
        self.reset()
        self.init()
        new_pin = pwinput("NEW PIN:")
        if not 4 <= len(new_pin) <= 64:
            print("pin must be between 4 and 64 bytes")
            return
        check = pwinput("CONFIRM:")
        if new_pin != check:
            print("doesn't match")
            return
        self._write(b"p")
        self._write_uint32(len(new_pin))
        self._write(new_pin)
        result = self._read_uint32()
        if result:
            print("pin change failed: {result}")
            return
        print("resetting device and reauthenticating")
        self.reset()
        self.init()
        print("new pin set, update your env as necessary")

    def reset(self) -> None:
        """
        Resets the device. Device pin will need to be reentered
        Normally this is handled by the context manager
        """
        # only send reset request if we have repl
        if self.have_repl:
            self.__endpoint_in.write(b"x")
            self.have_repl = False

        usb.util.dispose_resources(self.device)

        # It may raise USBError if there's e.g. no kernel driver loaded at all
        if self.reattach:
            self.device.attach_kernel_driver(0)

    def init(self) -> None:
        """
        Initialises the device with the supplied pin
        Normally this is handled by the context manager
        """
        self.device = usb.core.find(idVendor=0xAAFE, idProduct=0xC0FF)

        if not self.device:
            raise CryptoKeyNotFoundError()

        device_pin = (os.getenv("PICO_CRYPTO_KEY_PIN") or _read_pin_from_stdin()).encode("utf-8")

        cfg = self.device.get_active_configuration()
        # usb.core.USBError: [Errno 13] Access denied (insufficient permissions)
        # see https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the

        interface = cfg[(1, 0)]
        self.__endpoint_in, self.__endpoint_out = usb.util.find_descriptor(
            interface,
            find_all=True,
        )

        self.reattach = False
        if self.device.is_kernel_driver_active(0):
            self.reattach = True
            self.device.detach_kernel_driver(0)

        self._write_uint32(len(device_pin))
        self._write(device_pin)

        error_code = self._read_uint32()
        if error_code:
            raise ValueError("pin incorrect")

        # set time on device for TOTP/webauthn
        self._set_device_time()

        self.have_repl = True

    def _set_device_time(self) -> None:
        epoch_ms = int(datetime.now().timestamp() * 1000)
        self._write_uint64(epoch_ms)

    def _read(self, length: int) -> bytes:
        result = bytearray()
        while length:
            chunk = self.__endpoint_out.read(length).tobytes()
            result += chunk
            length -= len(chunk)
        return bytes(result)

    def _read_uint32(self) -> int:
        """Read raw uint32_t (?-endian)"""
        data = self._read(4)
        return unpack("I", data)[0]

    def _read_uint64(self) -> int:
        """Read raw uint64_t (?-endian)"""
        data = self._read(8)
        return unpack("Q", data)[0]

    def _write(self, b: bytes) -> int:
        bytes_written = self.__endpoint_in.write(b)
        assert bytes_written == len(b)
        return bytes_written

    def _write_uint32(self, n: int) -> bool:
        """Writes an int as uint32_t (?-endian)"""
        uint32 = pack("I", n)
        return self._write(uint32) == 4

    def _write_uint64(self, n: int) -> bool:
        """Writes an int as uint32_t (?-endian)"""
        uint64 = pack("Q", n)
        return self._write(uint64) == 8
