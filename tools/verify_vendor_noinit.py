import hashlib
import lz4.block
import struct
from pathlib import Path


MAX_BLOCK = 8 * 1024 * 1024
IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_noinit.img")


def decompress_legacy(data: bytes) -> bytes:
    output = bytearray()
    offset = 4
    while offset + 4 <= len(data):
        size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if offset + size > len(data):
            break
        output += lz4.block.decompress(
            data[offset : offset + size], uncompressed_size=MAX_BLOCK
        )
        offset += size
    return bytes(output)


def find_entry(cpio: bytes, target: str):
    offset = 0
    names = []
    while offset + 110 <= len(cpio):
        if cpio[offset : offset + 6] not in (b"070701", b"070702"):
            break
        fields = [
            int(cpio[offset + 6 + i * 8 : offset + 14 + i * 8], 16)
            for i in range(13)
        ]
        name_size = fields[11]
        file_size = fields[6]
        name = cpio[offset + 110 : offset + 110 + name_size - 1].decode(
            "latin1", errors="replace"
        )
        data_start = (offset + 110 + name_size + 3) & ~3
        data = cpio[data_start : data_start + file_size]
        names.append(name)
        if name == target:
            return data, names
        if name == "TRAILER!!!":
            break
        offset = (data_start + file_size + 3) & ~3
    return None, names


def main() -> None:
    data = IMAGE.read_bytes()
    size = struct.unpack_from("<I", data, 24)[0]
    cpio = decompress_legacy(data[4096 : 4096 + size])

    guard, names = find_entry(cpio, "lib/modules/oplus_security_guard.ko")
    print(f"total entries: {len(names)}")
    print(f"has init: {'init' in names}")
    print(f"guard present: {guard is not None}")

    if guard is not None:
        print(f"guard size: {len(guard)}")
        print(f"guard sha256: {hashlib.sha256(guard).hexdigest()}")
        print(
            "  .text+0x50c :",
            guard[0x1000 + 0x50C : 0x1000 + 0x510].hex(),
        )
        print(
            "  .init+0xb0  :",
            guard[0x2BE8 + 0xB0 : 0x2BE8 + 0xB4].hex(),
        )
        print("  rodata path :", bytes(guard[0x2088 + 0x823 : 0x2088 + 0x832]))

    print(f"original cpio order length matches: {len(names)}")


if __name__ == "__main__":
    main()
