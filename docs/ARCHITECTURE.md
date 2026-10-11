# 方案与决策记录

## 1. 目标

在 OnePlus Ace 2V（MT6983）上同时满足：

- `verifiedbootstate=green` + `flash.locked=1`（保持 BL 锁定状态）
- root 可用
- **无内核模块**（内建 KernelSU，非 LKM）
- SuSFS 隐藏能力
- 内核对外呈现与厂商原厂一致（版本串、config、模块 ABI）

## 2. 为什么必须编进内核本体

SuSFS 无法做成可加载模块，依据：

- `fs/susfs.c`（1538 行）**没有任何 `EXPORT_SYMBOL`**
- 补丁修改了 `struct nameidata`、`fs/namei.c`、`fs/stat.c`、`fs/open.c`、
  `mm/memory.c`、`security/selinux/*` 等**核心数据结构与调用点**
- `fs/Makefile` 中 `obj-$(CONFIG_KSU_SUSFS) += susfs.o`

也就是说 SuSFS 与 KernelSU 必须同处内核本体、一起内建编译。
这与"零模块"目标方向一致。

## 3. 组件选型

| 组件 | 选择 | 理由 |
|---|---|---|
| KernelSU | SukiSU-Ultra `builtin` 分支 | 官方为手动 hook 内核准备的变体，**自带 `CONFIG_KSU_SUSFS` 全套** |
| SuSFS | `gki-android12-5.10`（v2.3.0） | API 与 builtin 分支完全对应 |
| 内核源 | OnePlusOSS `android_kernel_5.10_oneplus_mt6983` | 唯一公开对应源 |
| 编译配置 | **设备 `/proc/config.gz` 导出的真机 config** | 保证与原厂优化一致，不降级 |

注：`simonpunk/susfs4ksu` 已不可访问，现行活跃源为 `ShirkNeko/susfs4ksu`。

## 4. 三条硬约束（每条都踩过坑）

### 4.1 AVB 必须搬运原厂签名 vbmeta

`avbtool add_hash_footer --algorithm NONE` 生成的是**无签名**结构。
实测直接导致：第一屏 logo → 无限重启。

正确做法：从原厂 boot 末尾取出 `AVBf` footer，读取其
`original_image_size / vbmeta_offset / vbmeta_size`（**大端**），
把原厂签名的 `AVB0` vbmeta 块**原样搬运**到新的内容末尾，
只重写 footer 中的偏移值。

参考实现：`scripts/pack_boot2.py`

### 4.2 gzip 头必须是纯净格式

- 原厂：`1f 8b 08 00 00 00 00 00 02 03`（`FLG=0x00`，无 FNAME，OS=3）
- Python `gzip.compress()` 默认为 `FLG=0x08`（带 FNAME）+ OS=255

用 `zlib` 手工构造头部（`FLG=0, XFL=2, OS=3`）以对齐原厂。

参考实现：`scripts/gz_clean.py`

### 4.3 必须使用完整 LLVM 工具链

`HAS_LTO_CLANG` 依赖 `nm`/`ar` 为 LLVM 版本（Kconfig 里 `grep -qi llvm`）。
主机默认 GNU binutils 会导致依赖判定失败，`olddefconfig` **静默丢弃**
`LTO_CLANG_FULL`、`CFI_CLANG`、`KASAN_HW_TAGS`、`SHADOW_CALL_STACK`，
进而使**所有导出符号 CRC 与厂商模块不匹配**。

必须让 `clang`、`ld.lld`、`llvm-nm`、`llvm-ar`、`llvm-objcopy`、
`llvm-objdump`、`llvm-readelf`、`llvm-strip` 全部来自同一 LLVM 工具链。

## 5. 配置对齐（关键项）

设备 stock 与重建内核必须一致的项：

```
CONFIG_LTO_CLANG_FULL=y
CONFIG_CFI_CLANG=y
CONFIG_CFI_CLANG_SHADOW=y
CONFIG_SHADOW_CALL_STACK=y
CONFIG_KASAN_HW_TAGS=y
CONFIG_ARM64_MTE=y
CONFIG_ARM64_4K_PAGES=y
CONFIG_ARM64_VA_BITS=39
CONFIG_ARM64_PA_BITS=48
CONFIG_RANDOMIZE_BASE=y
CONFIG_MODVERSIONS=y
```

差异应仅限于新增的 `CONFIG_KSU*` / `CONFIG_KSU_SUSFS*`。

## 6. ABI / 模块兼容性

设备有约 469 个厂商模块。因为内核开启 `CONFIG_MODVERSIONS`，
模块加载时 `same_magic()` **跳过 vermagic 版本串**，只比较
`SMP preempt mod_unload modversions aarch64` 与**导出符号 CRC**。

因此重建内核的 git hash 不同并不影响加载，关键是 CRC 一致。

验证方法：`scripts/abi_check.py`

抽样 11 个模块（含 7 MB 的 wlan、5.9 MB 的 mtk_aie、5.4 MB 的 oplus_chg），
共 1860 个版本化符号，`mismatch` 合计为 0。

> 注意：脚本报出的 `MISSING` 大多不是内核缺失，而是**由其它厂商模块导出**
> （如 `conninfra_reg_readable` 来自 `conninfra.ko`、`cmdq_pkt_write`
> 来自 `mtk_cmdq_drv_ext.ko`）。判定兼容性应以 `mismatch` 为准。

## 7. 厂商源码拼接

OnePlusOSS 内核仓库**不含** OPPO 私有部分。内核树里大量目录是指向
`vendor/` 的**符号链接**，解析目标是内核目录的**兄弟目录**：

```
/root/.../op/kernel     内核源
/root/.../op/vendor     ← 由 modules 仓库填充
```

另有 `kernel/oplus_cpu/` 需从 modules 仓库的
`vendor/oplus/kernel/cpu` 合并进来（否则 Kconfig 解析失败）。

模块仓库：`OnePlusOSS/android_kernel_modules_oneplus_mt6983`

## 8. 内核信息伪装

### 8.1 UTS 版本串

不改源码，通过内核自带环境变量覆盖 `scripts/mkcompile_h`：

```
KBUILD_BUILD_VERSION=1
KBUILD_BUILD_USER=build-user
KBUILD_BUILD_HOST=build-host
KBUILD_BUILD_TIMESTAMP="Sun Mar 5 22:34:08 UTC 2023"
```

### 8.2 内嵌 config

`/proc/config.gz` 的内容来自编译时 `.incbin` 进内核的
`kernel/config_data.gz`。将该文件的生成源从 `.config` 指向**原厂 config**：

```make
$(obj)/config_data: arch/arm64/configs/stock_defconfig FORCE
```

这是 SuSFS 官方文档推荐的做法。

### 8.3 效果对照（普通用户可读面）

| 检测面 | 伪装前 | 伪装后 |
|---|---|---|
| `/proc/version` | `(root@autodl-container-...) #2 ... Oct 11 ... 2026` | `(build-user@build-host) #1 ... Sun Mar 5 22:34:08 UTC 2023` |
| `uname -a` | 同上 | 同上（与原厂一致） |
| `zcat /proc/config.gz \| grep KSU` | **13 行命中** | **0 行** |

### 8.4 已确认干净的面

- `/proc/kallsyms`：普通用户 `Permission denied`
- `/proc/cmdline`：普通用户 `Permission denied`
- `/sys/module/`：无 `kernelsu` 条目
- `/proc`、`/sys/kernel`：无 `ksu` / `susfs` 节点

## 9. 已知局限

- **无法在内核层隐藏管理器包名**。`pm list packages` 走 binder IPC
  （检测 App → system_server），内核能拦的是 VFS 层，拦不到 binder
  回复中的字符串。桌面图标（launcher `queryIntentActivities`）与
  `pm list` 走**同一个 PM 服务**，内核无法区分调用方。
  标准解法是"随机包名"（hide manager），需要重编管理器 APK 并保持
  内核侧签名白名单一致。
- 源码为 A.05，设备为 A.08，两者差异未能完全枚举；实测重建内核可正常
  启动并加载厂商模块。
