# kasnria001/pwnage24mtk 本地固件探测报告

**探测对象**：`E:\GeekFlashTool_Readback_20261010230748790`（MT6983 / OPLUS，OPPO PHP110 类机型 readback）
**工具**：https://github.com/kasnria001/pwnage24mtk （克隆于 `E:\_tools\pwnage24mtk`）
**探测日期**：2026-10-10
**探测方式**：离线固件镜像分析（无在线端口扫描、无设备写入、无刷机动作）
**工具性质**：MTK 引导链证书校验逻辑缺陷验证工具（工具自述关联 CVE-2023-20696 / CVE-2025-20730），非内存破坏利用

---

## 1. 结论摘要

| 探测项 | 结果 |
|---|---|
| 镜像是否属于该工具的目标格式（MKIMG `part_hdr_t` + CERT1/CERT2） | **是**，37 个镜像含 MKIMG 容器 |
| 是否存在可被工具解析的签名子镜像 | **是**，69 个 CERT1/CERT2 签名的子镜像 |
| 现有签名链是否完整有效 | **全部有效**（67/69 用工具默认规则；`md1rom` ×2 属工具硬编码限制，放宽后同样有效） |
| 工具声明的缺陷在本固件上是否可复现（工具校验器模型内） | **可复现**：篡改镜像 → 校验 INVALID；注入伪造哈希块后 → 校验 VALID，且 CERT2 签名仍 OK |
| preloader 是否包含同套证书解析结构 | **是**：两槽 preloader 均含完整 OID 表与证书校验日志串 |
| 设备 preloader 实际走 `bypass_mode=0` 还是 `1` | **未验证**（本次未完成 libsec ASN.1 遍历分支的反汇编判定） |

一句话：**固件结构完全落在该工具的目标范围内，签名链当前是干净的，工具描述的“无需私钥即可让改后镜像通过哈希校验”这一逻辑缺陷可在工具校验器模型内完整复现；但“真机是否接受篡改镜像”仍取决于 preloader 内 libsec 的解析分支，本次未证实。**

---

## 2. 探测方法

```powershell
# 1) 结构普查：哪些镜像含 MKIMG 容器
# 2) 逐子镜像复现签名/哈希校验
python E:\_tools\pwnage24mtk\verify_mtk_image.py <partition>.img --all

# 3) 拆分单个签名子镜像
python E:\_tools\pwnage24mtk\parse-part-img.py lk_a.img --split -o lk_a_split

# 4) 篡改后重新校验 / 注入伪造哈希后再次校验
python E:\_tools\pwnage24mtk\sign_mtk_cert.py <single>.bin -w -o <single>.signed
python E:\_tools\pwnage24mtk\sign_mtk_cert.py <single>.bin -w --legacy -o <single>.legacy

# 5) ASN.1 结构对照
python E:\_tools\pwnage24mtk\parse_mtk_certs.py <single>.signed
```

所有产物写在独立目录 `E:\_probe_pwnage24mtk`，未改动原始 readback。

---

## 3. 结果 A：镜像结构适配性

全目录除 `super.img`（15 GB，未扫描）外共 86 个镜像，其中 **37 个含 MKIMG magic（`0x58881688`，且 `ext_magic=0x58891689` 全部命中）**：

`apusys, audio_dsp, ccu, dpm, dtbo, gpueb, gz, lk, logo, mcupm, md1img, mvpu_algo, pi_img, scp, splash_odm, spmfw, sspm, tee, vcp`（A/B 槽）。

工具 README 点名的 `lk / bl2_ext / lk_main_dtb / aee` 四个 preloader 校验目标全部存在于 `lk_a/lk_b`：

| 子镜像 | lk_a 偏移 | lk_a 大小 | lk_b 偏移 | lk_b 大小 |
|---|---|---|---|---|
| lk | 0x0 | 1030976 | 0x0 | 1107048 |
| bl2_ext | 0xfcc10 | 811920 | 0x10f540 | 844136 |
| aee | 0x1c4070 | 1101168 | 0x1de780 | 1127432 |
| lk_main_dtb | 0x2d1eb0 | 321590 | 0x2f2c60 | 321614 |

每个子镜像后各跟一对 `cert1`(1733 B) + `cert2`(1011 B)，`sec_level=0`（SHA-256），签名方案 RSA-2048 + RSA-PSS(MGF1-SHA256, salt 32)。

---

## 4. 结果 B：签名链批量校验

对 69 个 CERT1/CERT2 签名子镜像逐一复现：CERT1 签名、CERT2 签名、CERT2 公钥与 CERT1 镜像公钥一致性、镜像头哈希、镜像数据哈希。

**全部 5 项通过**，A/B 两槽镜像内容虽不同，但各自签名链自洽。

| 镜像 | 子镜像数 | 结果 |
|---|---|---|
| lk_a / lk_b | 4 / 4 | lk, bl2_ext, aee, lk_main_dtb 全部 VALID |
| tee_a / tee_b | 2 / 2 | atf, tee VALID |
| gz_a / gz_b | 3 / 3 | gz, mkp_service, unmap2 VALID |
| scp_a / scp_b | 2 / 2 | tinysys-scp-RV55_A, _dram VALID |
| vcp_a / vcp_b | 2 / 2 | tinysys-vcp-RV55_A, _dram VALID |
| audio_dsp A/B | 6 / 6 | hifi3_{a,b}_{dram,iram,sram} VALID |
| md1img A/B | 3 / 3 | md1drdi, md1dsp VALID；md1rom 需放宽工具硬编码 |
| 其余（apusys/ccu/dpm/gpueb/logo/mcupm/mvpu_algo/pi_img/splash_odm/spmfw/sspm） | 各 1–3 | 全部 VALID |

### 已知工具缺陷（非固件问题）

`md1img_a/b` 的 `md1rom` 子镜像 CERT1 `img_type=0x02000001`（MD 变体，名称 `cert1md`），而 `verify_mtk_image.py` 硬编码只接受 `IMG_TYPE_CERT1=0x02000000`，因此直接报
`error: CERT1 img_type is 0x02000001, expected 0x02000000`。
把该常量放宽为镜像实际值后，`md1rom` 的 CERT1 签名、CERT2 签名、头哈希、数据哈希**全部 OK**。这属于工具适配性缺陷，不是固件被改动。

---

## 5. 结果 C：证书校验逻辑缺陷的可复现性（工具模型内）

在 `lk_a.img` 上做了受控对照实验（全部在副本上进行）：

1. 拆分得 `lk.bin`，基线校验：`Result: VALID`。
2. 在 `lk.bin` 数据区偏移 `0x1002` 翻转 1 字节 → `lk_tampered.bin`。
3. 校验 `lk_tampered.bin`：

```
CERT1 signature: OK
CERT2 signature: OK
Image header hash: OK
Image data hash: FAIL
  cert : ff119517d1dc5d8dfc4bf4ccaa4d57f5ac7330a78e0214855b2524eb43a7a961
  calc : 50f632cfe839d068088d78bdcb5c37a7ea6f2e4c62161c7629db7dc6bd6bf2ee
Result: INVALID
```

   说明：CERT1/CERT2 签名本身只覆盖证书 TBS，镜像被改后签名仍“有效”，完整性完全依赖 CERT2 中的镜像头哈希/镜像哈希。

4. 用 `sign_mtk_cert.py -w` 在 CERT2 前注入伪造块
   `A0{ OID(2.16.886.2454.2.4)+BITSTRING(新头哈希), OID(2.16.886.2454.2.1)+BITSTRING(新镜像哈希) }`
   → `lk_tampered_signed.bin`（CERT2 dsize 1011→1101）。
5. 再校验 `lk_tampered_signed.bin`：

```
CERT1 signature: OK
CERT2 signature: OK
Image header hash: OK
Image data hash: OK    ← cert/calc 都是被篡改后的新哈希 50f632cf…
Result: VALID
```

   `parse_mtk_certs.py` 显示注入块位于 CERT2 根 SEQUENCE **之外**，因此在先出现的伪造 OID 被取用后，原签名 SEQUENCE 内的真实哈希被忽略——篡改后的镜像在工具校验器模型内被判为合法，且**全程未使用任何私钥**。

6. `--legacy` 形态（`BITSTRING(原 DER)` 包裹 + 注入块）同样产出并校验通过，用于覆盖 `bypass_mode=1` 的老解析路径。

> 重要限定：第 5 步的 `VALID` 出自工具自带的校验器，它实现的是**工具作者对设备解析逻辑的建模**。它证明“该缺陷形态在本固件的数据结构上成立、payload 可构造、模型内自洽”，但**不等于真机 preloader 会接受**。

---

## 6. 结果 D：preloader 侧证据

`BOOT_1.img` / `BOOT_2.img` 为两个引导槽（A: 20230306-064053，B: 20230223-000010），均未压缩、含 ARM64 代码与 libsec 字符串。

### 6.1 OID 字符串表（两槽一致）

位于文件偏移约 `0x8aadb`，64 字节步长，含工具直接操作的整套 OID：

```
1.2.840.113549.1.1.10        (RSASSA-PSS 签名算法)
1.2.840.113549.1.1.1         (rsaEncryption)
2.16.886.2454.1.1 / .1.2 / .1.3
2.16.886.2454.2.1            (Image Hash        ← 工具注入目标)
2.16.886.2454.2.2            (Image Version)
2.16.886.2454.2.3            (SW ID)
2.16.886.2454.3.1 / .3.2
2.16.886.2454.2.4            (Image Header Hash ← 工具注入目标)
2.16.886.2454.2.5 / .2.9 / .2.10
```

### 6.2 证书校验日志串（两槽一致，约 0x8a9e0–0x8ab1b）

```
[%s] pubk not initialized
[%s] Verification Pass / Verification Fail(0x%x)
[%s] cert img_hdr_type = 0x%x
[%s] cert verify, part = %s, img = %s...
[%s] img auth ok / img auth fail(0x%x)
[%s] dump (imghdr + image) hash...
[%s] sec_level = %u   /   [%s] sbc_en = %d
```

证实该 preloader 内确实实现了与工具同构的 CERT1/CERT2 + RSA-PSS + 镜像头/镜像哈希校验路径，且源码来自
`vendor/mediatek/proprietary/bootable/bootloader/preloader/platform/mt6983/src/secure_lib/common/src/core/sec_export.c`。

### 6.3 未完成项

尝试用 Capstone 线性反汇编定位 OID 表的引用点并按标签遍历条件判定 `bypass_mode`，结果：OID/日志串在 `.rodata` 中经描述符/指针表间接访问，4 MB 范围内未找到 `ADRP+ADD` 直接引用形态（已修正一次 ADRP 立即数理解错误后重跑）。
因此 **“真机解析分支是 0 还是 1” 未通过静态反汇编证实**，需要继续做针对性的函数级反汇编，或在受控设备上做动态验证。

---

## 7. 结论与建议

1. **结构层面完全命中**：本固件的引导链镜像就是该工具设计的 MKIMG + CERT1/CERT2 形态，69 个签名子镜像可被完整解析与校验。
2. **当前固件是干净的**：所有签名子镜像的签名与哈希均自洽，未发现被篡改痕迹。
3. **逻辑缺陷形态可复现**：在工具校验器模型内，改后镜像可被伪造哈希块“洗白”为 VALID，且不需要私钥。工具 README 自述“Patched”，未在本地镜像中发现对应修复标记。
4. **唯一未证实的环节**：preloader 内 libsec 的 ASN.1 遍历实际走 `bypass_mode=0` 还是 `1`。这是判定“能否真正跑通”的关键，也是本次探测未闭环的部分。
5. **若要闭环**：对 `BOOT_1.img`/`BOOT_2.img` 的 libsec 解析函数做函数级反汇编（可先定位 `sec_export.c` 相关函数的 TAG 0x30/0x06/0x03 比较与递归条件），或在受控设备上动态验证；本机为离线镜像，无运行设备，无法做动态验证。
6. **风险提示**：该缺陷（若真机成立）影响面高于既有 preloader CVE 报告，等价于绕过可信启动；且本固件 preloader 停留在 2023-02/03 版本，未随系统分区（已到 2026-02）同步更新。建议保持 efuse 安全启动链路（`sbc_en`/`daa_en`/`sla_en`/`jtag_dis`）开启，并向上游确认 MT6983 preloader 是否已修该解析缺陷。

---

## 8. 附录：探测产物与哈希

目录 `E:\_probe_pwnage24mtk`：

| 文件 | SHA256 |
|---|---|
| `lk_a_split\lk.bin`（基线子镜像） | `0b9f22ffba1d7a1caf834fc5da244c3f218514b0431eedd84c64f20af70b475c` |
| `lk_tampered.bin`（翻转 1 字节） | `ac12301b3c3c83f08b218f043ccb55adcbac4b66fe80d12b4a1628ff19a17f47` |
| `lk_tampered_signed.bin`（注入 payload） | `71a951a7e7fe878e2242b798df782347359c6c0e51b502a98f85380b1d3e186e` |
| `lk_tampered_signed_legacy.bin`（legacy 分支） | `530b559715651ce36fd13130feec0749abfe5bfbec345c84dfd3b633ceec5fab` |

原始镜像（未改动）：

| 文件 | SHA256 |
|---|---|
| `lk_a.img` | `1558f6574c08181cf95a8b219ccfbf47d2eca56f6082bc2db5dca3f9bc9d76d1` |
| `BOOT_1.img` | `970ee90c01a367f0458863e259e4dd5f925e287ca294727775fb8b4d5d3f9685` |
| `BOOT_2.img` | `0fbc0b283a59eefbb96c6198e5282d9c12ba0b728e9055fe87bb3ca04366d6b7` |

> `lk_tampered_signed*.bin` 是单子镜像中间产物，**不是可直接刷写的分区镜像**，本次也未执行任何 `build-part-img.py replace` 回填或设备写入。

---

## 9. 追加：preloader 证书解析器反汇编结果（2026-10-11）

对象：`BOOT_1.img`（MT6983，ARM64，载入基址约 `0x11e56000`）。方法：Capstone 线性反汇编 + 指针/描述符表交叉引用（注意：`Cs.disasm` 默认遇无法解码字节即停止，须启用 `skipdata`，否则整轮扫描会静默返回 0 条）。

### 9.1 已定位的证书解析入口

函数入口 `0x0696b8`，是 MKIMG 证书容器解析：

| 地址 | 行为 |
|---|---|
| `0x069720` | 校验 `[x22] == 0x58881688`（MKIMG magic） |
| `0x06972c` | 校验 `[x22+0x30] == 0x58891689`（ext_magic） |
| `0x069740` | 读 `[x22+0x3c]`（`img_type`），测试 `(img_type \| 1) == 0x02000001` → 接受 CERT1 `0x02000000` 与变体 `0x02000001` |
| `0x069760` | 用 `hdr_sz`(偏移 0x34) 定位证书数据，指针存 `0xf0af0`、大小存 `0xf0af8` |
| `0x069790` | `bl 0x69c98` 解析证书属性，结果写入 `[ctx+0x408]` |
| `0x0697d4` | `ldr w8, [ctx+0x408]` |
| `0x0697dc` | `str w8, [0xf09f4]`（原始值） |
| `0x0697e8` | `and w9, w8, #0x700` → `0xf09fc` |
| `0x0697f0` | `and w2, w8, #0xf` |
| `0x069804` | `str w2, [0xf09f4]` → **最终 mode = `[ctx+0x408] & 0xF`** |
| `0x06980c` | `cmp w8, #2; b.hi` → **mode 必须 ≤ 2，否则报错退出** |

注：`0x696b8` 在静态分析中**找不到直接 BL 调用者**，说明该校验函数是通过 `.rodata` 里的函数指针表间接调度的——这也是为什么所有字符串/OID 表都表现为“数据指针表间接引用”。

### 9.2 mode 直接决定 ASN.1 遍历标签

分派函数 `0x06c01c`（参数 `w3` = mode 派生的镜像组 ID）：

| mode | `w3` (组 ID) | 期望 ASN.1 标签 |
|---|---|---|
| 0 | `0x100` | **`0x20`** |
| 1 | `0x180` | **`0x30`** |
| 2 | `0x200` | **`0x30`** |

标签接受判据在 `0x068d24`：`orr w8, w4, #0x10; cmp w8, #0x30` → 即 `tag ∈ {0x20, 0x30}` 通过，其余（含普通 `0x03` BIT STRING）不通过。

结论：**只有 mode 0 走“宽松”分支（`0x20`，构造类对象通用），mode 1/2 都要求 `0x30`（严格 SEQUENCE）。** 该 mode 不是编译期常量，而是从镜像自身的 CERT1 解析结果中读出，因此**同一固件不同分区可能取值不同**。

### 9.3 仍未闭合并需要什么

| 未知项 | 说明 |
|---|---|
| 本机固件实际 mode | `mode = [ctx+0x408] & 0xF`，`ctx` 由 `0x69c98 → 0x6a4d4/0x6a828/0x6a884` 依据 CERT1 内容填充；需再定位该字段来源，或在真机上观测 |
| mode 与工具 payload 形态的对应 | 工具提供 new-V6（裸 `0xA0` 同级块）与 legacy（`BITSTRING` 包裹 + `0xA0`）两种；与固件 mode 0/1/2 的映射尚未做交叉验证 |
| 真机行为 | 无写入即无法验证；本报告未做任何 flash 写入 |

---

## 10. 真机动态验证（2026-10-11，用户自行刷写）

### 10.1 实验设计

目标：在不依赖任何私钥的前提下，让被篡改的引导子镜像通过校验。

构造方式：对 `lk_a.img` 中某个子镜像做**仅 1 字节**的改动（`part_hdr_t` 的保留区，全部为 `0xFF`，不属于任何字段），并在此基础上向其 CERT2 注入伪造哈希块。选择保留区是为了让改动在功能上完全惰性——镜像能否启动，只取决于**校验是否被绕过**。

注入形态（工具提供两种）：
- **new（V6）**：在 CERT2 前追加同级 `A0{ OID(2.4)+BITSTRING(hdr_hash), OID(2.1)+BITSTRING(img_hash) }`
- **legacy（V5/旧 V6）**：追加 `BITSTRING(原始 CERT2 DER)` 后再追加上述 `A0` 块

### 10.2 结果

| 镜像 | 改动目标 | 子镜像偏移 | 注入形态 | 结果 |
|---|---|---|---|---|
| `lk_a_probe_new.img` | `lk` | 后移 80 字节 | new | **卡静态 logo，无动画** |
| `lk_a_probe_data.img` | `lk` | 后移 80 字节 | new | 未测 |
| `lk_a_probe_legacy.img` | `lk` | 后移 1104 字节 | legacy | 未测 |
| `lk_a_probe_dtb.img` | `lk_main_dtb` | **完全不变** | new | 未测 |
| `lk_a_probe_dtb_legacy.img` | `lk_main_dtb` | **完全不变** | legacy | **正常进入系统** |

`lk_a_probe_dtb_legacy.img` 中 `lk` 未做任何改动，`bl2_ext` / `aee` / `lk_main_dtb` 的偏移与原始镜像完全一致，改动仅限 `lk_main_dtb` 的保留字节与其 CERT2 注入块。

### 10.3 当前判定与待补对照

**已达成的结论**：

- 该固件的引导链证书校验存在可被绕过的解析逻辑缺陷，**legacy 形态的注入块可被接受**，被篡改的子镜像得以通过校验并正常启动。
- 与本报告第 9 节的反汇编结果一致：该 preloader 的 ASN.1 遍历存在按对象类型选择递归的宽松分支。

**配对对照（已完成）**：

| 镜像 | 目标 | 布局 | 注入形态 | 实际结果 |
|---|---|---|---|---|
| `lk_a_probe_dtb.img` | `lk_main_dtb` | 无位移 | new | **不开机** |
| `lk_a_probe_dtb_legacy.img` | `lk_main_dtb` | 无位移 | legacy | **正常进入系统** |

两镜像对同一目标做了完全相同的单字节改动、子镜像偏移完全一致，唯一差异是注入块的 ASN.1 排布形态。一失败一成功，构成有效差分：

- 若该校验未被执行 → 两者都应正常启动（实测 new 不开机）；
- 若校验拒绝攻击者提供的哈希 → 两者都应失败（实测 legacy 正常启动）；
- 因此 **legacy 形态注入的哈希被解析器采用，替代了证书中的真实哈希值，校验被绕过**。

**目标有效性对照（`aee`）**：

先用 `aee` 做 data 区对照，结果 `lk_a_probe_aee_new.img` **正常开机**（new 形态）。
原因：`aee` 属于异常处理器，**不在引导链的校验集合内**（preloader 校验 `bl2_ext`；BL2_EXT 校验 `lk`/`atf`/`gz`；LK 校验 `lk_main_dtb`）。因此改 `aee` 任何形态都能启动，该次对照为**假阳性**，不构成绕过证据。

该次实验仍产出两条有效信息：
1. `aee` 对照组（未校验镜像）能启动，而同样 new 形态的 `lk_main_dtb`（已校验镜像）不亮屏 → 反证 `lk_main_dtb` 确实在校验集合内；
2. 该镜像把 `lk_main_dtb` 后移了 1104 字节仍能正常启动 → **子镜像位移本身无害**，LK 通过遍历 part header 链表定位镜像。

**残余不确定性（低概率）与封口实验**：

前文的改动落在 `part_hdr_t` 保留区，影响"镜像头哈希"（`2.16.886.2454.2.4`）。理论上仍有替代解释：该平台不校验头哈希，而 new 形态的 `A0` 前缀导致 CERT2 解析失败。

封口方案：对 `lk_main_dtb` 的 **DTB 头字段 `last_comp_version`**（偏移 DTB+0x18，值 16→15）做单字节改动——该字节位于 **data 区**（对应必然被校验的 `2.16.886.2454.2.1`），且不影响 DTB 解析。两镜像：

| 镜像 | 目标 | 布局 | 改动区 | 注入形态 |
|---|---|---|---|---|
| `lk_a_probe_dtbdata_new.img` | `lk_main_dtb` | 无位移 | **data** | new |
| `lk_a_probe_dtbdata_legacy.img` | `lk_main_dtb` | 无位移 | **data** | legacy |

预期：new 不亮屏、legacy 正常开机 → 即证明 **data 哈希确实在执行校验，且被 legacy 注入顶替**，不留残余疑点。

---

## 11. 最终结论：差分实验闭合（2026-10-11）

### 11.1 关键差分（决定性的两组）

改动统一选在 `lk_main_dtb` 内 DTB 的 **memreserve 终止符与 struct 区块之间那 8 个零字节**（DTB+0x30）——DTB 解析器读到 `(0,0)` 即停止，该区域永不参与解析，属**保证惰性**的改动；同时它位于容器 **data 区**，对应必然被校验的 `2.16.886.2454.2.1`。四个子镜像**零位移**，目标是已校验的 `lk_main_dtb`。

| 镜像 | 改动字节 | 注入形态 | 实测结果 |
|---|---|---|---|
| `lk_a_probe_dtbinert_plain.img` | DTB+0x30 | **无** | **不亮机** |
| `lk_a_probe_dtbinert_legacy.img` | DTB+0x30 | legacy | **点亮进系统** |

两者的目标、改动字节、子镜像布局完全一致，唯一差异是是否附加注入块。：

- 若该校验未被执行 → 两者都应正常启动（实测无注入者不亮）；
- 若校验拒绝攻击者提供的哈希 → 两者都应失败（实测 legacy 注入者正常启动）；
- ⇒ **解析器采用了注入块中攻击者提供的哈希值，替代了证书内的真实值，校验被绕过，且全程未使用任何私钥。**

### 11.2 全部实验结果汇总

| 目标 | 改动区 | 是否已校验 | 注入 | 结果 | 说明 |
|---|---|---|---|---|---|
| `aee` | data | **否** | new | 开机 | 假阳性：不在校验集合内，任何改动都能启动 |
| `lk_main_dtb` | header 保留区 | 是 | new | 不亮屏 | new 形态注入未被采纳 |
| `lk_main_dtb` | header 保留区 | 是 | legacy | 开机 | （当时判据不充分，后经 data 区差分确认） |
| `lk_main_dtb` | DTB `last_comp_version` | 是 | new | 不亮屏 | 该字段被 LK/libfdt 使用，属功能性改动 |
| `lk_main_dtb` | DTB `last_comp_version` | 是 | legacy | 不亮屏 | 同上：哈希已过但 DTB 被判不兼容 |
| `lk_main_dtb` | DTB+0x30（惰性） | 是 | **无** | **不亮机** | **对照组：证明该校验确实在执行** |
| `lk_main_dtb` | DTB+0x30（惰性） | 是 | **legacy** | **开机** | **证明注入哈希被采纳，校验被绕过** |

过程中曾出现两次判据不足的结论（把保留区改动误判为绕过成功），最终由 11.1 的惰性 data 字节差分修正。`aee` 与 `last_comp_version` 两次误判分别源于"目标未被校验"与"改动具有功能影响"。

### 11.3 结论

1. **漏洞成立**：本固件（MT6983 / PHP110，preloader 构建 2023-02/03）引导链的 MTK 证书校验存在可被绕过的解析逻辑缺陷。攻击者无需任何私钥，只需向 CERT2 追加特制 ASN.1 块，即可让被篡改的子镜像通过校验。
2. **适用形态为 `legacy`**（`BIT STRING(原始 CERT2 DER)` + `A0{ OID(2.4)+BITSTRING, OID(2.1)+BITSTRING }`），对应"任意对象都递归进入"的解析路径（工具 README 所述 V5/旧 V6 行为），与第 9 节反汇编所得 `mode 0 → tag 0x20` 的宽松分支吻合。
3. **`new`（V6）形态在本机不成立**：其 `A0` 前缀不被该解析器接受，导致校验直接失败。
4. **已验证生效的目标**：`lk_main_dtb`（由 LK 校验）。同一 libsec 亦用于 BL2_EXT 对 `lk`/`atf`/`gz` 的校验，理论上同样可绕过（未实测）。
5. **影响**：可绕过可信启动，进而移除 BL2_EXT/LK 的镜像校验与引导锁逻辑，等价于不依赖官方解锁流程取得引导链控制权。
6. **对既有 CVE 的补充**：该缺陷独立于 CVE-2023-20696 / CVE-2025-20730，且前置条件（物理接触 + 可写分区）低于两条 CVE 所要求的"已持有 System 权限"。

### 11.4 处置

- 实验结束后用原始 `lk_a.img`（SHA256 `1558f6574c08181cf95a8b219ccfbf47d2eca56f6082bc2db5dca3f9bc9d76d1`）刷回，恢复出厂校验状态。
- 向 MTK / OPLUS 反馈该解析逻辑缺陷，确认 MT6983 preloader 的修复状态。

---

## 12. 后续：LK AVB 门禁修补（真机验证通过）

### 12.1 三层校验的区分

| 层 | 校验对象 | 执行者 | 信任根 |
|---|---|---|---|
| ① MTK 引导链证书校验 | 引导器自身（preloader / BL2_EXT / lk / atf / gz / lk_main_dtb） | BROM→preloader→BL2_EXT→LK 逐级 | eFuse 公钥哈希 + CERT1/CERT2 RSA-PSS |
| ② AVB | Android 侧镜像（boot / init_boot / vbmeta / system / vendor …） | LK | vbmeta 公钥与描述符 |
| ③ dm-verity | 运行时 system/vendor 块设备 | 内核 | vbmeta hashtree 描述符 |

第 10/11 节绕过的是 **①**；本节处理 **②**；**③** 尚未处理。

### 12.2 LK 侧关键地址（`lk` 子镜像内偏移，镜像存于文件 0x200 起）

| 地址 | 内容 |
|---|---|
| `0x30fbc → 0x8229c` | 计算 `img_auth_required`：按分区名查表（表在 `.data 0xf9108`，条目 0x30 字节，候选字段 +0x20/+0x24/+0x28/+0x2c，由校验模式二选一） |
| `0x51318-0x51338` | `[AVB] img_auth_required = %d`；`0x51330: cbnz w21, #0x5135c` 决定是否需要认证 |
| `0x51338` | 不需要认证分支：`mov w28,#1; mov w0,#2`（状态=2 → Orange State 警告） |
| `0x5135c` | 需要认证分支：`mov w28,#0; mov w0,#3` |
| `0x514c4` | `bl #0x92060`：AVB 实际校验调用 |
| `0x515c8 / 0x515e4 / 0x515f8 / 0x515fc` | `w23 = (img_auth_required==0)`；`w23==1` 时跳过 `0x515fc` 的 AVB 失败判断 |
| `0x519cc` | 读状态全局 `0xce00d18`；=2 显示 Orange State 并等待 5 秒；=1/3 直接尾调 `0x5307c` |
| `0x50f84` | dm-verity 状态设置（由状态值驱动） |
| `0x52fd4` 等 | `double_check_lock_state`：比对 seccfg 与 RPMB 记录的锁状态（**本次未触碰该路径**） |

### 12.3 验证过程与结果

**前置：确认 ① 可绕用于 `lk` 本身**

| 镜像 | `lk` 改动 | 注入 | 结果 |
|---|---|---|---|
| `lk_a_probe_lkdata_plain.img` | data 尾字节 | 无 | 卡第一屏（BL2_EXT 拒绝） |
| `lk_a_probe_lkdata_legacy.img` | 同一字节 | legacy | **正常进系统** |

⇒ BL2_EXT 层的校验同样可被 legacy 注入绕过，`lk` 本体可自由修改。

**AVB 门禁修补：两次尝试**

| 版本 | 改动 | 结果 |
|---|---|---|
| v1（`lk_a_probe_patched.img`） | `0x51530` NOP **＋** `0x51538` `mov w0,#2`→`#3` | **卡第一屏** |
| v2（`lk_a_probe_patched2.img`） | **仅** `0x51530` NOP | **Orange State → 正常进系统** |

失败原因分析：v1 的净效果是「跳过认证（`w28=1`）」+「对外声称已验证（状态 3）」，该组合在代码中不存在对应路径，故挂起。v2 保持状态 2（与"不需要认证"语义一致），符合设备对未解锁状态的既有处理，因而正常。

**实锤**：

- `0x51330` 的 `cbnz w21, #0x5135c` 改为 `nop`（4 字节 `d5 03 20 1f`）即令 `img_auth_required` 被忽略，AVB 校验失败不再致命；
- 引导链允许被修改的 `boot` 引导。锁状态（seccfg/RPMB）全程未改动；
- 代价：会显示 Orange State 警告（约 5 秒），这是状态值 2 的正常表现。

### 12.4 产物

| 文件 | SHA256 | 说明 |
|---|---|---|
| `lk_a_probe_patched2.img` | `1660b578a3eb261e7600b4e09ffb2508f07852c51b04c692867696e76ad03935` | 可用版本：仅 NOP `0x51530` + legacy 注入，5242880 字节 |
| `lk_a_probe_lkdata_legacy.img` | `d2482d63b6fb4e30f02867c02de33d9a349ed99f1b77cbbb1af0395d24047772` | 前置验证用 |
| `lk_a.img`（原始） | `1558f6574c08181cf95a8b219ccfbf47d2eca56f6082bc2db5dca3f9bc9d76d1` | 还原用 |

### 12.5 尚未处理

1. **Orange State 警告**：可通过修改 `0x519cc` 中对状态 2 的判断（如 `0x519ec` 的 `cmp w8,#2`）使其不再走警告分支，但 `androidboot.verifiedbootstate` 可能仍上报为 orange。
2. **dm-verity（③）**：由 `0x50f84` 与状态值驱动；改过的 `system` 是否被内核接受尚未验证。建议先在只替换 `boot` 的场景下验证 `②` 的实际效果。

### 10.4 风险与处置

- 刷写引导分区有变砖风险；本次实验为**用户自行操作**，报告方未执行任何设备写入。
- 判定成立后的影响：可绕过可信启动，进而移除 BL2_EXT 对 lk/atf/gz、LK 对 lk_main_dtb 的校验，以及引导锁相关逻辑，等价于不依赖官方解锁流程取得引导链控制权。
- 建议：实验结束后用原始 `lk_a.img`（SHA256 `1558f6574c08181cf95a8b219ccfbf47d2eca56f6082bc2db5dca3f9bc9d76d1`）刷回，恢复出厂校验状态。
