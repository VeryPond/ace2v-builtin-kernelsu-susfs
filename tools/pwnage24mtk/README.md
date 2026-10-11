# pwnage24mtk 工具使用说明

上游：https://github.com/kasnria001/pwnage24mtk
（本项目内为**原样收录**，仅用于本机分析复现。）

## 脚本

| 脚本 | 用途 |
|---|---|
| `parse-part-img.py` | 拆分 MKIMG 容器为单子镜像 |
| `build-part-img.py` | 把修改后的子镜像回填容器（`replace`）或拼接（`concat`） |
| `sign_mtk_cert.py` | 向 CERT2 注入伪造哈希块（`-w`；旧路径加 `--legacy`） |
| `verify_mtk_image.py` | 复现签名/哈希校验，输出 VALID / INVALID |
| `parse_mtk_certs.py` | 解析并打印证书 ASN.1 结构 |

## 典型流程

```sh
python parse-part-img.py lk_a.img --split -o lk_a_split
# 编辑 lk_a_split/lk.bin
python sign_mtk_cert.py lk_a_split/lk.bin -w --legacy -o lk_new.bin
python build-part-img.py replace lk_a.img --name lk --file lk_new.bin -o lk_patched.img
python verify_mtk_image.py lk_patched.img --all
```

## 已知工具限制

### 1. `md1rom` 被误判

`md1img_a/b` 的 `md1rom` 子镜像 CERT1 `img_type=0x02000001`
（MD 变体，证书名 `cert1md`），而 `verify_mtk_image.py` 硬编码只接受
`IMG_TYPE_CERT1=0x02000000`，故直接报错。

把该常量放宽为镜像实际值后，`md1rom` 的四项校验全部 OK。
**属工具适配性缺陷，非固件问题。**

### 2. `Cs.disasm` 静默停止

用 Capstone 做线性反汇编时，默认遇无法解码字节即停止，
会使整轮扫描返回 0 条。必须启用 `skipdata=True`。

### 3. 架构识别

上游 README 自述"architecture detect 有问题，待修"。

## 重要限定

`verify_mtk_image.py` 的 VALID 出自**工具自带的校验器**，
它实现的是工具作者对设备解析逻辑的**建模**。
模型内 VALID 只证明"该缺陷形态在本固件数据结构上成立、payload 可构造"，
**不等于真机 preloader 会接受**——真机行为需实机验证
（本项目已做，见 `docs/LK_EXPLOIT_VERIFY.md`）。
