# 踩坑记录

按"现象 / 根因 / 解法"整理，供后续复现时快速对照。

---

## 1. 刷入后第一屏 logo 然后无限重启

**现象**：能看到开机 logo，随后反复重启，无法进系统。

**根因**：boot 镜像的 AVB 结构不对。使用
`avbtool add_hash_footer --algorithm NONE` 生成的是**无签名** vbmeta，
LK 加载失败。

**解法**：保留原厂签名的 vbmeta 块。从原厂 boot 末尾 `AVBf` footer 读取
偏移（**大端**），把原厂 `AVB0` vbmeta 原样搬到新内容末尾，只改 footer 偏移。

**验证**：`avbtool info_image` 应显示 `Algorithm: SHA256_RSA2048`、
`vbmeta_size=1600`，与已知可开机的镜像一致。

---

## 2. 编译成功但所有厂商模块 CRC 不匹配

**现象**：内核编译通过，但 `abi_check` 显示大量 `mismatch`，
`module_layout` 都不一致。

**根因**：`HAS_LTO_CLANG` 依赖 `nm`/`ar` 为 LLVM 版本。主机默认
GNU binutils 导致依赖判定失败，`olddefconfig` 静默把
`LTO_CLANG_FULL`、`CFI_CLANG`、`KASAN_HW_TAGS`、`SHADOW_CALL_STACK`
全部丢弃，配置被降级，符号 CRC 随之全变。

**解法**：确保 `PATH` 中 `clang`、`ld.lld`、`llvm-nm`、`llvm-ar` 等
全部来自同一 LLVM 工具链。

**自检**：构建后检查 `.config` 中上述四项是否保留。

---

## 3. 构建在 `drivers/kernelsu` 处长时间卡住

**现象**：make 停在 `drivers/kernelsu`，十几分钟无进展。

**根因**：SukiSU Makefile 中有
`$(shell ... git fetch --unshallow ...)`。内核仓库是浅克隆时，
该判断成立并触发**联网拉取**，网络不通即长时间阻塞
（另有向 GitHub API 查询版本的 curl 调用）。

**解法**：注释掉 unshallow 那行，并把 `CURL_BIN` 置为 `true`、
清空 `KSU_GITHUB_VER` 与 `GITHUB_COMMITS`。

---

## 4. `fs/notify/fdinfo.c` 补丁失败

**现象**：应用 SuSFS 补丁时该文件报 `Hunk #4 FAILED`。

**根因**：补丁假设存在 `inotify_mark_user_mask()`，而 MTK 树在
`inotify_fdinfo` 中使用内联的 `mask = mark->mask & IN_ALL_EVENTS`。

**解法**：手工把补丁 hunk 中的 `inotify_mark_user_mask(mark)`
替换为 `mask`，并调整 `ignored_mask` 参数。

---

## 5. 编译报 `VMA_PAD_START` 未定义

**现象**：`fs/proc/task_mmu.c:353: implicit declaration of function 'VMA_PAD_START'`

**根因**：该宏来自上游 ACK 的 vma padding 特性，MTK 5.10 树无
`vm_pad` 字段。

**解法**：在新增的 `include/linux/susfs_def.h` 末尾追加兼容定义：

```c
#ifndef VMA_PAD_START
#define VMA_PAD_START(vma) ((vma)->vm_start)
#endif
```

---

## 6. `kernel/oplus_cpu/sched/Kconfig` 找不到

**现象**：`olddefconfig` 报 `can't open file "kernel/oplus_cpu/sched/Kconfig"`

**根因**：OPPO 私有源码不在 OnePlusOSS 内核仓库内。

**解法**：从 modules 仓库合并
`vendor/oplus/kernel/cpu` 到 `kernel/oplus_cpu`。
同理，内核树中大量 `vendor/` 符号链接需要在**兄弟目录**补上
modules 仓库内容。

---

## 7. `/proc/config.gz` 泄露 KSU 配置

**现象**：普通用户 `zcat /proc/config.gz | grep KSU` 命中 13 行。

**根因**：`kernel/config_data.gz` 默认由构建用 `.config` 生成，其中含
`CONFIG_KSU=y`、`CONFIG_KSU_SUSFS=y` 等。

**解法**：把 `kernel/Makefile` 中 `config_data` 的生成源改为原厂
`stock_defconfig`。

---

## 8. `/proc/version` 暴露构建主机与时间

**现象**：显示 `(root@autodl-container-...)` 与编译时间。

**根因**：`scripts/mkcompile_h` 使用 `whoami` / `uname -n` / `date`。

**解法**：通过 `KBUILD_BUILD_USER`、`KBUILD_BUILD_HOST`、
`KBUILD_BUILD_TIMESTAMP`、`KBUILD_BUILD_VERSION` 环境变量覆盖，
**无需改源码**。

**注意**：环境变量变化后 `compile.h` 不会自动重算，需删除
`include/generated/compile.h`、`init/version.o` 与 `.version` 后重编。

---

## 9. Python 生成的 gzip 头与原厂不一致

**现象**：内核 gzip 头为 `1f 8b 08 08 ...`，原厂为 `1f 8b 08 00 ...`。

**根因**：`gzip.compress()` 默认写入 FNAME 标志（`FLG=0x08`）并把 OS 置 255。

**解法**：用 `zlib` 手工拼装头部（`FLG=0`、`XFL=2`、`OS=3`）。

---

## 10. 编译报 `python: not found`

**现象**：`scripts/link-vmlinux.sh: 51: python: not found`

**根因**：部分脚本调用 `python` 而非 `python3`。

**解法**：`ln -sf /usr/bin/python3 /usr/local/bin/python`
