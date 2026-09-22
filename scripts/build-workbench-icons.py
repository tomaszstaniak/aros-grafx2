#!/usr/bin/env python3
"""AROS PNG Workbench icons from GrafX2's shipped gfx2.png.

Two concatenated PNGs (normal + selected) with an icOn chunk, matching
AROS workbench/libs/icon/diskobjPNGio.c:
  0x8000100f  icon type (2 = drawer, 3 = tool)
  0x80001009  stack size in bytes
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

STACK = 8 * 1024 * 1024  # 8 MiB; same as __stack in osdep.c


def _chunk(name: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(name + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_indexed_png(path: Path) -> tuple[int, int, list[int]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    pos = 8
    width = height = bit_depth = color_type = None
    palette: list[tuple[int, int, int]] = []
    trans = [255] * 256
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        name = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if name == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif name == b"PLTE":
            palette = [
                (chunk[i], chunk[i + 1], chunk[i + 2]) for i in range(0, len(chunk), 3)
            ]
        elif name == b"tRNS":
            for i, v in enumerate(chunk):
                trans[i] = v
        elif name == b"IDAT":
            idat.extend(chunk)
        elif name == b"IEND":
            break
    if width is None or color_type != 3 or bit_depth != 8:
        raise ValueError(f"{path}: need 8-bit indexed PNG, got {color_type}/{bit_depth}")
    raw = zlib.decompress(bytes(idat))
    stride = width
    pixels: list[int] = []
    prev = bytes(stride)
    offset = 0
    for _ in range(height):
        ftype = raw[offset]
        row = bytearray(raw[offset + 1 : offset + 1 + stride])
        offset += 1 + stride
        if ftype == 1:
            for x in range(stride):
                row[x] = (row[x] + (row[x - 1] if x else 0)) & 255
        elif ftype == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif ftype == 3:
            for x in range(stride):
                left = row[x - 1] if x else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif ftype == 4:
            for x in range(stride):
                left = row[x - 1] if x else 0
                upleft = prev[x - 1] if x else 0
                row[x] = (row[x] + _paeth(left, prev[x], upleft)) & 255
        elif ftype != 0:
            raise ValueError(f"unsupported PNG filter {ftype}")
        prev = bytes(row)
        for idx in row:
            r, g, b = palette[idx]
            pixels.append((r << 16) | (g << 8) | b | (trans[idx] << 24))
    return width, height, pixels


def encode_icon_png(width: int, height: int, pixels: list[int], kind: int, selected: bool) -> bytes:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            p = pixels[y * width + x]
            r, g, b, a = (p >> 16) & 255, (p >> 8) & 255, p & 255, (p >> 24) & 255
            if selected:
                r, g, b = min(255, r + 40), min(255, g + 40), min(255, b + 40)
                if x < 2 or y < 2 or x >= width - 2 or y >= height - 2:
                    r, g, b, a = 255, 220, 0, 255
            raw.extend((r, g, b, a))
    tags = [(0x8000100F, kind), (0x80001009, STACK)]
    metadata = b"".join(struct.pack(">II", *t) for t in tags)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _chunk(b"icOn", metadata)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


def main() -> None:
    dest = Path(sys.argv[1])
    src = Path(sys.argv[2])
    dest.mkdir(parents=True, exist_ok=True)
    width, height, pixels = decode_indexed_png(src)
    tool = encode_icon_png(width, height, pixels, 3, False) + encode_icon_png(
        width, height, pixels, 3, True
    )
    drawer = encode_icon_png(width, height, pixels, 2, False) + encode_icon_png(
        width, height, pixels, 2, True
    )
    (dest / "GrafX2.info").write_bytes(tool)
    dest.with_suffix(".info").write_bytes(drawer)


if __name__ == "__main__":
    main()
