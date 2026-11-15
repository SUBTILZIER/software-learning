---
name: amap-apk-customization
description: Reverse-engineer and customize Android AMap packages (com.autonavi.minimap), including ad/feed removal, feature retention, non-root packaging, device validation, performance comparison, and rollback. Use only for AMap APK analysis or modification, not ordinary Android application development.
---

# AMap APK Customization

Use this skill for 高德地图 APK version selection, reverse analysis, slimming, UI/data filtering, non-root repackaging, device tests, and release artifacts.

## Required outcome

- Preserve the official APK and its SHA-256; modify a decoded copy.
- Prefer selective data/request filtering over deleting shared navigation code or merely hiding rendered views.
- Preserve the user-selected core flows. Unless the current request says otherwise, verify map/search/navigation, fixed shortcuts, nearby search, genuine messages/taxi chat, favorites/orders, and the wake-word assistant.
- Produce a signed installable APK plus source diff, verification record, and executable rollback script.
- Test the exact delivered hash on the named device. Do not reboot a phone merely for an ordinary APK/UI change.

## Route the work

1. Inventory every candidate with `scripts/inspect_amap_apk.py`. Reject a Play base split as a standalone candidate when it has no native libraries.
2. For version/architecture and patch-map decisions, read [references/implementation-playbook.md](references/implementation-playbook.md).
3. Before building or touching a device, read [references/known-pitfalls.md](references/known-pitfalls.md).
4. For installation, UI checks, benchmarks, artifacts, and rollback, follow [references/validation-and-release.md](references/validation-and-release.md).

## Decision rules

- **Data first:** intercept decoded AOS JSON before AJX/UI rendering. Delete only known cards, entries, or fields. Preserve nearby, message, taxi, order, and wake-word endpoints explicitly.
- **Request stop when unused:** if a feature is unwanted and has its own request entry point, return before one-shot location or network dispatch. Hiding a card alone does not remove request cost.
- **View clipping is a fallback:** use it only for a local AJX shell that remains after its payload/request is removed. Choose the boundary from measured UI bounds and retest large/small state variants.
- **Cached versus new data:** distinguish server responses, local cache, and rendered rows. A network filter may not remove old cached content. Do not add a UI filter that leaves blank rows when the user prefers cached rows to remain visible.
- **Universal versus device-specific:** keep vendor push services for a universal build when real taxi/message notifications matter. Disabling non-current OEM push is appropriate only for an explicitly device-specific build.
- **Avoid physical module deletion by default:** reflection, plugin registration, native libraries, and the embedded-official signature layer make apparent dead code risky and size savings smaller than expected.

## Non-root packaging invariants

- Ensure the signature-compatibility superclass and helper classes are present before build.
- Include `assets/origin473.apk` in the rebuilt APK before overlap composition, otherwise the origin payload may exist without a central-directory entry.
- Align uncompressed entries and sign v1/v2/v3. Android 11+ rejects an uncompressed, unaligned `resources.arsc`.
- Verify the embedded official payload hash separately from the outer APK hash.
- Install only after the signature and overlap checks pass.

## Completion evidence

Record exact commands, inputs, literal results, and exit statuses for:

- baseline official hash/signature;
- modified build/signature/origin verification;
- device install and installed-base hash;
- requested functional regressions;
- five cold starts, process count, PSS/RSS, audio app-op, and crash scan;
- rollback on a separate copy while the delivered APK remains modified.

Keep screenshots and UI dumps containing account or location data out of final artifacts.
