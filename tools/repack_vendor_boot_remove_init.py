import hashlib
import lz4.block
import struct
from pathlib import Path


SRC = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_patched_initfix.img")
ORIGINAL = Path(r"E:\GeekFlashTool_Readback_20261010230748790\vendor_boot_a.img")
OUT = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_noinit_initfix.img")

PAGE = 4096
CPIO_SIZE = 87_254_272
MAX_BLOCK = 8 * 1024 * 1024
LZ4_MAGIC = 0x184C2102


def decompress_legacy(data: bytes) -> bytes:
    assert struct.unpack_from("<I", data, 0)[0] == LZ4_MAGIC
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


def compress_legacy(data: bytes) -> bytes:
    output = bytearray(struct.pack("<I", LZ4_MAGIC))
    for start in range(0, len(data), MAX_BLOCK):
        block = data[start : start + MAX_BLOCK]
        compressed = lz4.block.compress(
            block, mode="high_compression", compression=12, store_size=False
        )
        output += struct.pack("<I", len(compressed))
        output += compressed
    return bytes(output)


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def strip_init(cpio: bytes) -> tuple[bytes, list[str]]:
    output = bytearray()
    offset = 0
    removed = []
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
        record = cpio[offset:end]

        if name == "init":
            removed.append(name)
        else:
            output += record

        if name == "TRAILER!!!":
            break
        offset = end

    return bytes(output), removed


def main() -> None:
    base = bytearray(SRC.read_bytes())
    original = ORIGINAL.read_bytes()

    src_ramdisk_size = struct.unpack_from("<I", base, 24)[0]
    compressed = bytes(base[PAGE : PAGE + src_ramdisk_size])
    cpio = decompress_legacy(compressed)
    if len(cpio) != CPIO_SIZE:
        raise ValueError(f"unexpected cpio size {len(cpio)}")

    stripped, removed = strip_init(cpio)
    if removed != ["init"]:
        raise ValueError(f"unexpected removed entries: {removed}")
    # Re-add the CPIO trailer padding so the archive stays well formed.
    stripped = stripped.ljust(len(cpio), b"\x00")

    repacked = compress_legacy(stripped)
    stream_size = len(repacked)

    original_ramdisk_size = struct.unpack_from("<I", original, 24)[0]
    dtb_size = struct.unpack_from("<I", original, 2100)[0]
    table_size = struct.unpack_from("<I", original, 2112)[0]
    bootconfig_size = struct.unpack_from("<I", original, 2124)[0]

    original_dtb = align(PAGE + original_ramdisk_size, PAGE)
    original_table = align(original_dtb + dtb_size, PAGE)
    original_bootconfig = align(original_table + table_size, PAGE)

    dtb = bytes(original[original_dtb : original_dtb + dtb_size])
    table = bytes(original[original_table : original_table + table_size])
    bootconfig = bytes(
        original[original_bootconfig : original_bootconfig + bootconfig_size]
    )

    output = bytearray(base)
    output[PAGE : PAGE + stream_size] = repacked
    output[PAGE + stream_size : PAGE + original_ramdisk_size] = (
        b"\x00" * (original_ramdisk_size - stream_size)
    )
    struct.pack_into("<I", output, 24, original_ramdisk_size)

    new_dtb = align(PAGE + stream_size, PAGE)
    new_table = align(new_dtb + dtb_size, PAGE)
    new_bootconfig = align(new_table + table_size, PAGE)
    output[new_dtb : new_dtb + dtb_size] = dtb
    output[new_table : new_table + table_size] = table
    if bootconfig:
        output[new_bootconfig : new_bootconfig + bootconfig_size] = bootconfig

    OUT.write_bytes(output)

    check = decompress_legacy(
        bytes(output[PAGE : PAGE + stream_size])
    )
    names = []
    offset = 0
    while offset + 110 <= len(check):
        if check[offset : offset + 6] not in (b"070701", b"070702"):
            break
        fields = [
            int(check[offset + 6 + i * 8 : offset + 14 + i * 8], 16)
            for i in range(13)
        ]
        name_size = fields[11]
        file_size = fields[6]
        name = check[offset + 110 : offset + 110 + name_size - 1].decode(
            "latin1", errors="replace"
        )
        names.append(name)
        data_start = (offset + 110 + name_size + 3) & ~3
        offset = (data_start + file_size + 3) & ~3
        if name == "TRAILER!!!":
            break

    print(f"output: {OUT}")
    print(f"sha256: {hashlib.sha256(output).hexdigest()}")
    print(f"lz4_stream_size: 0x{stream_size:x}")
    print(f"removed: {removed}")
    print(f"init_in_new_ramdisk: {'init' in names}")
    print(f"entries: {len(names)}")
    print(f"dtb_offset: 0x{new_dtb:x}")
    print("verify .init.text patch kept: "
          f"{check[0x26B9714 + 0x2C98:0x26B9714 + 0x2C9C].hex()}")
    print("verify ksud path kept: "
          f"{bytes(check[0x26B9714 + 0x28AB:0x26B9714 + 0x28BA])!r}")


if __name__ == "__main__":
    main()
