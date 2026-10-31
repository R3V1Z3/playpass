#!/usr/bin/env python3
"""
Synchronize Google Play Pass Games & Apps list from Ytechb.com
Extracts categories, game titles, supported regions, and source metadata,
then writes data.js, data.json, and embeds the dataset into index.html if present.
"""

import os
import re
import json
import html as html_lib
import urllib.request
from datetime import datetime, timezone
from collections import OrderedDict

SOURCE_URL = "https://www.ytechb.com/google-play-pass-games-list/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_html(url: str, fallback_file: str = None) -> str:
    if fallback_file and os.path.exists(fallback_file):
        print(f"Reading cached HTML from {fallback_file}...")
        with open(fallback_file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    print(f"Fetching {url}...")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    text = html_lib.unescape(text)
    # Normalize curly apostrophes/quotes and non-breaking spaces
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\xa0", " ").strip()
    return text


def parse_play_pass_html(content: str) -> dict:
    # 1. Extract Date Modified
    dates = re.findall(r'dateModified["\']?\s*:\s*["\'](.*?)["\']', content)
    source_updated = dates[0] if dates else None

    # 2. Extract Supported Regions
    r_start = content.find('id="google-play-pass-regions"')
    r_end = content.find('id="google-play-pass-games-list"')
    regions = []
    if r_start != -1 and r_end != -1:
        r_sec = content[r_start:r_end]
        for li in re.findall(r"<li[^>]*>(.*?)</li>", r_sec, re.S):
            r_name = clean_text(li)
            if r_name and r_name not in regions:
                regions.append(r_name)

    # 3. Extract Categories and Games/Apps
    g_start = content.find('id="google-play-pass-games-list"')
    g_end = content.find('id="google-play-pass-games-requirements"')
    if g_end == -1:
        g_end = content.find('id="conclusion"')
    section = content[g_start:g_end] if (g_start != -1 and g_end != -1) else content

    cat_blocks = re.findall(r"<h3[^>]*>(.*?)</h3>\s*<ul[^>]*>(.*?)</ul>", section, re.S)

    categories_meta = []
    games_map = OrderedDict()
    raw_total = 0

    for cat_raw, ul_raw in cat_blocks:
        cat_name = clean_text(cat_raw)
        if not cat_name:
            continue
        # Short label (e.g. "Action Games" -> "Action")
        short_cat = re.sub(r"\s+Games$", "", cat_name, flags=re.I).strip()

        items = re.findall(r"<li[^>]*>(.*?)</li>", ul_raw, re.S)
        cat_count = 0
        for item_raw in items:
            # Check if there is an explicit anchor link
            link_match = re.search(r'href=["\'](.*?)["\']', item_raw)
            explicit_url = link_match.group(1).strip() if link_match else None

            title = clean_text(item_raw)
            if not title:
                continue

            raw_total += 1
            cat_count += 1

            key = title.lower()
            if key not in games_map:
                games_map[key] = {
                    "id": len(games_map) + 1,
                    "title": title,
                    "categories": [short_cat],
                    "fullCategories": [cat_name],
                    "url": explicit_url,
                }
            else:
                if short_cat not in games_map[key]["categories"]:
                    games_map[key]["categories"].append(short_cat)
                if cat_name not in games_map[key]["fullCategories"]:
                    games_map[key]["fullCategories"].append(cat_name)
                if explicit_url and not games_map[key]["url"]:
                    games_map[key]["url"] = explicit_url

        categories_meta.append(
            {
                "id": short_cat.lower().replace(" ", "-"),
                "name": short_cat,
                "fullName": cat_name,
                "count": cat_count,
            }
        )

    games_list = list(games_map.values())

    return {
        "sourceUrl": SOURCE_URL,
        "sourceUpdated": source_updated,
        "syncedAt": datetime.now(timezone.utc).isoformat(),
        "totalEntries": raw_total,
        "uniqueCount": len(games_list),
        "categoryCount": len(categories_meta),
        "regionCount": len(regions),
        "categories": categories_meta,
        "regions": regions,
        "items": games_list,
    }


def main():
    temp_cache = os.path.join(os.environ.get("TEMP", ""), "ytechb_playpass.html")
    html_content = fetch_html(SOURCE_URL, fallback_file=temp_cache if os.path.exists(temp_cache) else None)
    data = parse_play_pass_html(html_content)

    json_path = os.path.join(BASE_DIR, "data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    js_path = os.path.join(BASE_DIR, "data.js")
    compact_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(f"window.PLAYPASS_DATA = {compact_json};\n")

    print(
        f"Successfully extracted {data['uniqueCount']} unique titles "
        f"({data['totalEntries']} total category entries) across {data['categoryCount']} categories "
        f"and {data['regionCount']} regions."
    )
    print(f"Wrote {json_path} and {js_path}")


if __name__ == "__main__":
    main()
