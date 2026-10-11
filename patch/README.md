# 补丁说明

## 文件

| 文件 | 内容 |
|---|---|
| `0001-susfs-kernelsu-core-changes.patch` | 对内核源码的全部改动（29 个文件，+1688/-6） |
| `new_host_fixups.sh` 引用的 `fdinfo.c` 修正 | 已包含在上述 patch 中 |
| `stock_defconfig` | 原厂 config，用于伪装 `/proc/config.gz`（见 `configs/`） |

## patch 覆盖的改动分类

**A. SuSFS 内核侧（上游补丁，来自 ShirkNeko/susfs4ksu）**

`fs/namei.c`、`fs/open.c`、`fs/stat.c`、`fs/namespace.c`、`fs/exec.c`、
`fs/readdir.c`、`fs/read_write.c`、`fs/statfs.c`、`fs/super.c`、
`fs/proc/*`、`fs/proc_namespace.c`、`kernel/kallsyms.c`、`kernel/reboot.c`、
`kernel/sys.c`、`mm/memory.c`、`security/selinux/*`、`drivers/input/input.c`、
`fs/Makefile`

**B. 本仓库自行处理的部分**

| 文件 | 改动 |
|---|---|
| `fs/notify/fdinfo.c` | 手工修正 hunk，替换 `inotify_mark_user_mask()` 为内联 `mask` |
| `kernel/Makefile` | `config_data` 生成源指向 `stock_defconfig` |
| `scripts/setlocalversion` | 去掉 `-dirty` 与 `${scm:++}` 后缀 |
| `include/linux/susfs_def.h` | 追加 `VMA_PAD_START` 兼容定义 |
| `drivers/Makefile`、`drivers/Kconfig` | 挂载 `drivers/kernelsu` |

**C. 不包含在 patch 中的内容**

- `KernelSU/` 目录（来自 SukiSU-Ultra builtin 分支，建议直接 clone）
- `kernel/oplus_cpu/`（来自 modules 仓库，属厂商私有源码）
- `vendor/` 符号链接目标（来自 modules 仓库）
- `arch/arm64/configs/stock_defconfig`（见 `configs/`）

## 应用顺序

1. 准备内核源码（OnePlusOSS）
2. 应用本 patch
3. 合并 modules 仓库的 `vendor/` 与 `kernel/oplus_cpu`
4. 放入 KernelSU builtin 源码并链接 `drivers/kernelsu`
5. 编译
