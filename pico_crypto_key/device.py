from __future__ import annotations
import os
from io import BytesIO
from struct import pack, unpack
from types import TracebackType
from typing import Any

import usb.core
import usb.util


class CryptoKey:
    CHUNK_SIZE = 16384

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
        return self._read().decode()

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
        return self._read()

    # def encrypt(self, data: BytesIO) -> bytearray:
    #     assert self.have_repl
    #     self.__device.write(str.encode("e"))
    #     data_enc = bytearray()
    #     while True:
    #         raw = data.read(CryptoKey.CHUNK_SIZE)
    #         if not raw:
    #             break
    #         b = b64encode(raw)
    #         self.__device.write(bytearray(b) + b"\n")
    #         resp = b64decode(self.__device.readline())
    #         data_enc.extend(resp)
    #     self.__device.write(b"\n")
    #     return data_enc

    # def decrypt(self, data: BytesIO) -> bytearray:
    #     # This returns garbage if the device isn't the one that encrypted it
    #     assert self.have_repl
    #     self.__device.write(str.encode("d"))
    #     data_dec = bytearray()
    #     while True:
    #         raw = data.read(CryptoKey.CHUNK_SIZE)
    #         if not raw:
    #             break
    #         b = b64encode(raw)
    #         self.__device.write(bytearray(b) + b"\n")
    #         resp = b64decode(self.__device.readline())
    #         data_dec.extend(resp)
    #     self.__device.write(b"\n")
    #     return data_dec

    def sign(self, filename: str) -> tuple[bytes, bytes]:
        assert self.have_repl
        self._write(b"s")
        file_length = os.stat(filename).st_size
        self._write_int(file_length)
        # print(f"H: wrote {ret} bytes")
        with open(filename, "rb") as fd:
            write_remaining = file_length
            while write_remaining > 0:
                write_chunk_length = min(write_remaining, self.CHUNK_SIZE)
                data = fd.read(write_chunk_length)
                ret = self._write(data)
                write_remaining -= ret    
        # somehow separates hash and sig even when length not specified
        hash = self._read(32)
        sig = self._read()
        return hash, sig


    def verify(self, digest: bytes, sig: bytes, pubkey: bytes) -> int:
        """return value:

        0:      successfully verified
        -19968: not verified
        any other value means something else went wrong e.g. data formats are incorrect
        """
        assert self.have_repl
        self._write(b"v")
        self._write(digest)
        self._write_int(len(sig))
        self._write(sig)
        self._write_int(len(pubkey))
        self._write(pubkey)
        return self._read_int() == 0

    def pubkey(self) -> bytes:
        assert self.have_repl
        self.__endpoint_in.write(str.encode("k"))
        pubkey = self._read()
        return pubkey

    def reset(self) -> None:
        # only send reset request if we have repl
        if self.have_repl:
            print("resetting")
            self.__endpoint_in.write(b"r")
            self.have_repl = False

    def init(self) -> None:
        self.device = usb.core.find(idVendor=0xAAFE, idProduct=0xC0FF)

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

        print("H: sending pin")
        self._write(self.device_pin)
        response = self._read()
        print(f"H: got '{response}' ({len(response)})")

        if response != b"pin ok":
            raise ValueError("pin incorrect")
        self.have_repl = True

    def _read(self, length: int | None = None) -> bytes:
        length = length or self.CHUNK_SIZE
        return self.__endpoint_out.read(length).tobytes()
    
    def _read_int(self) -> int:
        """Read raw uint32_t (?-endian)"""
        data = self._read(4)
        return unpack("I", data)[0]

    def _write(self, b: bytes) -> int:
        return self.__endpoint_in.write(b)
    
    def _write_int(self, n: int) -> bool:
        """Writes an int as uint32_t (?-endian)"""
        uint32 = pack("I", n)   
        return self._write(uint32) == 4



def get_endpoints(device: usb.core.Device) -> tuple:
    # TODO this function needs improvement
    cfg = device.get_active_configuration()
    # usb.core.USBError: [Errno 13] Access denied (insufficient permissions)
    # see https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the

    interface = cfg[(1, 0)]
    endpoints = usb.util.find_descriptor(
        interface,
        find_all=True,
    )

    return endpoints
