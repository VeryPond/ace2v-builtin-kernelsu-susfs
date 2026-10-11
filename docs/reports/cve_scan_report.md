# MediaTek 固件离线 CVE 扫描报告

**扫描对象**：`E:\GeekFlashTool_Readback_20261010230748790`
**目标 CVE**：CVE-2023-20696、CVE-2025-20730
**扫描日期**：2026-10-10
**扫描方式**：离线固件镜像特征扫描（非在线端口/服务扫描）

---

## 1. 结论摘要

| CVE-ID | CVSS 3.1 | 受影响组件 | 本机是否命中 | 判定 | 依据 |
|---|---|---|---|---|---|
| CVE-2025-20730 | 6.7 (Medium) | preloader | **是** | **存在漏洞（未修补）** | 平台 MT6983 在厂商受影响列表中；两个 preloader 槽均为 2023 年构建，早于 2025-11 的修复 `ALPS10068463` |
| CVE-2023-20696 | 6.7 (Medium) | preloader | 否 | **不在影响范围** | 平台 MT6983 不在该公告的受影响芯片列表中（补丁 `ALPS07856356 / ALPS07874388` 覆盖 MT6880/MT6890 等 24 款，不含 MT6983） |

注意：两条 CVE 的利用前提均为攻击者**已持有 System 权限**，属于本地提权类问题，不是远程可利用漏洞。

---

## 2. 镜像与平台识别

| 项目 | 值 | 来源 |
|---|---|---|
| 平台 | MT6983 (Dimensity 9000) | preloader 源码路径 `bootloader/preloader/platform/mt6983/` |
| preloader 镜像名 | `preloader_k6983v1_64.bin` | `MTK_BLOADER_INFO_v00` 结构体 |
| OEM | OPLUS (`Oplus_cert`) | preloader 安全配置段 `[SEC] Name = Oplus_cert` |
| 机型代码 | `PHP110domestic_PRD_11_A.01_2023` | `proinfo.img` |
| 存储 | UFS，`BOOT_1/BOOT_2` 即 UFS LU0/LU1 引导 LUN | `MT907_Android_scatter.txt` |
| 分区总数 | 87 | scatter |
| Android 安全补丁级别 | system/product/system_ext/boot = `2023-02-05` | `vbmeta_system_a.img`、`vbmeta_a.img` |

### preloader 定位说明

scatter 中 `preloader` 分区声明为 `region: UFS_LU0_LU1`、`partition_size: 0x400000`，`file_name: NONE`（不参与普通下载）。
目录中的 `BOOT_1.img` 与 `BOOT_2.img` 各为 `0x400000` 字节，且镜像内容包含 preloader 特征（`MTK_BLOADER_INFO_v00`、`preloader_k6983v1_64.bin`、`bootloader/preloader/platform/mt6983/...` 源码路径），**确认二者分别是 preloader 的 A/B 槽副本**。

---

## 3. 逐 CVE 分析

### 3.1 CVE-2025-20730 — 命中

- 描述：preloader 中存在不安全默认值，已获得 System 权限的攻击者可进一步本地提权（CWE-287）。
- 厂商公告：MediaTek Product Security Bulletin, November 2025
- 修复：`Patch ID: ALPS10068463`，`Issue ID: MSV-4141`
- 受影响芯片列表包含 **MT6983**。

本机证据：

| 证据 | 值 |
|---|---|
| preloader 构建时间（A 槽） | `20230306-064053`（2023-03-06 06:40:53） |
| preloader 构建时间（B 槽） | `20230223-000010`（2023-02-23 00:00:10） |
| A 槽构建线 | `Build_S_Vendor/151` |
| B 槽构建线 | `Build_S_Vendor/754259` |
| `BOOT_1.img` SHA256 | `970ee90c01a367f0458863e259e4dd5f925e287ca294727775fb8b4d5d3f9685` |
| `BOOT_2.img` SHA256 | `0fbc0b283a59eefbb96c6198e5282d9c12ba0b728e9055fe87bb3ca04366d6b7` |
| 补丁 ID 检索 | 两个 preloader 中均**未发现** `ALPS10068463` |
| 构建时间检索 | 两个 preloader 中均**未发现**任何 2025/2026 年构建时间戳 |

判定：两个已写入设备的 preloader 槽均构建于 2023 年 2–3 月，早于 2025-11 的修复版本约 2.5 年，**判定为未修补，存在该漏洞**。

### 3.2 CVE-2023-20696 — 未命中（芯片不在范围）

- 描述：preloader 中缺少边界检查导致越界写（CWE-787）。
- 厂商公告：MediaTek Product Security Bulletin, May 2023
- 修复：`Patch ID: ALPS07856356 / ALPS07874388`（公告注明仅适用于 MT6880 与 MT6890）
- 受影响芯片列表（24 款）：MT6880, MT6890, MT8167, MT8175, MT8185, MT8195, MT8321, MT8365, MT8385, MT8395, MT8666, MT8667, MT8673, MT8675, MT8765, MT8766, MT8768, MT8781, MT8786, MT8788, MT8789, MT8791, MT8791T, MT8797

判定：**MT6983 不在上述列表中**，本机平台不适用该 CVE。
说明：本机 preloader 构建时间（2023-03）确实早于 2023-05 的公告时间，若仅按时间线判断会误报；实际判定依据是厂商芯片适用范围。

---

## 4. 其他观察（非本次 CVE 结论，但影响风险判断）

1. **preloader 来自多条构建线，固件状态不统一**
   - `gz_a.img` 构建线 `Build_S_Vendor/151`（与 A 槽 preloader 一致）
   - `gz_b.img`、`expdb.img` 断言路径为 `Build_S_Vendor/55720`
   - `BOOT_2.img` 为 `Build_S_Vendor/754259`
   - 说明该机经历过多次刷写/维修，A/B 槽内容不一致。

2. **`expdb.img` 中存在更晚的 preloader 运行记录**
   - `[BLDR] Build Time: 20230306-064053` ×2
   - `[BLDR] Build Time: 20260409-160541` ×7
   - `expdb` 为日志分区，包含 `PL fatal error` / `emergency download mode` 记录，说明至少存在一次 preloader 进入 EDL 的异常启动，且日志中出现 2026-04-09 构建的 preloader。
   - 这不改变结论：当前**实际存储在引导 LUN 中的 preloader 仍是 2023 年版本**。

3. **存在 2026 年的 OTA 痕迹**
   - `oplusreserve2.img` 中 `ro.build.version.security_patch=2026-02-01`
   - `incremental=1770223077924`（≈2026-02），并含 `update_engine` 日志（2026-01/02/05/10）
   - `boot_b.img` 构建时间戳 `1770223077924`（≈2026-02）
   - 即系统分区已更新到 2026 年版本，但 **preloader 未被同步更新**，这与 A/B preloader 停留在 2023 年相互印证。

4. **刷机记录**：`flashinfo.img` 含 `#ACTION_HISTORY_RECORD#`、`Download.Finished`、`Rslt.NoError`、`Aug 10 2023`，即 2023-08-10 有一次成功刷写。

5. **`seccfg.img`** 存在 MTK seccfg 结构（头部 `4D4D4D4D ... 45454545`），说明安全配置分区有效；精确的解锁/锁定状态需按具体 seccfg 版本结构体解析，本次未做结论。

---

## 5. 方法学与局限

- 扫描方式：流式二进制特征匹配（正则），覆盖目录内除 `super.img` 外的全部 86 个文件；`super.img`（15 GB）扫描在读取阶段被中断，未完成。
- 由于这两个 CVE **均只影响 preloader**，而 preloader 已完整扫描，`super.img` 未扫描不影响本报告结论。
- MediaTek 不会在 preloader 二进制中嵌入 `ALPS` 补丁号，因此无法做“补丁号存在性”证明，本判定基于：①厂商受影响芯片清单；②preloader 构建时间与补丁发布时间线对比。
- 未执行任何主动利用（Exploit Status = 未验证）。原因为：对象为离线镜像、无运行中的目标设备，且两条 CVE 均需攻击者已具备 System 权限，静态镜像无法验证利用链。
- 若要进一步确认，需要：取得对应平台的已修补 preloader 二进制做差异比对，或在受控设备上做动态验证。

---

## 6. 处置建议

1. 以 MT6983 平台的最新 preloader（含 `ALPS10068463`）重刷两个引导 LUN，A/B 槽同时更新。
2. 统一固件版本，消除 A 槽（`Build_S_Vendor/151`）与 B 槽（`754259` / `55720`）的构建线混杂。
3. 复核 OTA 流程为何更新了系统分区（2026-02）却未更新 preloader。
4. 保持 efuse 安全启动链路（`sbc_en` / `daa_en` / `sla_en` / `jtag_dis`）开启，以降低 preloader 层提权的实际可利用性。

---

## 7. 附录：MTK 证书校验绕过工具评估（kasnria001/pwnage24mtk）

### 7.1 工具性质

| 项目 | 内容 |
|---|---|
| 地址 | `https://github.com/kasnria001/pwnage24mtk` |
| 性质 | MTK 安全启动**证书校验绕过**工具（非内存破坏利用） |
| 许可 / 语言 | GPL-3.0 / Python |
| 时间 | 2026-06-22 创建，最后推送 2026-07-23 |
| 规模 | 37 star / 15 fork，5 个脚本，约 70 KB |
| 组件 | `parse-part-img.py`（拆分）、`build-part-img.py`（回填）、`sign_mtk_cert.py`（注入伪造哈希）、`parse_mtk_certs.py`（DER 解析）、`verify_mtk_image.py`（本地复现校验） |
| 自述 | "Cert exploit for MTK devices. There is a logic flaw in MTK cert verification process." |
| 代码质量 | 作者自述为 "vibe-coded"，存在已知的架构识别缺陷，计划重写 |

### 7.2 技术原理

MTK 引导链中 preloader 校验 bl2_ext / lk / atf 后才跳转；这些镜像由 MKIMG 容器（`part_hdr_t`，magic `0x58881688`）+ CERT1/CERT2 ASN.1 证书签名。

缺陷不在于密码学，而在于**在 CERT2 中定位镜像哈希字段的解析逻辑**：

- `bypass_mode=0`（新 V6）：解析过程跳过非 SEQUENCE(`0x30`) 对象。于是把 `0xA0`（context `[0]`）构造块作为**同级**插入，内含 `OID 2.16.886.2454.2.4`（镜像头哈希）+ `OID 2.16.886.2454.2.1`（镜像哈希），校验器取"首个匹配"即读到攻击者提供的值。
- `bypass_mode=1`（旧 V5 / 老 V6）：任何对象都会被进入，用 `BIT STRING(原始 CERT2 DER)` 包一层即可。

关键点：注入块位于原签名 SEQUENCE **之外**，不参与 RSA-PSS 验签，因此**无需私钥**即可让被篡改的镜像通过哈希校验。

### 7.3 与 CVE-2023-20696 / CVE-2025-20730 的关系（结论：关联需打折）

这是工具作者的自述归类，**未获厂商确认**，且技术定性并不一致：

| 项目 | 厂商官方定性 | 该工具实际利用的缺陷 | 是否同类 |
|---|---|---|---|
| CVE-2023-20696 | preloader 越界写（CWE-787，缺边界检查） | ASN.1/DER 解析逻辑缺陷 | 否，内存破坏 vs 解析逻辑 |
| CVE-2025-20730 | preloader 不安全默认值（CWE-287） | 同上，涉及 `bypass_mode` 分支行为 | 存疑，措辞吻合但无公开证据 |

结论：把该工具直接引用为这两个 CVE 的 PoC 不严谨；它更接近一个独立（或变种）的证书校验逻辑缺陷。

### 7.4 对本固件的适用性（实测证据）

工具的目标格式与本目录镜像**高度吻合**，已实测确认：

1. **镜像结构匹配**（本目录实测，MKIMG magic + `ext_magic=0x58891689` 全部命中）：
   - `lk_a.img`：`lk`(1030976) + `bl2_ext`(811920) + `aee`(1101168) + `lk_main_dtb`(321590)，每个子镜像后各跟一组 `cert1` + `cert2`；文件尾部另有一组孤立 cert 对。
   - `tee_a.img`：`atf`(301928) + `tee`(562176)。
   - `gz_a.img`：`gz`(1889776) + `mkp_service` + `unmap2`。
   - `scp_a.img`：`tinysys-scp-RV55_A` 等。
   - README 点名的 `lk` / `bl2_ext` / `lk_main_dtb` / `aee` 四者**全部命中**。

2. **证书格式匹配**（`parse_mtk_certs.py` 实测）：
   - CERT1 含 `2.16.886.2454.3.1`(签名算法)、`2.16.886.2454.1.2`(镜像公钥)、`2.16.886.2454.1.1`(根公钥)、`2.16.886.2454.2.2/2.5/2.3/2.9/2.10`。
   - CERT2 含工具直接操作的两个关键 OID：`2.16.886.2454.2.1`（镜像哈希）、`2.16.886.2454.2.4`（镜像头哈希）。
   - 签名方案 RSA-2048 + RSA-PSS(OID `1.2.840.113549.1.1.10`) + MGF1-SHA256 + salt 32 + SHA-256。
   - `sec_level = 0`（对应 SHA-256）。

3. **校验模型匹配**：对 `lk_a.img` 运行工具的 `verify_mtk_image.py --all`，子镜像 `lk` 返回：
   ```
   CERT1 signature: OK
   CERT2 public key matches CERT1 image key: OK
   CERT2 signature: OK
   Image header hash: OK
   Image data hash: OK
   Result: VALID
   ```
   说明该工具对这套镜像的签名模型还原是准确的，当前镜像签名链完整有效。

4. **preloader 侧 OID 一致**：`BOOT_1.img` 中同时存在 `2.16.886.2454.2.1`、`2.16.886.2454.2.4` 及 `AND_SECCTRL_v` / `AND_SECRO_v` 旧式安全控制结构。

### 7.5 利用前置条件

- 需要一条**带外写入通道**把篡改后的镜像写回设备（EDL/BROM + DA，或已解锁的刷写路径），即需要物理接触与刷写能力。
- 需要该设备 preloader 的证书校验实际走 `bypass_mode=0` 或 `bypass_mode=1` 分支——本报告未对 preloader 的 ARM64 代码做反汇编确认，**该点属于未验证项**，也是判定"能否真正跑通"的唯一剩余不确定性。

### 7.6 影响评估

若成立，其影响**高于**本报告正文的 CVE：

- 绕过可信启动后，被篡改的 bootloader 仍被接受，可直接移除 BL2_EXT 对 lk/atf/gz 的校验、移除 LK 的 `lk_main_dtb` 校验、移除 `set_lock_state` 等引导锁。
- 结果等价于**永久的 EL3 级控制权 / bootloader 解锁**，且不依赖"已获得 System 权限"这一前提——比正文两条 CVE 更前置、更彻底。

### 7.7 风险与结论

风险：

1. 改引导链极易**变砖**；本机 A/B 槽构建线本就不一致（`151` / `754259` / `55720`），风险进一步放大。
2. 可能触发 efuse **反回滚 / 安全计数**，一次性且不可逆；本机 `sbc_en` / `daa_en` / `sla_en` 全开。
3. 解锁后 verified boot 完全失效，恶意固件可持久驻留于最高权限层。
4. 绕过设备安全引导在多数场景属于法律 / 保修 / 服务条款灰区。
5. 工具本身质量未成熟，且脚本会直接改写引导分区，误操作不可逆。

结论：

- **格式层面：完全适用**（镜像结构、证书 OID、签名方案、校验模型四项均已实测吻合）。
- **漏洞类别：证书解析逻辑缺陷，不是 CVE-2023-20696 的越界写**，与其宣称的 CVE 关联应打折扣。
- **实际可利用性：未验证**，取决于 preloader 的 `bypass_mode` 分支行为。
- **严重性：高**（若成立 → 可信启动绕过 / 永久 EL3 控制）。

本报告仅完成静态评估，未执行任何绕过、签名伪造或刷写操作。
