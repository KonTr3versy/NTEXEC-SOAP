from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NMFFrame:
    """Minimal NMF frame representation for ADWS POC scaffolding."""

    payload: bytes
    is_end_of_sequence: bool = False


def encode_frame(payload: bytes, end_of_sequence: bool = False) -> bytes:
    """Encode a minimal frame with a 1-byte EOS marker + payload."""
    marker = b"\x01" if end_of_sequence else b"\x00"
    return marker + payload


def decode_frame(raw: bytes) -> NMFFrame:
    if not raw:
        raise ValueError("raw frame cannot be empty")
    return NMFFrame(payload=raw[1:], is_end_of_sequence=raw[0] == 1)
