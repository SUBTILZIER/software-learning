# 高德地图 17.03 非 Root 语音与首页精简修复技术报告

**日期：** 2026-11-15（Asia/Shanghai）

**最终版本：** 17.03.0.2008（versionCode 170300，targetSdk 35）

**最终 APK SHA-256：** `D2226C697643BF01B44DA36DADC034005BA69F47AD9BB9A6B301025A0857F60C`

**内嵌官方 APK SHA-256：** `287202D017D27C6BBACB84C658DA9A6CC265655C4CF9E44D878127B50836D15B`

## 1. 最终目标

最终包需要同时满足：

- 普通非 Root 手机可安装；
- “你好高德”唤醒后能够执行导航命令；
- 首页保留固定快捷入口及回家/单位/常去地点/编辑；
- 首页上述固定区域以下不再显示天气、推荐、猜你喜欢等卡片；
- 页面上滑、冷启动、保留旧数据时也不能重新露出卡片；
- “我的”页保留订单、收藏、待评价、钱包卡券和足迹；
- 继续移除店铺入驻、地图共建、家人地图、地图小程序、借钱、高德超划算和真探入口；
- 保留附近、打车会话、订单消息、二维码与核心导航能力；
- 提供差异、验证和回滚记录。

## 2. 版本迁移与问题根因

### 2.1 16.12 语音命令失效

16.12 包的录音权限、唤醒词和 ASR 均正常：说“你好高德”会得到响应，语音也能识别成“导航去公司”。但服务器随后返回：

```text
当前版本已不再支持 AI 对话，请升级至最新版本后继续使用。
```

旧任务的关键状态为：

```text
sceneType=ai_native
msgStatus=valid
agent_intent=tool_agent
```

这说明故障不是麦克风、KWS 或 ASR，而是服务端拒绝旧客户端的 AI 命令协议。修改提示文案或录音权限不会恢复命令执行，因此底包迁移到 17.03。

### 2.2 17.03 首页卡片回归

最初采用的 17.03 Clean8 只包含：

- 禁止 QuickService 面板展开；
- 停止 `WeatherUnit` 和 `ExploreFeedAgent`；
- 隐藏天气 Widget；
- 保留固定快捷入口。

它没有包含后来在 16.12 中成熟的 `CleanHomeFilter` 和最终 QuickService 缓存裁剪。覆盖升级又保留了应用数据，所以旧天气、推荐和图片卡片重新从“回家/单位/常去地点”下面渲染。

本轮修复把 16.12 的成熟数据层过滤移植到 17.03，并增加 188dp 显示层兜底。

## 3. 非 Root 打包结构

继续使用已验证的非 Root 兼容架构：

1. `NewMapApplication` 继承签名兼容 Application；
2. 加入 `bin.mt.signature` 与 `libSignatureKiller473.so`；
3. 内嵌官方 APK 为 `assets/origin473.apk`；
4. 普通重建并使用测试证书生成 v1 签名；
5. 通过重叠 ZIP 复用官方包中未变化的条目；
6. 写入布局保持的 v2/v3 签名块。

最终验证：

```text
v1=true
v2=true
v3=true
embedded official SHA256=287202D017D27C6BBACB84C658DA9A6CC265655C4CF9E44D878127B50836D15B
```

## 4. AOS 统一过滤入口

在 `AosResponse.getResponseBodyData()` 返回业务层前调用：

```text
GaodeMapPatcher.patchAosResponseBody(byte[], response)
```

最终数据流：

```text
服务器响应 → URL识别 → 精确过滤 → AJX/原生页面 → UI
```

首页、消息、我的页使用不同规则，不能用一个全局空响应替代。

## 5. 首页卡片修复

### 5.1 直接返回空数据的接口

以下首页非核心接口返回结构正确的空响应：

```text
/ws/faas/amap-navigation/main-page-aiqs
/ws/promote/main-page/assets
/ws/promote/main-page/location
/ws/valueadded/weather/v2
/ws/render/weatherservice/historyweather
```

空响应结构：

```json
{"code":"1","data":{},"result":"true","success":true,"message":"Successful."}
```

这样卡片不会进入 AJX 解析、布局、图片加载与曝光流程。

### 5.2 保留固定快捷入口

`/shield/scene/recommend` 同时承载固定快捷按钮和推荐内容。完全拦截会导致驾车、公交、打车、酒店等入口消失。

`CleanHomeFilter.filterScene()` 只保留：

```text
data.toolsRecommend
```

其余推荐字段被删除，因此固定按钮保留，推荐卡片不再生成。

### 5.3 旧缓存兜底

仅过滤新响应不能清除账号/AJX 已保存的天气和推荐卡片。因此在：

```text
smali_classes5/com/autonavi/bundle/amaphome/components/quickservice/QSScrollContainerV2.smali
```

将内部容器固定为 188dp，并启用：

```text
clipChildren=true
clipToPadding=true
```

该边界在 K60 上保留：

```text
固定快捷按钮
回家
去单位
常去地点
编辑
```

同时裁掉它们之后的天气、推荐、猜你喜欢和图片卡片。

### 5.4 上滑与冷启动

`NewQuickServiceView.onPanelStateChanged()` 继续把 `EXPANDED` 重定向到 `ANCHORED`。最终冷启动和上滑后结果一致：

```text
回家=1
去单位=1
常去地点=1
编辑=1
天气=0
16°=0
多云=0
推荐=0
猜你喜欢=0
```

## 6. 语音命令保留

`GaodeMapPatcher` 对下列端点立即返回原始字节：

```text
/v1/ai_rec/
```

首页和消息过滤不会继续处理它。

17.03 语音修复阶段的实机任务结果：

```text
questionText=导航去公司。
sceneType=ai_native
msgStatus=valid
result=0
agent_intent=sdm
```

手机随后打开公司路线页。首页卡片补丁完成后又验证：

```text
RECORD_AUDIO=allow (running)
/v1/ai_rec/ branch=return original
```

手动 SearchBar 语音按钮仍关闭，但后台唤醒管线保留。

## 7. “我的”页过滤

保留：

```text
订单
收藏
待评价
钱包卡券
足迹
```

按卡片类与标题删除：

```text
店铺入驻
地图共建
家人地图
地图小程序
互动专区
高德超划算
借钱
借钱服务
高德真探运营官
真探运营官
```

最终 K60 UI 计数：保留项均为 1，删除项均为 0。

## 8. 消息与附近保护

明确原样保留：

```text
/c3frontend/af-nearby/nearby
/shield/search/nearbyrec_smart
/ws/message/notice/list
/ws/msgbox/pull_mp
/v1/ai_rec/
```

`CleanMessageFilter` 只过滤新的营销会话更新；订单、司机、打车等实际消息不按营销标题命中。

## 9. 构建与体积

```text
修复前 17.03 Clean8：221,612,055 bytes
最终修复包：          221,616,151 bytes
增加：                4,096 bytes
```

新增 4KB 来自最终签名布局；数据过滤和 Smali 逻辑本身体积影响很小。

GitHub 交付使用 7-Zip：

```text
压缩包：203,145,935 bytes
分卷：90MiB + 90MiB + 14,402,255 bytes
```

分卷重组后归档哈希与原归档一致，解压后的 APK 哈希与 K60 已安装 `base.apk` 一致。

## 10. 实机验证

设备：Redmi K60 Pro，Android 13，ADB 端口 5044。

通过项目：

- v1/v2/v3 签名；
- 内嵌官方 APK 哈希；
- 普通覆盖安装；
- 冷启动 `340ms`；
- 首页固定入口；
- 冷启动与上滑后卡片计数；
- “我的”页保留与删除入口；
- 语音端点原样放行与录音运行状态；
- 两个应用进程；
- 无应用 FATAL、ANR、VerifyError、NoClassDefFoundError 或 UnsatisfiedLinkError；
- 设备 `base.apk` 与交付 APK 哈希一致；
- 独立副本回滚。

未重启手机。

## 11. 回滚

本轮基线是语音可执行但首页卡片回归的 17.03 Clean8：

```text
FAE4131C66753F22D9F92C668D856AE6482FAFB043348F978681E6606048C743
```

独立副本验证：

```text
ROLLBACK_BEFORE_SHA256=D2226C697643BF01B44DA36DADC034005BA69F47AD9BB9A6B301025A0857F60C
ROLLBACK_AFTER_SHA256=FAE4131C66753F22D9F92C668D856AE6482FAFB043348F978681E6606048C743
ROLLBACK_RESULT=PASS
```

仓库回滚脚本要求调用者提供该旧 APK；Git 历史也可恢复旧版本文件。

## 12. 已知限制

1. 17.03 比 16.12 占用更多运行内存，但旧 16.12 的 AI 命令协议已被服务端拒绝；
2. 188dp 边界已在 K60 分辨率验证，迁移到特殊分辨率、字体缩放或新版布局时需重新测量；
3. 后台唤醒持续录音仍有电量成本；
4. 服务端端点、JSON 字段或卡片类名变化后，需要重新抓取首包并更新过滤表；
5. 代码和资源主要是逻辑禁用而非物理删除，包体大小不会与 UI 精简量等比例下降。

## 13. 可复用经验

- 唤醒成功不代表命令协议仍被服务器接受；必须检查新语音任务和最终动作；
- 版本迁移必须迁移完整的“请求层 + 数据层 + 缓存显示层”补丁，不能只搬运 UI 开关；
- `/shield/scene/recommend` 应保留 `toolsRecommend`，不能整体拒绝；
- `/v1/ai_rec/`、附近、订单和真实消息端点必须显式放行；
- 首页验证必须覆盖冷启动、保留旧数据和上滑三种状态；
- 最终交付必须让设备 `base.apk` 与交付文件哈希一致。
