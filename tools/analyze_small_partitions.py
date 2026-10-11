import collections
import hashlib
import json
import math
import os
import re
import struct
from pathlib import Path


ROOT = Path(r"E:\GeekFlashTool_Readback_20261010230748790")
OUT_DIR = ROOT / "small_partition_scan"
MAX_SIZE = 64 * 1024 * 1024
SKIP_NAMES = {"super.img"}

HIGH_VALUE_TERMS = [
    "androidboot",
    "avb",
    "bootloader",
    "bt_mac",
    "carrier",
    "device",
    "efuse",
    "eng",
    "fastboot",
    "flash",
    "frp",
    "gsm",
    "imei",
    "locked",
    "log",
    "mac",
    "meid",
    "model",
    "nv",
    "oplus",
    "oppo",
    "oneplus",
    "op5927",
    "persist",
    "php110",
    "product",
    "proinfo",
    "rpmb",
    "seccfg",
    "serial",
    "sim",
    "slot",
    "sota",
    "unlock",
    "verifiedboot",
    "wifi",
]

STRING_RE = re.compile(rb"[\x20-\x7e]{6,}")
UTF16_RE = re.compile(rb"(?:[\x20-\x7e]\x00){5,}")
GUID_RE = re.compile(
    rb"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
    rb"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
)
MAC_RE = re.compile(rb"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
IMEI_RE = re.compile(rb"\b\d{15}\b")
HEX_RE = re.compile(rb"\b[0-9A-Fa-f]{16,64}\b")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = collections.Counter(data)
    length = len(data)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def printable_strings(data: bytes, limit: int = 20000) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()

    for match in STRING_RE.finditer(data):
        value = match.group().decode("latin1", errors="replace")
        if value not in seen:
            seen.add(value)
            values.append(value)
            if len(values) >= limit:
                return values

    for match in UTF16_RE.finditer(data):
        value = match.group().decode("utf-16le", errors="replace")
        if value not in seen:
            seen.add(value)
            values.append(value)
            if len(values) >= limit:
                break

    return values


def parse_ext4(data: bytes) -> dict | None:
    if len(data) < 2048 or struct.unpack_from("<H", data, 1080)[0] != 0xEF53:
        return None

    (
        inode_count,
        block_count_lo,
        reserved_blocks_lo,
        free_blocks_lo,
        free_inodes,
        first_data_block,
        log_block_size,
        log_cluster_size,
        blocks_per_group,
        clusters_per_group,
        inodes_per_group,
    ) = struct.unpack_from("<11I", data, 1024 + 0x00)
    block_size = 1024 << log_block_size
    block_count = block_count_lo | (
        struct.unpack_from("<I", data, 1024 + 0x150)[0] << 32
    )
    volume_name = data[1024 + 0x78 : 1024 + 0x88].split(b"\x00", 1)[0]
    last_mount = data[1024 + 0x88 : 1024 + 0xC8].split(b"\x00", 1)[0]

    return {
        "block_size": block_size,
        "block_count": block_count,
        "inode_count": inode_count,
        "free_blocks": free_blocks_lo,
        "free_inodes": free_inodes,
        "first_data_block": first_data_block,
        "blocks_per_group": blocks_per_group,
        "clusters_per_group": clusters_per_group,
        "inodes_per_group": inodes_per_group,
        "volume_name": volume_name.decode("latin1", errors="replace"),
        "last_mount": last_mount.decode("latin1", errors="replace"),
    }


def parse_android_boot(data: bytes) -> dict:
    if data[:8] != b"ANDROID!":
        return {}

    header_version = struct.unpack_from("<I", data, 40)[0]
    if header_version in (3, 4):
        header = {
            "kernel_size": struct.unpack_from("<I", data, 8)[0],
            "ramdisk_size": struct.unpack_from("<I", data, 12)[0],
            "os_version": struct.unpack_from("<I", data, 16)[0],
            "header_size": struct.unpack_from("<I", data, 20)[0],
            "header_version": header_version,
            "cmdline": data[44:1580].split(b"\x00", 1)[0].decode(
                "latin1", errors="replace"
            ),
        }
        if header_version == 4 and len(data) >= 1584:
            header["signature_size"] = struct.unpack_from("<I", data, 1580)[0]
        return header

    return {
        "kernel_size": struct.unpack_from("<I", data, 8)[0],
        "kernel_addr": struct.unpack_from("<I", data, 12)[0],
        "ramdisk_size": struct.unpack_from("<I", data, 16)[0],
        "ramdisk_addr": struct.unpack_from("<I", data, 20)[0],
        "second_size": struct.unpack_from("<I", data, 24)[0],
        "second_addr": struct.unpack_from("<I", data, 28)[0],
        "tags_addr": struct.unpack_from("<I", data, 32)[0],
        "page_size": struct.unpack_from("<I", data, 36)[0],
        "os_version": struct.unpack_from("<I", data, 40)[0],
        "header_version": header_version,
        "header_size": struct.unpack_from("<I", data, 20)[0],
        "name": data[48:64].split(b"\x00", 1)[0].decode("latin1"),
        "cmdline": data[64:576].split(b"\x00", 1)[0].decode(
            "latin1", errors="replace"
        ),
    }


def parse_vendor_boot(data: bytes) -> dict:
    if data[:8] != b"VNDRBOOT":
        return {}

    result = {
        "header_version": struct.unpack_from("<I", data, 8)[0],
        "page_size": struct.unpack_from("<I", data, 12)[0],
        "kernel_addr": struct.unpack_from("<I", data, 16)[0],
        "ramdisk_addr": struct.unpack_from("<I", data, 20)[0],
        "vendor_ramdisk_size": struct.unpack_from("<I", data, 24)[0],
        "cmdline": data[28:2076].split(b"\x00", 1)[0].decode(
            "latin1", errors="replace"
        ),
        "tags_addr": struct.unpack_from("<I", data, 2076)[0],
        "name": data[2080:2096].split(b"\x00", 1)[0].decode("latin1"),
        "header_size": struct.unpack_from("<I", data, 2096)[0],
        "dtb_size": struct.unpack_from("<I", data, 2100)[0],
        "dtb_addr": struct.unpack_from("<Q", data, 2104)[0],
        "vendor_ramdisk_table_size": struct.unpack_from("<I", data, 2112)[0],
        "vendor_ramdisk_table_entry_num": struct.unpack_from("<I", data, 2116)[0],
        "vendor_ramdisk_table_entry_size": struct.unpack_from("<I", data, 2120)[0],
        "bootconfig_size": struct.unpack_from("<I", data, 2124)[0],
    }

    page_size = result["page_size"]
    if page_size:
        table_offset = align_up(
            align_up(4096 + result["vendor_ramdisk_size"], page_size)
            + result["dtb_size"],
            page_size,
        )
        entries = []
        for index in range(result["vendor_ramdisk_table_entry_num"]):
            offset = table_offset + index * result["vendor_ramdisk_table_entry_size"]
            if offset + 12 > len(data):
                break
            size, ramdisk_offset, ramdisk_type = struct.unpack_from("<III", data, offset)
            name = data[offset + 12 : offset + 44].split(b"\x00", 1)[0]
            entries.append(
                {
                    "size": size,
                    "offset": ramdisk_offset,
                    "type": ramdisk_type,
                    "name": name.decode("latin1", errors="replace"),
                }
            )
        result["vendor_ramdisk_table"] = entries
    return result


def parse_dtbo(data: bytes) -> dict:
    if len(data) < 32 or struct.unpack_from(">I", data, 0)[0] != 0xD7B7AB1E:
        return {}
    (
        magic,
        total_size,
        header_size,
        entry_size,
        entry_count,
        entries_offset,
        page_size,
        version,
    ) = struct.unpack_from(">8I", data, 0)
    entries = []
    for index in range(entry_count):
        offset = entries_offset + index * entry_size
        if offset + entry_size > len(data):
            break
        dt_size, dt_offset, dt_id, rev = struct.unpack_from(">4I", data, offset)
        entries.append(
            {
                "size": dt_size,
                "offset": dt_offset,
                "id": dt_id,
                "rev": rev,
            }
        )
    return {
        "magic": f"0x{magic:08x}",
        "total_size": total_size,
        "header_size": header_size,
        "entry_size": entry_size,
        "entry_count": entry_count,
        "entries_offset": entries_offset,
        "page_size": page_size,
        "version": version,
        "entries": entries,
    }


def parse_avb(data: bytes) -> dict:
    if data[:4] != b"AVB0" or len(data) < 256:
        return {}

    values = struct.unpack_from(">4sIIQQI", data, 0)
    result = {
        "magic": values[0].decode("latin1"),
        "required_major": values[1],
        "required_minor": values[2],
        "auth_block_size": values[3],
        "auxiliary_block_size": values[4],
        "algorithm_type": values[5],
    }
    fields = struct.unpack_from(
        ">QQQQQQQQQQQII48s",
        data,
        32,
    )
    names = [
        "hash_offset",
        "hash_size",
        "signature_offset",
        "signature_size",
        "public_key_offset",
        "public_key_size",
        "public_key_metadata_offset",
        "public_key_metadata_size",
        "descriptors_offset",
        "descriptors_size",
        "rollback_index",
    ]
    result.update(dict(zip(names, fields[:11])))
    result["flags"] = fields[11]
    result["rollback_index_location"] = fields[12]
    result["release_string"] = fields[13].split(b"\x00", 1)[0].decode(
        "latin1", errors="replace"
    )

    descriptors_start = 256 + result["auth_block_size"] + result["descriptors_offset"]
    descriptors_end = descriptors_start + result["descriptors_size"]
    result["descriptors"] = parse_avb_descriptors(
        data[descriptors_start:descriptors_end]
    )
    return result


def parse_avb_descriptors(data: bytes) -> list[dict]:
    descriptors = []
    offset = 0
    while offset + 16 <= len(data):
        tag, length = struct.unpack_from(">QQ", data, offset)
        offset += 16
        if offset + length > len(data):
            break
        payload = data[offset : offset + length]
        offset += length

        if tag == 0:
            key_end = payload.find(b"\x00")
            if key_end < 0:
                continue
            descriptors.append(
                {
                    "tag": "property",
                    "key": payload[:key_end].decode("latin1", errors="replace"),
                    "value": payload[key_end + 1 :].decode(
                        "latin1", errors="replace"
                    ),
                }
            )
        elif tag == 1:
            fields = struct.unpack_from(">QQQQQQQ", payload, 0)
            descriptors.append(
                {
                    "tag": "hashtree",
                    "image_size": fields[0],
                    "tree_offset": fields[1],
                    "tree_size": fields[2],
                    "data_block_size": fields[3],
                    "hash_block_size": fields[4],
                    "fdt_offset": fields[5],
                    "fdt_size": fields[6],
                }
            )
        elif tag == 2:
            image_size = struct.unpack_from(">Q", payload, 0)[0]
            hash_algorithm = payload[8:40].split(b"\x00", 1)[0]
            salt_len = struct.unpack_from(">I", payload, 40)[0]
            digest_len = struct.unpack_from(">I", payload, 44)[0]
            descriptors.append(
                {
                    "tag": "hash",
                    "image_size": image_size,
                    "hash_algorithm": hash_algorithm.decode(
                        "latin1", errors="replace"
                    ),
                    "salt_len": salt_len,
                    "digest_len": digest_len,
                }
            )
        elif tag == 3:
            flags, cmdline_len = struct.unpack_from(">II", payload, 0)
            cmdline = payload[8 : 8 + cmdline_len].split(b"\x00", 1)[0]
            descriptors.append(
                {
                    "tag": "kernel_cmdline",
                    "flags": flags,
                    "cmdline": cmdline.decode("latin1", errors="replace"),
                }
            )
        elif tag == 4:
            rollback_index_location = struct.unpack_from(">I", payload, 0)[0]
            partition_name = payload[4:40].split(b"\x00", 1)[0]
            public_key_len = struct.unpack_from(">I", payload, 40)[0]
            descriptors.append(
                {
                    "tag": "chain_partition",
                    "rollback_index_location": rollback_index_location,
                    "partition_name": partition_name.decode(
                        "latin1", errors="replace"
                    ),
                    "public_key_len": public_key_len,
                }
            )
        else:
            descriptors.append({"tag": tag, "length": length})
    return descriptors


def parse_sparse(data: bytes) -> dict:
    if len(data) < 28 or struct.unpack_from("<I", data, 0)[0] != 0xED26FF3A:
        return {}
    (
        magic,
        major,
        minor,
        file_header_size,
        chunk_header_size,
        block_size,
        total_blocks,
        total_chunks,
        checksum,
    ) = struct.unpack_from("<IHHHHIIII", data, 0)
    chunks = []
    offset = file_header_size
    for index in range(total_chunks):
        if offset + chunk_header_size > len(data):
            break
        chunk_type, reserved, chunk_blocks, total_size = struct.unpack_from(
            "<HHII", data, offset
        )
        chunks.append(
            {
                "index": index,
                "type": chunk_type,
                "blocks": chunk_blocks,
                "total_size": total_size,
            }
        )
        offset += total_size
    return {
        "major": major,
        "minor": minor,
        "block_size": block_size,
        "total_blocks": total_blocks,
        "total_chunks": total_chunks,
        "checksum": checksum,
        "chunks": chunks,
    }


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def detect_type(data: bytes, name: str) -> str:
    if not data or not any(data):
        return "all-zero"
    if data[:8] == b"ANDROID!":
        return "android-boot"
    if data[:8] == b"VNDRBOOT":
        return "vendor-boot"
    if len(data) >= 4 and struct.unpack_from(">I", data, 0)[0] == 0xD7B7AB1E:
        return "dtbo"
    if data[:4] == b"AVB0":
        return "avb-vbmeta"
    if struct.unpack_from("<I", data, 0)[0] == 0xED26FF3A:
        return "android-sparse"
    if len(data) >= 1082 and struct.unpack_from("<H", data, 1080)[0] == 0xEF53:
        return "ext4"
    if data[:4] == b"\x7fELF":
        return "elf"
    if data[:4] == b"\x28\xb5\x2f\xfd":
        return "zstd"
    if data[:4] == b"\x04\x22\x4d\x18":
        return "lz4"
    if data[:2] == b"\x1f\x8b":
        return "gzip"
    if data[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if data[:3] == b"BZh":
        return "bzip2"
    if data[:4] == b"\xd0\x0d\xfe\xed":
        return "fdt"
    if data[:6] in (b"070701", b"070702"):
        return "cpio"
    if data[0x1FE:0x200] == b"\x55\xaa" and data[0x200:0x208] == b"EFI PART":
        return "gpt"
    if data[0x200:0x208] == b"EFI PART":
        return "gpt"
    if data[0x1FE:0x200] == b"\x55\xaa":
        return "mbr"
    if name.endswith(".img") and data.count(b"\x00") / len(data) > 0.95:
        return "mostly-zero"
    return "unknown"


def histogram_nonzero(data: bytes, bucket: int = 0x1000) -> list[dict]:
    result = []
    for offset in range(0, len(data), bucket):
        chunk = data[offset : offset + bucket]
        nonzero = sum(byte != 0 for byte in chunk)
        if nonzero:
            result.append({"offset": offset, "nonzero": nonzero})
    return result


def first_nonzero(data: bytes) -> int | None:
    for offset, byte in enumerate(data):
        if byte:
            return offset
    return None


def high_value_strings(strings: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = collections.defaultdict(list)
    lowered = [(value, value.lower()) for value in strings]
    for term in HIGH_VALUE_TERMS:
        matches = [
            value
            for value, lower in lowered
            if term in lower
        ]
        if matches:
            result[term] = matches[:100]
    return dict(result)


def file_report(path: Path) -> dict:
    data = path.read_bytes()
    strings = printable_strings(data)
    report = {
        "name": path.name,
        "size": len(data),
        "sha256": sha256_file(path),
        "entropy": round(entropy(data), 6),
        "zero_ratio": round(data.count(b"\x00") / len(data), 6),
        "first_nonzero": first_nonzero(data),
        "type": detect_type(data, path.name),
        "magic_hex": data[:32].hex(),
        "strings_count": len(strings),
        "high_value_strings": high_value_strings(strings),
        "guids": sorted({"".join(match.group().decode("latin1")) for match in GUID_RE.finditer(data)}),
        "macs": sorted({match.group().decode("latin1") for match in MAC_RE.finditer(data)}),
        "imeis": sorted({match.group().decode("latin1") for match in IMEI_RE.finditer(data)}),
        "long_hex": sorted({match.group().decode("latin1") for match in HEX_RE.finditer(data)})[:200],
        "nonzero_blocks": histogram_nonzero(data)[:512],
    }

    ext4 = parse_ext4(data)
    if ext4:
        report["ext4"] = ext4

    android_boot = parse_android_boot(data)
    if android_boot:
        report["android_boot"] = android_boot

    vendor_boot = parse_vendor_boot(data)
    if vendor_boot:
        report["vendor_boot"] = vendor_boot

    dtbo = parse_dtbo(data)
    if dtbo:
        report["dtbo"] = dtbo

    avb = parse_avb(data)
    if avb:
        report["avb"] = avb

    sparse = parse_sparse(data)
    if sparse:
        report["sparse"] = sparse

    strings_path = OUT_DIR / f"{path.stem}.strings.txt"
    strings_path.write_text("\n".join(strings), encoding="utf-8")
    return report


def write_markdown(reports: list[dict]) -> None:
    lines = [
        "# Small Partition Deep Scan",
        "",
        f"Scanned files: {len(reports)}",
        "",
        "| File | Type | Size | Entropy | Zero ratio | Findings |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for report in reports:
        findings = []
        for key in ("android_boot", "vendor_boot", "dtbo", "avb", "ext4", "sparse"):
            if key in report:
                findings.append(key)
        if report["imeis"]:
            findings.append("IMEI")
        if report["macs"]:
            findings.append("MAC")
        if report["guids"]:
            findings.append("GUID")
        if report["high_value_strings"]:
            findings.append(
                "terms:" + ",".join(sorted(report["high_value_strings"]))
            )
        lines.append(
            f"| {report['name']} | {report['type']} | {report['size']} | "
            f"{report['entropy']} | {report['zero_ratio']} | "
            f"{'; '.join(findings)} |"
        )
    lines.append("")
    for report in reports:
        lines.append(f"## {report['name']}")
        lines.append("")
        lines.append(f"- Type: `{report['type']}`")
        lines.append(f"- Size: `{report['size']}`")
        lines.append(f"- SHA256: `{report['sha256']}`")
        lines.append(f"- Entropy: `{report['entropy']}`")
        lines.append(f"- Zero ratio: `{report['zero_ratio']}`")
        lines.append(f"- First nonzero: `{report['first_nonzero']}`")
        lines.append(f"- Magic: `{report['magic_hex']}`")
        for key in ("android_boot", "vendor_boot", "dtbo", "avb", "ext4", "sparse"):
            if key in report:
                lines.append(f"- {key}: `{json.dumps(report[key], ensure_ascii=False)}`")
        if report["imeis"]:
            lines.append(f"- IMEI candidates: `{report['imeis']}`")
        if report["macs"]:
            lines.append(f"- MAC candidates: `{report['macs']}`")
        if report["guids"]:
            lines.append(f"- GUID candidates: `{report['guids']}`")
        if report["high_value_strings"]:
            lines.append(
                f"- High-value strings: `{json.dumps(report['high_value_strings'], ensure_ascii=False)}`"
            )
        lines.append(
            f"- Nonzero block count: `{len(report['nonzero_blocks'])}`"
        )
        lines.append("")
    (OUT_DIR / "small_partition_scan.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    reports = []
    for path in sorted(ROOT.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file():
            continue
        if path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() in {".md", ".txt"}:
            continue
        if path.stat().st_size > MAX_SIZE:
            continue
        reports.append(file_report(path))

    (OUT_DIR / "small_partition_scan.json").write_text(
        json.dumps(reports, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(reports)
    print(f"scanned={len(reports)}")
    print(OUT_DIR / "small_partition_scan.md")
    print(OUT_DIR / "small_partition_scan.json")


if __name__ == "__main__":
    main()
