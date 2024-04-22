import importlib.metadata

__version__ = importlib.metadata.version("pico-crypto-key")

from .device import CryptoKey
