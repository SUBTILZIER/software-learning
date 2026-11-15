#!/usr/bin/env python3
"""Inventory ordinary or intentional-overlap AMap APK files."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

EOCD = b"PK\x05\x06"
CDH = b"PK\x01\x02"
LFH = b"PK\x03\x04"


@dataclass
class Entry:
    name: str
    method: int
    compressed_size: int
    size: int
    local_offset: int


def read_entries(data: bytes) -> list[Entry]:
    eocd = data.rfind(EOCD, max(0, len(data) - 65557))
    if eocd < 0:
        raise ValueError("ZIP EOCD not found")
    fields = struct.unpack_from("<4s4H2LH", data, eocd)
    count, cd_offset = fields[4], fields[6]
    out: list[Entry] = []
    pos = cd_offset
    for _ in range(count):
        if data[pos : pos + 4] != CDH:
            raise ValueError(f"central header missing at {pos}")
        f = struct.unpack_from("<4s6H3L5H2L", data, pos)
        flags, method = f[3], f[4]
        csize, size = f[8], f[9]
        name_len, extra_len, comment_len = f[10], f[11], f[12]
        local_offset = f[16]
        raw_name = data[pos + 46 : pos + 46 + name_len]
        name = raw_name.decode("utf-8" if flags & 0x800 else "cp437")
        out.append(Entry(name, method, csize, size, local_offset))
        pos += 46 + name_len + extra_len + comment_len
    return out


def payload(data: bytes, entry: Entry) -> bytes:
    if data[entry.local_offset : entry.local_offset + 4] != LFH:
        raise ValueError(f"local header missing for {entry.name}")
    name_len, extra_len = struct.unpack_from("<HH", data, entry.local_offset + 26)
    start = entry.local_offset + 30 + name_len + extra_len
    if entry.method != 0:
        raise ValueError(f"{entry.name} is compressed; raw payload hashing unsupported")
    return data[start : start + entry.size]


def inspect(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    entries = read_entries(data)
    dex = [e for e in entries if e.name.startswith("classes") and e.name.endswith(".dex")]
    libs = [e for e in entries if e.name.startswith("lib/")]
    assets = [e for e in entries if e.name.startswith("assets/")]
    result: dict[str, object] = {
        "path": str(path.resolve()),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper(),
        "entries": len(entries),
        "dex_count": len(dex),
        "dex_uncompressed_bytes": sum(e.size for e in dex),
        "dex_compressed_bytes": sum(e.compressed_size for e in dex),
        "native_library_entries": len(libs),
        "native_library_bytes": sum(e.size for e in libs),
        "asset_entries": len(assets),
        "has_arm64_native_libraries": any(e.name.startswith("lib/arm64-v8a/") for e in libs),
        "standalone_candidate": bool(libs),
    }
    origin = next((e for e in entries if e.name == "assets/origin473.apk"), None)
    if origin:
        origin_data = payload(data, origin)
        result["embedded_origin_bytes"] = len(origin_data)
        result["embedded_origin_sha256"] = hashlib.sha256(origin_data).hexdigest().upper()
        result["embedded_origin_data_offset"] = origin.local_offset + 30 + len(origin.name.encode("utf-8")) + struct.unpack_from("<H", data, origin.local_offset + 28)[0]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("apk", nargs="+", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    rows = [inspect(p) for p in args.apk]
    print(json.dumps(rows[0] if len(rows) == 1 else rows, ensure_ascii=False, indent=None if args.compact else 2))


if __name__ == "__main__":
    main()
