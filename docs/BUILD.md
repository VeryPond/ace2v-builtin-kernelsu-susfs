# 完整编译流程

## 环境

- Linux x86_64，建议 16 核以上、32 GB 内存以上（Full LTO 链接峰值内存约 12 GB）
- 磁盘：源码约 1.5 GB + 输出约 3 GB
- Python 3，`lz4`、`pyelftools` 模块

工具链（Android clang r416183b / 12.0.5，与设备原厂一致）：

```
clang  ld.lld  llvm-nm  llvm-ar  llvm-objcopy  llvm-objdump  llvm-readelf  llvm-strip
```

## 步骤

### 1. 准备源码

```sh
mkdir -p $OP && cd $OP
git clone -b oneplus/mt6983_t_13.0_oneplus_ace_2v --depth 1 \
  https://github.com/OnePlusOSS/android_kernel_5.10_oneplus_mt6983 kernel
git clone -b oneplus/mt6983_t_13.0_oneplus_ace_2v --depth 1 \
  https://github.com/OnePlusOSS/android_kernel_modules_oneplus_mt6983 modules
```

SuSFS kernel 侧补丁：

```sh
git clone -b gki-android12-5.10 https://github.com/ShirkNeko/susfs4ksu susfs510
```

KernelSU builtin 分支：

```sh
git clone https://github.com/SukiSU-Ultra/SukiSU-Ultra sukisu
cd sukisu && git checkout builtin
```

### 2. 集成

```sh
bash scripts/new_host_integrate.sh
bash scripts/new_host_fixups.sh
```

集成脚本做的事：

- 把 modules 仓库的 `vendor/` 放到内核的**兄弟目录**
- 把 `vendor/oplus/kernel/cpu` 合并为 `kernel/oplus_cpu`
- 复制 `fs/susfs.c`、`include/linux/susfs.h`、`include/linux/susfs_def.h`
- 应用 `50_add_susfs_in_gki-android12-5.10.patch`
- 把 KernelSU 放入内核树并链接 `drivers/kernelsu`
- 屏蔽 KernelSU Makefile 中的联网调用（`git fetch --unshallow` / curl）

补丁在 `fs/notify/fdinfo.c` 处有一处冲突：MTK 树使用内联
`mask = mark->mask & IN_ALL_EVENTS`，而补丁假设存在
`inotify_mark_user_mask()`。已由 `scripts/new_host_fixups.sh` 用修好的版本覆盖。

### 3. 生成安全 config

```sh
bash scripts/hide_config.sh
```

把真机 config 存为 `arch/arm64/configs/stock_defconfig`，并让
`kernel/config_data` 从它生成。

### 4. 编译（含版本串伪装）

```sh
bash scripts/build_spoofed.sh
```

核心环境变量：

```
ARCH=arm64  LLVM=1  LLVM_IAS=1
CROSS_COMPILE=aarch64-linux-gnu-  CLANG_TRIPLE=aarch64-linux-gnu-
KBUILD_BUILD_VERSION=1
KBUILD_BUILD_USER=build-user
KBUILD_BUILD_HOST=build-host
KBUILD_BUILD_TIMESTAMP="Sun Mar 5 22:34:08 UTC 2023"
KSU_VERSION=40900
```

产物：`kout/arch/arm64/boot/Image`

### 5. 校验 ABI

```sh
python3 scripts/abi_check.py
```

要求：所有模块 `mismatch: 0`。

### 6. 打包 boot

```sh
python3 scripts/gz_clean.py kout/arch/arm64/boot/Image kout/arch/arm64/boot/Image.gz
python3 scripts/pack_boot2.py
python3 scripts/verify_boot.py
```

### 7. 打 AK3 卡刷包（可选）

```sh
bash tools/make_ak3_zip.sh
```

## 关键补丁点速查

| 文件 | 修改 | 原因 |
|---|---|---|
| `kernel/Makefile` | `config_data` 指向 `stock_defconfig` | 伪装 `/proc/config.gz` |
| `scripts/setlocalversion` | 去掉 `-dirty` 与 `${scm:++}` | 版本串对齐原厂 |
| `include/linux/susfs_def.h` | 追加 `VMA_PAD_START` fallback | MTK 5.10 无 vm_pad |
| `fs/notify/fdinfo.c` | 手工修 hunk | 本树无 `inotify_mark_user_mask()` |
| `drivers/Makefile` / `drivers/Kconfig` | 挂载 `kernelsu` | 接入 KernelSU |

## 构建耗时参考

在 32 核 / 503 GB 主机上：

- 全量编译加 Full LTO 链接：约 20 到 25 分钟
- 其中 LTO 链接（单线程）：约 10 到 15 分钟

`-j32` 只加速编译阶段；`ld.lld -r -o vmlinux.o` 是单进程，增加并行度无益。
