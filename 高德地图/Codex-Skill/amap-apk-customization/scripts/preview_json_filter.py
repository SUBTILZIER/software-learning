#!/usr/bin/env python3
"""Preview reusable My, message, or scene JSON filtering on a fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MY_BLOCKED_KEYS = {
    "MineNewVirtualAssetCard",
    "MineNewDoubleRowCard",
    "MineMemberRecommendTaskCard",
    "MineGoodsDisplayCard",
    "PopularActivitiesCard",
    "MineNewVirtualAssetCardV3",
    "UserCircleCard",
    "MineMemberRecommendTaskCardV2",
    "MineUserEmblemPopup",
    "UserCircleCardV3",
    "PopularActivitiesCardV5",
    "ContentCenterFeedCard",
    "PopularActivitiesCardV2",
}
MY_BLOCKED_TITLES = {"店铺入驻", "地图共建", "家人地图", "地图小程序"}
MESSAGE_BLOCKED = ("超划算", "借钱", "活动", "打卡消息", "地点评论", "真探", "公共交通动态", "高德运动", "足迹动态")


def prune_mine(value):
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                if item.get("dataKey") in MY_BLOCKED_KEYS or item.get("title") in MY_BLOCKED_TITLES:
                    continue
            result.append(prune_mine(item))
        return result
    if isinstance(value, dict):
        return {k: prune_mine(v) for k, v in value.items()}
    return value


def prune_message(root: dict) -> dict:
    data_list = root.get("data", {}).get("dataList")
    if not isinstance(data_list, list):
        return root
    kept = []
    for item in data_list:
        title = item.get("data", {}).get("info", {}).get("title", "") if isinstance(item, dict) else ""
        if any(token in title for token in MESSAGE_BLOCKED):
            continue
        kept.append(item)
    root["data"]["dataList"] = kept
    return root


def prune_scene(root: dict) -> dict:
    data = root.get("data")
    if isinstance(data, dict):
        root["data"] = {"toolsRecommend": data["toolsRecommend"]} if "toolsRecommend" in data else {}
    return root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("mine", "message", "scene"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = json.loads(args.input.read_text(encoding="utf-8"))
    result = prune_mine(obj) if args.mode == "mine" else prune_message(obj) if args.mode == "message" else prune_scene(obj)
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
