import importlib.metadata
from datetime import UTC, datetime, timezone
from struct import pack

__version__ = importlib.metadata.version("pico-crypto-key")

from .device import CryptoKey, CryptoKeyConnectionError, CryptoKeyPinError

TIMESTAMP_RESOLUTION_MS = 60_000  # 1 min


def timestamp() -> bytes:
    """
    Returns ms timestamp rounded to the nearest time interval
    There is a small chance that host and user rounded timestamps differ
    """
    now = datetime.now(tz=UTC)
    t = int(now.timestamp() * 1000)
    return pack("Q", t - t % TIMESTAMP_RESOLUTION_MS)
