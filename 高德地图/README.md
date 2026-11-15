# 高德地图

本目录保存高德地图 Android 非 Root 定制包、Codex Skill、技术报告、源码差异和验证记录。

## 当前版本

- 应用版本：`17.03.0.2008`（versionCode `170300`）
- 测试设备：Redmi K60 Pro / Android 13
- APK SHA-256：`D2226C697643BF01B44DA36DADC034005BA69F47AD9BB9A6B301025A0857F60C`
- 状态：已在 K60 实机安装，设备 `base.apk` 与交付 APK 哈希一致

该版本同时修复：

1. 16.12 客户端能够唤醒“你好高德”，但执行“导航去公司”时被服务端提示版本不再支持；
2. 升级 17.03 后，回家/单位/常去地点下面的天气、推荐和猜你喜欢卡片重新出现；
3. “我的”页重新下发借钱、店铺入驻、地图共建、家人地图等入口。

最终保留固定快捷按钮、回家、单位、常去地点、编辑、订单、收藏、足迹与唤醒语音命令；继续过滤天气、推荐流、猜你喜欢及指定营销入口。

## 下载与解压

GitHub 普通 Git 单文件限制为 100MB，APK 被压缩为 7-Zip 并拆成三个 90MiB 以内分卷：

```text
Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk.7z.001
Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk.7z.002
Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk.7z.003
```

将三个分卷放在同一目录，从 `.001` 开始解压：

```powershell
7z x Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk.7z.001
```

解压后得到：

```text
Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk
```

安装前校验：

```powershell
Get-FileHash -Algorithm SHA256 .\Amap_17.03.0.2008_Voice_HomeFix_NonRoot_Optimized.apk
```

预期：

```text
D2226C697643BF01B44DA36DADC034005BA69F47AD9BB9A6B301025A0857F60C
```

## 文档

- [技术报告](./TECHNICAL_REPORT.md)
- [验证记录](./VERIFICATION.txt)
- [Smali 差异](./PATCH_DIFF.patch)
- [SHA-256 校验](./SHA256SUMS.txt)
- [回滚脚本](./ROLLBACK.sh)

## Codex Skill

Skill 位于：

```text
Codex-Skill/amap-apk-customization
```

复制到用户的 `.codex/skills/` 后调用：

```text
$amap-apk-customization
```

## 历史版本说明

旧的 `16.12.0.2027` 包体更轻，但服务端已经拒绝其 AI 语音命令协议，因此从当前目录移除。Git 历史仍保留旧分卷和对应报告；需要研究历史实现时可从旧提交恢复。
