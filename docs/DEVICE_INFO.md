# 设备与固件基线

## 硬件

| 项目 | 值 |
|---|---|
| 机型 | OnePlus Ace 2V |
| 型号代码 | `OP5927` |
| 设备代号 | `PHP110` |
| 平台 | MediaTek MT6983（Dimensity 9000） |
| 存储 | UFS（`BOOT_1` / `BOOT_2` 即 LU0 / LU1 引导 LUN） |

## 固件

| 项目 | 值 |
|---|---|
| 版本 | `PHP110_11_A.08` |
| 指纹 | `OnePlus/PHP110/OP5927:13/SP1A.210812.016/T.eb981a_3c91:user/release-keys` |
| Android | 13 |
| 安全补丁 | `2023-02-05` |
| 内核 | `5.10.110-android12-9-g4d2e7c69e8b4` |
| 内部分区版本 | `T.eb981a_3c91` |

## 分区布局（A/B）

| 分区 | A 槽 | B 槽 |
|---|---|---|
| boot | `/dev/block/sdc39` | `/dev/block/sdc74` |
| vendor_boot | `/dev/block/sdc40` | `/dev/block/sdc75` |
| init_boot | `/dev/block/sdc41` | `/dev/block/sdc76` |
| dtbo | `/dev/block/sdc42` | `/dev/block/sdc79` |

分区总数 87（见 `MT907_Android_scatter.txt`）。

## 引导链镜像

### lk_a.img（5242880 字节）

| 子镜像 | 偏移 | 大小 |
|---|---|---|
| `lk` | `0x0` | 1030976 |
| `bl2_ext` | `0xfcc10` | 811920 |
| `aee` | `0x1c4070` | 1101168 |
| `lk_main_dtb` | `0x2d1eb0` | 321590 |

每个子镜像后跟一对 `cert1`(1733 B) + `cert2`(1011 B)，
`sec_level=0`（SHA-256），RSA-2048 + RSASSA-PSS。

### preloader（BOOT_1.img / BOOT_2.img）

- 大小：各 `0x400000`（4 MB）
- 未压缩，含 ARM64 代码与 libsec 字符串
- A 槽构建时间：20230306-064053
- B 槽构建时间：20230223-000010
- 载入基址约 `0x11e56000`

## boot 分区结构

| 字段 | 值 |
|---|---|
| header_version | 4（实际按 v0 布局解析，`header_size=1584`） |
| kernel_size | 20317798（gzip 压缩） |
| ramdisk_size | 1650577（lz4 legacy） |
| os_version | `0x18000172` |
| AVB | `SHA256_RSA2048`，vbmeta 1600 字节 |

### vendor_boot 分区

| 字段 | 值 |
|---|---|
| header_version | 4 |
| vendor_ramdisk_size | 32476753 |
| **dtb_size** | **321654** |
| **dtb_addr** | **0x47c80000** |

**DTB 在 vendor_boot 内，不在 boot 分区**。所以换内核的时候 DTB 不用动，
它会跟着 vendor_boot 一起保持原样。

不过这套方案里 vendor_boot 的 ramdisk 还是改了两处（删 `init`、
给安全守卫模块打补丁），DTB 本身没动。具体见 `FLASHING.md`。

## 厂商模块

- `/vendor/lib/modules/` 约 469 个模块
- vendor_boot ramdisk 内含约 269 个 `.ko`
- 模块 vermagic：`5.10.110-android12-9-g4d2e7c69e8b4 SMP preempt mod_unload modversions aarch64`

## 相关 CVE 状态

| CVE | 状态 |
|---|---|
| CVE-2025-20730 | 存在（preloader 未修补） |
| CVE-2023-20696 | 不在影响范围 |

详见 `CVE_COMPARISON.md`。
