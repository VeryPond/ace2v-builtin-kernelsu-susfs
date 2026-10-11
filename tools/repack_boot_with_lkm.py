import hashlib
import lz4.block
import struct
from pathlib import Path


IMAGE = Path(r"C:\Users\11308\Desktop\kernelsu_patched_20100101_000320.img")
LKM = Path(r"E:\_tools\lkm-a12-510\android12-5.10_kernelsu.ko")
OUT = Path(r"E:\_probe_pwnage24mtk\boot_a_kernelsu_versions_fixed.img")

PAGE = 4096
MAX_BLOCK = 8 * 1024 * 1024


def decompress_legacy(data: bytes) -> bytes:
    output = bytearray()
    offset = 4
    while offset < len(data):
        size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        output += lz4.block.decompress(
            data[offset : offset + size], uncompressed_size=MAX_BLOCK
        )
        offset += size
    return bytes(output)


def compress_legacy(data: bytes) -> bytes:
    output = bytearray(struct.pack("<I", 0x184C2102))
    for start in range(0, len(data), MAX_BLOCK):
        block = data[start : start + MAX_BLOCK]
        compressed = lz4.block.compress(
            block, mode="high_compression", compression=12, store_size=False
        )
        output += struct.pack("<I", len(compressed))
        output += compressed
    return bytes(output)


def parse_cpio(cpio: bytes):
    entries = []
    offset = 0
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
        end = (data_start + file_size + 3) & ~3
        entries.append((name, fields, cpio[offset:end], data_start, file_size))
        if name == "TRAILER!!!":
            break
        offset = end
    return entries


def build_cpio(entries) -> bytes:
    output = bytearray()
    for name, fields, record, data_start, file_size in entries:
        output += record
    return bytes(output)


def main() -> None:
    data = IMAGE.read_bytes()
    kernel_size = struct.unpack_from("<I", data, 8)[0]
    ramdisk_size = struct.unpack_from("<I", data, 12)[0]
    ramdisk_offset = ((PAGE + kernel_size + PAGE - 1) // PAGE) * PAGE
    ramdisk = data[ramdisk_offset : ramdisk_offset + ramdisk_size]
    cpio = decompress_legacy(ramdisk)
    entries = parse_cpio(cpio)

    new_lkm = LKM.read_bytes()
    replaced = False
    output_cpio = bytearray()
    for name, fields, record, data_start, file_size in entries:
        if name == "lib/modules/kernelsu.ko":
            # Rebuild this record with the corrected LKM payload.
            old_data_start = data_start
            header = bytearray(record[:old_data_start])
            fields = fields.copy()
            fields[6] = len(new_lkm)
            header = bytearray(
                "070701".encode()
                + b"".join(f"{value:08x}".encode() for value in fields)
                + name.encode()
                + b"\x00"
            )
            header = header.ljust(110 + len(name) + 1, b"\x00")
            while len(header) % 4:
                header += b"\x00"
            record = bytes(header) + new_lkm
            while len(record) % 4:
                record += b"\x00"
            replaced = True
        output_cpio += record

    if not replaced:
        raise ValueError("kernelsu.ko not found in boot ramdisk")

    new_ramdisk = compress_legacy(bytes(output_cpio))
    output = bytearray(data)
    output[ramdisk_offset : ramdisk_offset + ramdisk_size] = b"\x00" * ramdisk_size
    output[ramdisk_offset : ramdisk_offset + len(new_ramdisk)] = new_ramdisk
    struct.pack_into("<I", output, 12, len(new_ramdisk))

    OUT.write_bytes(output)
    print(f"output: {OUT}")
    print(f"sha256: {hashlib.sha256(output).hexdigest()}")
    print(f"lkm_size: {len(new_lkm)}")
    print(f"ramdisk_size: 0x{len(new_ramdisk):x} (was 0x{ramdisk_size:x})")
    print(f"ramdisk_offset: 0x{ramdisk_offset:x}")


if __name__ == "__main__":
    main()
