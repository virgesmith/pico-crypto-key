from __future__ import annotations
import os
from struct import pack, unpack
from types import TracebackType

import usb.core
import usb.util

class CryptoKeyNotFoundError(ConnectionError):
    pass


class CryptoKey:
    CHUNK_SIZE = 2048
    VERIFY_FAILED = 2 ** 32 - 19968  # -0x480 MBEDTLS_ERR_ECP_VERIFY_FAILED

    def __init__(self, *, pin: str) -> None:
        """Create device object for use in context manager."""
        self.have_repl = False  # tracks whether repl entered (i.e. pin was correct)
        self.device_pin = pin.encode("utf-8")
        self.device = None

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
        if self.reattach:
            self.device.attach_kernel_driver(0)

    def help(self) -> str:
        assert self.have_repl
        self._write(b"H")
        return self._read_int()

    def hash(self, filename: str) -> bytes:
        assert self.have_repl
        self._write(b"h")
        file_length = os.stat(filename).st_size
        uint32 = pack("I", file_length)   
        ret = self._write(uint32)
        with open(filename, "rb") as fd:
            write_remaining = file_length
            while write_remaining > 0:
                write_chunk_length = min(write_remaining, self.CHUNK_SIZE)
                data = fd.read(write_chunk_length)
                ret = self._write(data)
                write_remaining -= ret    
        return self._read(32)

    def encrypt(self, data: bytes) -> bytes:
        assert self.have_repl
        self._write(b"e")

        length = len(data)
        uint32 = pack("I", length)   
        self._write(uint32)

        output = bytearray()
        for pos in range(0, length, self.CHUNK_SIZE):
            chunk_length = min(length - pos, self.CHUNK_SIZE)
            # write a chunk
            bytes_written = self._write(data[pos:pos + chunk_length])
            chunk = self._read(bytes_written)
            output += chunk
        return bytes(output)

    def decrypt(self, data: bytes) -> bytes:
        # This returns garbage if the device isn't the one that encrypted it
        assert self.have_repl
        self._write(b"d")

        length = len(data)
        uint32 = pack("I", length)   
        self._write(uint32)

        output = bytearray()
        for pos in range(0, length, self.CHUNK_SIZE):
            chunk_length = min(length - pos, self.CHUNK_SIZE)
            # write a chunk
            bytes_written = self._write(data[pos:pos + chunk_length])
            chunk = self._read(bytes_written)
            output += chunk
        return bytes(output)

    def sign(self, filename: str) -> tuple[bytes, bytes]:
        assert self.have_repl
        self._write(b"s")
        file_length = os.stat(filename).st_size
        self._write_int(file_length)
        with open(filename, "rb") as fd:
            write_remaining = file_length
            while write_remaining > 0:
                write_chunk_length = min(write_remaining, self.CHUNK_SIZE)
                data = fd.read(write_chunk_length)
                ret = self._write(data)
                write_remaining -= ret    
        # somehow separates hash and sig even when length not specified
        hash = self._read(32)
        siglen = self._read_int()
        sig = self._read(siglen)
        return hash, sig

    def verify(self, digest: bytes, sig: bytes, pubkey: bytes) -> int:
        """
        device return value:
        0:      successfully verified
        -19968: not verified (=4294947328u)
        any other value means something else went wrong e.g. data formats are incorrect
        """
        assert self.have_repl
        self._write(b"v")
        self._write(digest)
        self._write_int(len(sig))
        self._write(sig)
        self._write_int(len(pubkey))
        self._write(pubkey)
        return self._read_int()

    def pubkey(self) -> bytes:
        assert self.have_repl
        self.__endpoint_in.write(str.encode("k"))
        pubkey = self._read(65)
        return pubkey

    def reset(self) -> None:
        # only send reset request if we have repl
        if self.have_repl:
            self.__endpoint_in.write(b"r")
            self.have_repl = False

    def init(self) -> None:
        self.device = usb.core.find(idVendor=0xAAFE, idProduct=0xC0FF)

        if not self.device:
            raise CryptoKeyNotFoundError()

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

        self._write(self.device_pin)
        error_code = unpack("I", self._read(4))[0]

        if error_code:
            raise ValueError("pin incorrect")
        self.have_repl = True

    def _read(self, length: int) -> bytes:
        result = bytearray()
        while length:
            chunk = self.__endpoint_out.read(length).tobytes()
            result += chunk
            length -= len(chunk)
        return bytes(result)
    
    def _read_int(self) -> int:
        """Read raw uint32_t (?-endian)"""
        data = self._read(4)
        return unpack("I", data)[0]

    def _write(self, b: bytes) -> int:
        bytes_written = self.__endpoint_in.write(b)
        assert bytes_written == len(b)
        return bytes_written
    
    def _write_int(self, n: int) -> bool:
        """Writes an int as uint32_t (?-endian)"""
        uint32 = pack("I", n)   
        return self._write(uint32) == 4


