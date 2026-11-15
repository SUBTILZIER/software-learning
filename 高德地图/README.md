# 高德地图

本目录包含高德地图 16.12.0.2027 非 Root 平衡精简版、Codex Skill、技术报告和验证记录。

## 安装包

GitHub普通Git单文件限制为100MB，APK使用7-Zip压缩并拆成两个95MiB以内分卷：

```text
Amap_16.12.0.2027_Balanced_NonRoot_Optimized.apk.7z.001
Amap_16.12.0.2027_Balanced_NonRoot_Optimized.apk.7z.002
```

两个分卷下载到同一目录后，从 `.001` 开始解压：

```powershell
7z x Amap_16.12.0.2027_Balanced_NonRoot_Optimized.apk.7z.001
```

解压得到：

```text
Amap_16.12.0.2027_Balanced_NonRoot_Optimized.apk
```

APK SHA-256：

```text
377FBCC407F1F569906FC4D7DF2344A5BC18CBFC2F01994E848A27D5B36B43D8
```

## Codex Skill

Skill 位于：

```text
Codex-Skill/amap-apk-customization
```

复制到用户的 `.codex/skills/` 后可使用：

```text
$amap-apk-customization
```

## 文档

- [技术报告](./TECHNICAL_REPORT.md)
- [完整验证记录](./VERIFICATION.txt)
- [SHA-256校验](./SHA256SUMS.txt)
