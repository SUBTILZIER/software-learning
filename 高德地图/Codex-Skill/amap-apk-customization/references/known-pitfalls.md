# Known Pitfalls

## Packaging

- Apktool output may have an uncompressed but unaligned `resources.arsc`; Android 11+ rejects installation with error `-124`.
- Signing an unaligned ordinary rebuild does not repair alignment. Align before final signing or use a layout builder that aligns stored entries.
- An overlap builder that writes origin bytes but has no `assets/origin473.apk` record in the rebuilt input can produce an unindexed payload. Add the placeholder asset before the ordinary build.
- Standard ZIP tools may misread intentional overlapping entry layouts. Use a central-directory/local-header parser and independently hash the embedded official payload.
- A downloaded Play base split can be much smaller because native libraries are missing. Do not compare it directly with a complete standalone package.

## Device and data

- Downgrading from a newer AMap version can expose incompatible app-data schemas. Back up or perform a clean install rather than clearing user data without authorization.
- Multiple ADB servers can be used on different ports. Verify the intended serial and port before every install. Do not assume the default 5037 server owns the target device.
- Restarting a Windows PnP ADB interface can leave it pending reboot. Replugging USB is preferable to rebooting the phone or PC during ordinary package work.
- UI dumps and screenshots can expose account and precise location data. Use them for diagnosis, then exclude them from deliverables.

## Runtime/UI

- `View.GONE` in an override is ineffective if the initialization path never calls `setVisibility`. Programmatic constructors and XML inflation use different paths.
- Hiding an outer `NewQuickServiceView` can remove the bottom tab bar or leave sibling layers visible. Identify the exact `home_scroll_view`/container hierarchy first.
- Fixed-height clipping can expose a card when an earlier row is absent, or hide Home/Company when the boundary is too short. Measure both states.
- Weather UI removal alone does not stop one-shot location or weather requests.
- Message server filtering does not erase old AJX/account cache. A render-time hide can leave blank positions; do not use it when the user prefers a continuous list.
- A broad URL reject can break nearby loading. Preserve or selectively filter nearby endpoints and retest a known POI's `搜周边` flow.

## Functional tradeoffs

- Disabling all vendor push services can delay driver chat and order reminders when AMap is backgrounded.
- A 16.x client may not render some new-format messages even when the message center itself works.
- Continuous wake-word audio remains a battery cost. Disabling the manual mic does not stop the wake-word pipeline.
- Physical deletion of shared code can break reflection and plugin registries while saving little in an embedded-origin overlap package.

## Stopping conditions

- Do not install when signature, origin hash, alignment, or package identity is unverified.
- Stop iterative UI patching when a change removes a requested core entry, breaks nearby/message flows, or produces a layout gap; restore the previous candidate and change layers.
- Do not claim a final build until the installed `base.apk` hash equals the delivered APK hash.
