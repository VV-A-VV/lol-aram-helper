import json
import re
import ssl
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class DataUpdateResult:
    ok: bool
    message: str
    champion_count: int


class ChampionTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = None
        self.current_cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.current_row = []
            return

        if tag == "td" and self.current_row is not None:
            self.current_cell = {"text": "", "links": [], "alts": []}
            return

        if self.current_cell is None:
            return

        if tag == "a":
            self.current_cell["links"].append(attrs.get("href", ""))
        elif tag == "img":
            alt = attrs.get("alt")
            if alt:
                self.current_cell["alts"].append(alt)

    def handle_endtag(self, tag):
        if tag == "td" and self.current_row is not None and self.current_cell is not None:
            self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            self.rows.append(self.current_row)
            self.current_row = None

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell["text"] += data


def parse_champion_table(html: str) -> dict:
    parser = ChampionTableParser()
    parser.feed(html)

    champions = {}
    for row in parser.rows:
        if len(row) < 6:
            continue

        link_text = " ".join(row[1]["links"])
        match = re.search(r"champion-stats/(\d+)", link_text)
        if not match:
            continue

        champion_id = match.group(1)
        name = re.sub(r"\s+", " ", row[1]["text"]).strip().replace("攻略", "").strip()
        tier_match = re.search(r"T\d", row[2]["text"])
        winrate_match = re.search(r"\d+\.\d+%", row[3]["text"])
        champions[champion_id] = {
            "name": name or f"ID:{champion_id}",
            "tier": tier_match.group(0) if tier_match else "?",
            "winrate": winrate_match.group(0) if winrate_match else "?",
            "augments": row[5]["alts"],
        }

    return champions


def fetch_url(url: str, timeout: float = 30.0) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read().decode("utf-8")


def update_champion_data(
    data_path: str | Path,
    source_url: str,
    fetcher: Callable[[str], str] = fetch_url,
) -> DataUpdateResult:
    data_path = Path(data_path)
    existing = _load_existing(data_path)
    html = fetcher(source_url)
    champions = parse_champion_table(html)
    if not champions:
        return DataUpdateResult(False, "未解析到英雄数据", 0)

    for champion_id, champion in champions.items():
        old = existing.get("champions", {}).get(champion_id, {})
        champion["items"] = old.get("items", [])
        if not champion["augments"]:
            champion["augments"] = old.get("augments", [])

    payload = {
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "champions": champions,
    }
    with data_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    return DataUpdateResult(True, "更新成功", len(champions))


def _load_existing(data_path: Path) -> dict:
    if not data_path.exists():
        return {"champions": {}}

    try:
        with data_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        data.setdefault("champions", {})
        return data
    except (OSError, json.JSONDecodeError):
        return {"champions": {}}
