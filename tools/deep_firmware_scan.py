import json
import re
import struct
from pathlib import Path


ROOT = Path(r"E:\GeekFlashTool_Readback_20261010230748790")
OUTPUT = ROOT / "small_partition_scan" / "firmware_blobs.md"
MAX_SIZE = 64 * 1024 * 1024

MAGICS = {
    "elf": b"\x7fELF",
    "fdt": b"\xd0\x0d\xfe\xed",
    "gzip": b"\x1f\x8b",
    "xz": b"\xfd7zXZ\x00",
    "zstd": b"\x28\xb5\x2f\xfd",
    "lz4": b"\x04\x22\x4d\x18",
    "android_boot": b"ANDROID!",
    "vendor_boot": b"VNDRBOOT",
    "avb0": b"AVB0",
    "optee": b"OPTE",
    "cpio": b"070701",
}

MTK_GFH_MAGICS = [
    bytes.fromhex("88168858"),
    bytes.fromhex("89168958"),
]

VERSION_RE = re.compile(
    rb"[\x20-\x7e]{0,80}(?:\b(?:version|build|release|commit|"
    rb"secure|key|certificate|root|boot|verified|mac|serial|imei)\b)"
    rb"[\x20-\x7e]{0,120}",
    re.IGNORECASE,
)


def all_offsets(data: bytes, magic: bytes, limit: int = 50) -> list[int]:
    offsets = []
    start = 0
    while len(offsets) < limit:
        offset = data.find(magic, start)
        if offset < 0:
            break
        offsets.append(offset)
        start = offset + 1
    return offsets


def parse_elf_header(data: bytes, offset: int) -> dict:
    if offset + 64 > len(data):
        return {}
    ident = data[offset : offset + 16]
    elf_class = ident[4]
    data_encoding = ident[5]
    endian = "<" if data_encoding == 1 else ">"
    try:
        e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags = (
            struct.unpack_from(endian + "HHIQQQI", data, offset + 16)
        )
        e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = (
            struct.unpack_from(endian + "HHHHHH", data, offset + 40)
        )
    except struct.error:
        return {}
    return {
        "class": "ELF64" if elf_class == 2 else "ELF32",
        "encoding": "little" if data_encoding == 1 else "big",
        "type": e_type,
        "machine": e_machine,
        "entry": e_entry,
        "program_header_offset": e_phoff,
        "section_header_offset": e_shoff,
        "flags": e_flags,
        "header_size": e_ehsize,
        "program_header_size": e_phentsize,
        "program_header_count": e_phnum,
        "section_header_size": e_shentsize,
        "section_header_count": e_shnum,
        "section_string_index": e_shstrndx,
    }


def parse_mtk_gfh(data: bytes) -> dict:
    for magic in MTK_GFH_MAGICS:
        if data.startswith(magic):
            name = data[8:32].split(b"\x00", 1)[0]
            return {
                "magic": magic.hex(),
                "name": name.decode("latin1", errors="replace"),
                "header_hex": data[:128].hex(),
            }
    return {}


def interesting_strings(data: bytes, limit: int = 120) -> list[str]:
    values = []
    seen = set()
    for match in VERSION_RE.finditer(data):
        value = match.group().decode("latin1", errors="replace").strip()
        if value and value not in seen:
            seen.add(value)
            values.append(value)
            if len(values) >= limit:
                break
    return values


def main() -> None:
    lines = ["# Firmware Blob Deep Scan", ""]
    for path in sorted(ROOT.glob("*.img"), key=lambda item: item.name.lower()):
        if path.stat().st_size > MAX_SIZE:
            continue
        data = path.read_bytes()
        if data[:8] in (b"ANDROID!", b"VNDRBOOT") or data[:4] == b"AVB0":
            continue
        if len(data) > 1082 and struct.unpack_from("<H", data, 1080)[0] == 0xEF53:
            continue

        report = {
            "name": path.name,
            "size": len(data),
            "mtk_gfh": parse_mtk_gfh(data),
            "magic_offsets": {
                key: all_offsets(data, magic, limit=12)
                for key, magic in MAGICS.items()
            },
            "elf_headers": [],
            "interesting_strings": interesting_strings(data),
        }
        for offset in report["magic_offsets"]["elf"][:12]:
            header = parse_elf_header(data, offset)
            if header:
                header["offset"] = offset
                report["elf_headers"].append(header)

        lines += [f"## {path.name}", "", "```json"]
        lines += json.dumps(report, indent=2).splitlines()
        lines += ["```", ""]

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
