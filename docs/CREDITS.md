# 漏洞、上游项目与致谢

本项目的成果建立在一批公开漏洞信息与开源项目之上。这里把
**用到的 CVE**、**依赖的仓库**、**各项目的作者**完整列出。

---

## 1. 涉及的漏洞

### 1.1 本项目分析并验证的缺陷

| 标识 | 说明 | 本项目角色 |
|---|---|---|
| MTK 证书校验 ASN.1 解析逻辑缺陷 | 引导链 CERT1/CERT2 校验可被 ASN.1 遍历绕过，无需私钥 | **独立分析与真机验证**（见 `LK_EXPLOIT.md` / `LK_EXPLOIT_VERIFY.md`） |

该缺陷与下述两条 CVE **形态相似但并非同一漏洞**，详见 `CVE_COMPARISON.md`。

### 1.2 作为背景与线索的 CVE

| CVE | CVSS 3.1 | 组件 | 本机状态 | 来源 |
|---|---|---|---|---|
| **CVE-2023-20696** | 6.7 | preloader | 不在影响范围（MT6983 不在公告受影响列表） | MTK 安全公告；`pwnage24mtk` 工具自述关联 |
| **CVE-2025-20730** | 6.7 | preloader | **存在，未修补** | 厂商公告 `ALPS10068463`（2025-11 修复） |

两条 CVE 的利用前提均为**已持有 System 权限**，属本地提权类；
本项目分析的缺陷前置条件更低（物理接触 + 可写分区）。

---

## 2. 上游工具与项目

### 2.1 引导链漏洞分析工具（核心）

| 项目 | 作者 | 地址 | 本项目用法 |
|---|---|---|---|
| **pwnage24mtk** | **kasnria001** | https://github.com/kasnria001/pwnage24mtk | 证书拆分 / 注入 / 校验复现；本项目据此完成真机验证 |

该工具自述为一处 MTK 证书校验逻辑缺陷的验证工具，关联
CVE-2023-20696 与 CVE-2025-20730。本项目收录于 `tools/pwnage24mtk/`，
并记录了其已知限制（见该目录 README）。

### 2.2 内核源码

| 项目 | 作者 / 组织 | 地址 | 本项目用法 |
|---|---|---|---|
| **android_kernel_5.10_oneplus_mt6983** | **OnePlusOSS**（一加开源） | https://github.com/OnePlusOSS/android_kernel_5.10_oneplus_mt6983 | 内核主体源码（分支 `oneplus/mt6983_t_13.0_oneplus_ace_2v`，HEAD `ff51a39`） |
| **android_kernel_modules_oneplus_mt6983** | **OnePlusOSS** | https://github.com/OnePlusOSS/android_kernel_modules_oneplus_mt6983 | OPPO 私有内核模块（`vendor/`、`oplus_cpu`），分支同上，HEAD `a362bee` |

### 2.3 Root 与隐藏

| 项目 | 作者 / 组织 | 地址 | 本项目用法 |
|---|---|---|---|
| **SukiSU-Ultra** | **SukiSU-Ultra 团队** | https://github.com/SukiSU-Ultra/SukiSU-Ultra | 使用 `builtin` 分支（HEAD `6c284e9`），内建 KernelSU |
| **susfs4ksu** | **ShirkNeko**（维护镜像） | https://github.com/ShirkNeko/susfs4ksu | SuSFS v2.3.0 内核补丁，分支 `gki-android12-5.10`（HEAD `9892175`） |

> 说明：SuSFS 原始作者为 **simonpunk**（原仓库 `simonpunk/susfs4ksu`
> 已不可访问）。当前活跃维护源为 ShirkNeko 的镜像仓库。

### 2.4 打包工具

| 项目 | 作者 | 地址 | 本项目用法 |
|---|---|---|---|
| **AnyKernel3** | **osm0sis** | https://github.com/osm0sis/AnyKernel3 | AK3 卡刷包骨架（`AK_BASE_VERSION=20260904`），含 `magiskboot` |
| **Magisk**（magiskboot 部分） | **topjohnwu** | https://github.com/topjohnwu/Magisk | `magiskboot` 用于 boot 镜像拆解与重打包 |

### 2.5 编译工具链

| 项目 | 来源 | 版本 |
|---|---|---|
| **Android (AOSP) Clang** | Google / AOSP prebuilts | `clang-r416183b`（12.0.5），与设备原厂一致 |

### 2.6 分析库

| 库 | 用途 |
|---|---|
| **Capstone** | ARM64 反汇编（preloader / LK 分析，注意 `skipdata` 陷阱） |
| **pyelftools** | 解析模块 `__versions` 段，做 ABI/CRC 校验 |
| **lz4** | boot ramdisk 解压 |

---

## 3. 参考的公开资料

| 资料 | 用途 |
|---|---|
| MTK 安全公告（`ALPS10068463` / `ALPS07856356` / `ALPS07874388`） | 判定 CVE-2025-20730 / CVE-2023-20696 的修复状态 |
| Android AVB（`avbtool`）文档 | 理解 vbmeta / footer 结构与签名算法 |
| SuSFS 官方集成文档 | `/proc/config.gz` 伪装的做法（改用原厂 defconfig） |
| KernelSU 官方构建文档 | `builtin` 分支的接入方式与手动 hook 说明 |

---

## 4. 特别说明

- `pwnage24mtk` 为上游作者 **kasnria001** 的成果；本项目对其的使用是
  **复现与真机验证**，未修改其核心逻辑（收录于 `tools/pwnage24mtk/`，
  附带其原始 LICENSE）。
- SuSFS 与 KernelSU 的版权与许可遵循各自上游（GPL-2.0 等）。
- 内核源码补丁的原始版权归属 MediaTek / OnePlusOSS 及各上游项目。
- 本项目新增的文档、脚本与验证结论，许可见仓库根目录 `LICENSE`。
