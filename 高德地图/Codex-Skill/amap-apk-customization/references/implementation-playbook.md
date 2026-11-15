# Implementation Playbook

## Contents

- Candidate APK selection
- Non-root signature architecture
- AOS response interception
- AMap 16.12 patch map
- AMap 17.03 patch map
- Data filters
- Weather and home panel
- Messages and cache behavior

## Candidate APK selection

Inspect size, version, dex entries, native libraries, and signing certificate before decoding.

- A complete arm64 package normally has `lib/arm64-v8a/*.so`.
- A Play base APK with zero `lib/` entries is not a standalone universal candidate even when the web listing calls it an APK.
- Prefer the lightest complete version that contains the required navigation/message features and targets a current Android API.
- The official AMap certificate observed in the 16.x line had SHA-256 `b36c0b80cb2417e7fe4c3df01a2d163a7d8443604dd276a2bc1ab0d325102e3e`; verify rather than assuming it is permanent.

The 16.12.0.2027 case was a useful balance for size and nearby behavior, but a later live test showed that the wake word could answer while the server returned `当前版本已不再支持 AI 对话` for commands such as `导航去公司`. When voice-command execution is required, prefer a currently accepted client line such as the tested 17.03.0.2008 build rather than spoofing the returned text.

## Non-root signature architecture

Observed packages used an embedded official APK plus signature-compatibility layer:

1. Change `NewMapApplication` superclass from `android.app.Application` to `bin.mt.signature.KillerApplication473`.
2. Add `bin/mt/signature/*` and `libSignatureKiller473.so`.
3. Add the official APK as `assets/origin473.apk` before rebuilding so the ZIP central directory includes it.
4. Sign the ordinary rebuilt APK with the chosen test key.
5. Compose an overlap ZIP in which unchanged outer entries share bytes with the embedded official APK.
6. Add a layout-preserving v2/v3 signing block; retain v1.

The overlap design reduces the repacked size substantially. Do not remove the embedded official payload without redesigning both signature emulation and shared-entry layout.

## AOS response interception

Hook `AosResponse.getResponseBodyData()` after obtaining the response bytes and before returning them. Pass bytes plus the response object to a filter that can recover the URL and selectively transform JSON.

Preserve these flows when requested:

- `/v1/ai_rec/` for wake-word responses;
- `/ws/aos/main/page/product/list` and `/shield/dsp/profile/index/nodefaasv3` for functional My-page cards;
- `/c3frontend/af-nearby/nearby` and `/shield/search/nearbyrec_smart` for nearby search;
- message notice/conversation endpoints for real taxi and order messages.

Treat `/shield/scene/recommend` specially: it also carries `toolsRecommend`, which feeds fixed home shortcuts. Keep `toolsRecommend` and discard unrelated scene recommendation payloads instead of blocking the whole response.

## AMap 16.12 patch map

Paths are relative to an Apktool decode and may move between minor releases.

| Concern | Class/method |
|---|---|
| Signature superclass | `smali_classes6/com/autonavi/minimap/lite/NewMapApplication.smali` |
| AOS body hook | `smali/com/amap/bundle/aosservice/response/AosResponse.smali` |
| Manual home voice | `smali_classes4/com/autonavi/bundle/amaphome/components/SearchBarV2.smali` |
| AI conversation scene | `smali_classes4/com/autonavi/bundle/ai/AISceneService.smali` |
| Message tab | obfuscated config `ao2.smali` |
| Mine tab | `bo2.smali` |
| Explore/Nearby tab | `co2.smali` |
| Taxi tab | `eo2.smali` |
| Home tab | `fo2.smali` |
| QuickService content | `QSScrollContainerV2.smali` |
| Panel expansion | `NewQuickServiceView.onPanelStateChanged(...)` |
| Map weather widget | `CombineWidgetBuilderManager.setWeatherRestrictWidgetVisible(int)` |
| Home weather orchestration | `mk6.doBizLogic()` |
| Weather runnable | `smali_classes5/lk6.run()` |
| Weather API holder | `WeatherRequestHolder.sendInfo(...)` and `sendMoji(...)` |

Set unwanted tab `isEnable()` methods to false. Disable `ai_conversation` and `ai_tab_conversation` while delegating every other AI scene to preserve the wake word.

## AMap 17.03 patch map

Names are less obfuscated in the tested build:

- `HomeTabInitConfigNearbyV2.isEnable()`
- `HomeTabInitConfigMessageV2.isEnable()`
- `HomeTabInitConfigTaxiV2.isEnable()`
- `SearchBarV2` manual voice methods
- `WeatherUnit.doBizLogic()`
- `ExploreFeedAgent.start(...)`
- `NewQuickServiceView.onPanelStateChanged(...)`
- `CombineWidgetBuilderManager.setWeatherRestrictWidgetVisible(int)`
- `QSScrollContainerV2`
- `smali_classes10/com/rikkati/mod/GaodeMapPatcher.smali`
- `smali_classes10/com/rikkati/mod/CleanHomeFilter.smali`

In the tested non-root 17.03 build, `QSScrollContainerV2` was in `smali_classes5`. The 188dp clipped inner container preserved fixed quick tools plus Home/Company/Frequent/Edit on the K60 while preventing cached weather/recommendation cards from rendering below them.

Do not transplant paths blindly. Search by interface, endpoint, scene name, or visible behavior on each version.

## My-page data filters

Filter the decoded response before AJX sees it. For the 16.12 case, preserve:

- `MineNewFootprintCard`
- `MineNewBEntranceCard`

Observed marketing/optional cards included:

- `MineNewVirtualAssetCard`
- `MineNewDoubleRowCard`
- `MineMemberRecommendTaskCard`
- `MineGoodsDisplayCard`
- `PopularActivitiesCard`

The 17.03 line used related names with suffixes such as `V2`, `V3`, or `V5`; support both families when one filter is reused.

Nested `MineNewBEntranceCard.entranceList` can be filtered by exact title. Observed removable entries included 店铺入驻, 地图共建, 家人地图, 地图小程序, 借钱, 借钱服务, 高德超划算, 高德真探运营官, and 真探运营官. Keep titles requested by the user, such as 订单, 收藏, 待评价, or 钱包卡券.

Measured effect in the case study: seven cards and a 63,377-byte cached JSON payload became two cards and a 2,349-byte payload.

## Home panel and weather

Use three layers in this order:

1. **Data layer:** block main-page AI/promote payloads; retain only fixed `toolsRecommend` data.
2. **Request layer:** return before weather one-shot location and network dispatch (`mk6`, `lk6`, and `WeatherRequestHolder`).
3. **View fallback:** if the AJX bundle still draws a local empty weather shell, clip below the fixed shortcuts plus Home/Company/Frequent/Edit row. In the tested 16.12 layout, 188dp retained that row; 150dp hid it.

Keep the panel anchored when the user does not want expandable feed content.

When migrating a working 16.12 customization to 17.03, port both the response filter and the view clip. The earlier Clean8 build only stopped expansion and selected requests; an in-place upgrade with preserved data rendered cached weather/recommendation cards again. The corrected 17.03 build returned empty data for main-page AI/promote/weather endpoints, retained only `toolsRecommend` from `/shield/scene/recommend`, and clipped the inner QuickService container at 188dp. Cold-start and upward-swipe checks both kept Home/Company/Frequent/Edit present while weather/recommendation counts stayed zero.

Always return the original bytes for `/v1/ai_rec/`. This endpoint carried the working 17.03 voice-command flow and must not pass through home or message filters.

## Message filtering and local cache

Conversation updates were observed at `/ws/amc/server/conv/raise_list` with objects shaped like:

```json
{"act":"UPDATE","data":{"id":"...","info":{"title":"..."}}}
```

Filter new marketing updates only after a cheap string pre-check for `dataList` plus target keywords. Do not parse every AOS response unconditionally.

Old conversations can be restored from an opaque AJX/account cache after force-stop or reinstall. Network filtering therefore does not guarantee old rows disappear. Hiding rendered rows can leave visible gaps. Follow the current user's choice:

- keep cached rows visible while blocking new updates; or
- implement a message-page-specific rendering strategy that also reflows rows, after validating it does not leave blanks.

Always preserve taxi and order conversations unless explicitly asked otherwise.
