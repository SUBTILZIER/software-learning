# Validation and Release

## Baseline

Record:

```powershell
Get-FileHash -Algorithm SHA256 OFFICIAL.apk
java -jar apksigner.jar verify --verbose --print-certs OFFICIAL.apk
aapt2 dump badging OFFICIAL.apk
```

Capture size, version code/name, target SDK, native ABI, certificate digest, and exit statuses.

## Modified APK

Verify before installation:

```powershell
java -jar apksigner.jar verify --verbose --print-certs MODIFIED.apk
python verify_overlap_origin.py MODIFIED.apk
```

Expected invariants:

- v1, v2, and v3 all verify;
- embedded official size/hash match the preserved baseline;
- package name remains `com.autonavi.minimap` unless a clone was explicitly requested;
- final outer hash is recorded.

## Installation

Use the explicit device serial and ADB port:

```powershell
adb -P PORT -s SERIAL install -r --no-streaming MODIFIED.apk
```

Use `-d` only for an intentional downgrade. After installation, hash the device `base.apk` and compare it to the delivered file.

## Functional matrix

At minimum test the requested subset of:

- launch and map render;
- search and route entry;
- fixed home shortcuts;
- Home/Company/Frequent/Edit visibility;
- weather/recommendation absence before and after swipe;
- real Message page versus AI voice page;
- taxi conversation and order reminder;
- My-page footprint/orders/favorites and removed marketing cards;
- a known POI detail followed by `搜周边` (no loading failure);
- QR/camera if retained;
- wake-word permission and active audio pipeline.
- a fresh spoken command such as `导航去公司`, with the new `ai_native` task marked valid and the route page opened; do not treat `RECORD_AUDIO` alone as command success.

For home-card regressions, record text counts before and after a cold start and an upward swipe. A verified 17.03 result kept `回家/去单位/常去地点/编辑=1` and `天气/推荐/猜你喜欢=0` in both states.

Use UIAutomator dumps for counts and bounds. Do not publish private text or map screenshots.

## Runtime matrix

Run five cold starts:

```powershell
adb shell am force-stop com.autonavi.minimap
adb shell am start -W -n com.autonavi.minimap/com.autonavi.map.activity.SplashActivity
```

Then record:

- samples, average, median, minimum, maximum;
- each package process and total PSS/RSS;
- `appops get com.autonavi.minimap RECORD_AUDIO`;
- absence of `FATAL EXCEPTION`, ANR, VerifyError, NoClassDefFoundError, and UnsatisfiedLinkError;
- presence/absence of `:widgetProvider` and push processes.

Compare packages on the same device and display mode. Cross-device numbers are descriptive, not a package-only benchmark.

## Four release artifacts

Create and reopen:

1. `MODIFIED_FILE` — final APK;
2. `DIFF_FILE` — source diff and hashes for added binary/dex resources;
3. `VERIFICATION.txt` — changed branches, exact commands, inputs, literal outputs, statuses, known limitations, installed hash;
4. executable `ROLLBACK.sh` — copy rollback and optional device restore.

Rollback must be tested on a separate copy:

```text
ROLLBACK_BEFORE_SHA256=<modified>
ROLLBACK_AFTER_SHA256=<official or prior baseline>
ROLLBACK_RESULT=PASS
```

Leave the delivered APK modified and the test device in the user-requested state. State explicitly whether a phone reboot occurred.
