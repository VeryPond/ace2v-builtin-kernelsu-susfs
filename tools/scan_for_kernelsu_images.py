import gzip
import lz4.block
import struct
from pathlib import Path


ROOTS = [
    Path(r"E:\_probe_pwnage24mtk"),
    Path(r"E:\GeekFlashTool_Readback_20261010230748790"),
    Path(r"C:\Users\11308\Desktop"),
    Path(r"C:\Users\11308\Downloads"),
    Path(r"E:\hc\S\5de90acd4f2a429492c8d20e71fe6044\images"),
]
MAX_BLOCK = 8 * 1024 * 1024


def decompress_legacy(data: bytes) -> bytes:
    output = bytearray()
    offset = 4
    while offset < len(data):
        size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        output += lz4.block.decompress(
            data[offset : offset + size],
            uncompressed_size=MAX_BLOCK,
        )
        offset += size
    return bytes(output)


def decompress_maybe(data: bytes) -> bytes | None:
    try:
        if struct.unpack_from("<I", data, 0)[0] == 0x184C2102:
            return decompress_legacy(data)
        if data[:2] == b"\x1f\x8b":
            return gzip.decompress(data)
    except Exception:
        return None
    return None


def ramdisk_from_image(path: Path, data: bytes) -> tuple[bytes, str] | None:
    if data[:8] == b"ANDROID!":
        header_version = struct.unpack_from("<I", data, 40)[0]
        if header_version not in (3, 4):
            return None
        kernel_size = struct.unpack_from("<I", data, 8)[0]
        ramdisk_size = struct.unpack_from("<I", data, 12)[0]
        page = 4096
        offset = ((4096 + kernel_size + page - 1) // page) * page
        return data[offset : offset + ramdisk_size], "boot"

    if data[:8] == b"VNDRBOOT":
        ramdisk_size = struct.unpack_from("<I", data, 24)[0]
        return data[4096 : 4096 + ramdisk_size], "vendor_boot"
    return None


def main() -> None:
    seen = set()
    matches = []
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.stat().st_size > 300 * 1024 * 1024:
                continue
            try:
                with path.open("rb") as handle:
                    header = handle.read(16)
                    if header[:8] not in (b"ANDROID!", b"VNDRBOOT"):
                        continue
                    handle.seek(0)
                    data = handle.read()
            except OSError:
                continue
            if id(path) in seen:
                continue
            seen.add(id(path))
            result = ramdisk_from_image(path, data)
            if not result:
                continue
            ramdisk, kind = result
            cpio = decompress_maybe(ramdisk)
            if cpio is None:
                continue
            if b"name=kernelsu" in cpio or b"kernelsu.ko" in cpio:
                vermagic = b""
                for marker in (
                    b"5.10.110-android12-9-g4d2e7c69e8b4",
                    b"5.10.252",
                    b"6.6.127",
                ):
                    if marker in cpio:
                        vermagic = marker
                        break
                matches.append(
                    {
                        "path": str(path),
                        "kind": kind,
                        "ramdisk_size": len(ramdisk),
                        "cpio_size": len(cpio),
                        "vermagic": vermagic.decode("latin1"),
                    }
                )
    for match in matches:
        print(match)
    print(f"matches={len(matches)}")


if __name__ == "__main__":
    main()
