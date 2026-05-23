import json
import re
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Mapping
from urllib.parse import urljoin


@dataclass(frozen=True)
class DataUpdateResult:
    ok: bool
    message: str
    champion_count: int


@dataclass(frozen=True)
class AugmentStat:
    augment_id: str
    tier: str
    win_rate: float
    num_games: int
    pick_rate: float


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

        detail_href = next((link for link in row[1]["links"] if re.search(r"champion-stats/\d+", link)), "")
        match = re.search(r"champion-stats/(\d+)", detail_href)
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
            "_detail_href": detail_href,
        }

    return champions


class AugmentCatalogParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names: dict[str, str] = {}
        self.current_augment_id: str | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            match = re.search(r"/augments/(\d+)", attrs.get("href", ""))
            if match:
                self.current_augment_id = match.group(1)
            return

        if tag == "img":
            self._capture_alt(attrs)

    def handle_startendtag(self, tag, attrs):
        if tag == "img":
            self._capture_alt(dict(attrs))

    def handle_endtag(self, tag):
        if tag == "a":
            self.current_augment_id = None

    def handle_data(self, data):
        if not self.current_augment_id or self.current_augment_id in self.names:
            return
        text = re.sub(r"\s+", " ", unescape(data)).strip()
        if _looks_like_augment_name(text):
            self.names[self.current_augment_id] = text

    def _capture_alt(self, attrs: dict):
        if not self.current_augment_id:
            return
        alt = attrs.get("alt")
        if alt:
            self.names.setdefault(self.current_augment_id, unescape(alt).strip())


def parse_augment_catalog(html: str) -> dict[str, str]:
    parser = AugmentCatalogParser()
    parser.feed(html)
    names = dict(parser.names)

    # The source is a minified Next.js page. Keep a small regex fallback for
    # cards whose anchor/image nesting is not emitted as balanced HTML.
    for match in re.finditer(
        r'href=["\'][^"\']*/augments/(\d+)["\'][\s\S]{0,1000}?alt=["\']([^"\']+)["\']',
        html,
    ):
        names.setdefault(match.group(1), unescape(match.group(2)).strip())
    for match in re.finditer(
        r'href=["\'][^"\']*/augments/(\d+)["\'][\s\S]{0,1000}?<p[^>]*>([^<]+)</p>',
        html,
    ):
        text = re.sub(r"\s+", " ", unescape(match.group(2))).strip()
        if _looks_like_augment_name(text):
            names.setdefault(match.group(1), text)

    return names


def _looks_like_augment_name(text: str) -> bool:
    if not text:
        return False
    if text in {"白银", "黄金", "棱彩", "选取率"}:
        return False
    if text.startswith("选取率") or text.startswith("#"):
        return False
    if re.fullmatch(r"\d+(\.\d+)?%?", text):
        return False
    return True


def parse_champion_detail_augments(html: str, augment_names: Mapping[str, str]) -> list[str]:
    stats = _extract_augment_stats(html)
    ranked = sorted(
        stats.values(),
        key=lambda stat: (_int_or_default(stat.tier, 99), -stat.win_rate, -stat.num_games, -stat.pick_rate, stat.augment_id),
    )

    augments = []
    seen = set()
    for stat in ranked:
        name = augment_names.get(stat.augment_id)
        if not name or name in seen:
            continue
        augments.append(name)
        seen.add(name)
    return augments


def _extract_augment_stats(html: str) -> dict[str, AugmentStat]:
    escaped = re.compile(
        r'\\"(?P<id>\d+)\\":\{\\"tier\\":\\"(?P<tier>[^"]+)\\",'
        r'\\"num_win_games\\":\\"(?P<wins>\d+)\\",'
        r'\\"win_rate\\":\\"(?P<win_rate>[\d.]+)\\",'
        r'\\"num_games\\":\\"(?P<num_games>\d+)\\",'
        r'\\"pick_rate\\":\\"(?P<pick_rate>[\d.]+)\\"',
    )
    plain = re.compile(
        r'"(?P<id>\d+)":\{"tier":"(?P<tier>[^"]+)",'
        r'"num_win_games":"(?P<wins>\d+)",'
        r'"win_rate":"(?P<win_rate>[\d.]+)",'
        r'"num_games":"(?P<num_games>\d+)",'
        r'"pick_rate":"(?P<pick_rate>[\d.]+)"',
    )

    stats: dict[str, AugmentStat] = {}
    for pattern in (escaped, plain):
        for match in pattern.finditer(html):
            augment_id = match.group("id")
            stats[augment_id] = AugmentStat(
                augment_id=augment_id,
                tier=match.group("tier"),
                win_rate=_float_or_zero(match.group("win_rate")),
                num_games=_int_or_zero(match.group("num_games")),
                pick_rate=_float_or_zero(match.group("pick_rate")),
            )
    return stats


def _float_or_zero(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int_or_zero(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _int_or_default(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
    max_workers: int = 8,
) -> DataUpdateResult:
    data_path = Path(data_path)
    existing = _load_existing(data_path)
    html = fetcher(source_url)
    champions = parse_champion_table(html)
    if not champions:
        return DataUpdateResult(False, "未解析到英雄数据", 0)

    base_url = source_url.rstrip("/") + "/"
    augment_catalog = _fetch_augment_catalog(base_url, fetcher)
    ordered_ids = list(champions)
    hydrated: dict[str, dict] = {}
    detail_count = 0

    if max_workers <= 1 or len(champions) <= 1:
        for champion_id in ordered_ids:
            hydrated_id, champion, used_detail = _hydrate_champion(
                champion_id,
                champions[champion_id],
                existing,
                base_url,
                augment_catalog,
                fetcher,
            )
            hydrated[hydrated_id] = champion
            detail_count += int(used_detail)
    else:
        workers = max(1, min(max_workers, len(champions)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _hydrate_champion,
                    champion_id,
                    champions[champion_id],
                    existing,
                    base_url,
                    augment_catalog,
                    fetcher,
                ): champion_id
                for champion_id in ordered_ids
            }
            for future in as_completed(futures):
                hydrated_id, champion, used_detail = future.result()
                hydrated[hydrated_id] = champion
                detail_count += int(used_detail)

    champions = {champion_id: hydrated[champion_id] for champion_id in ordered_ids}

    payload = {
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "source": source_url,
        "champions": champions,
    }
    with data_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    return DataUpdateResult(True, f"更新成功，完整海克斯 {detail_count}/{len(champions)}", len(champions))


def _fetch_augment_catalog(base_url: str, fetcher: Callable[[str], str]) -> dict[str, str]:
    try:
        return parse_augment_catalog(fetcher(urljoin(base_url, "augments")))
    except Exception:
        return {}


def _hydrate_champion(
    champion_id: str,
    champion: dict,
    existing: dict,
    base_url: str,
    augment_catalog: Mapping[str, str],
    fetcher: Callable[[str], str],
) -> tuple[str, dict, bool]:
    champion = dict(champion)
    old = existing.get("champions", {}).get(champion_id, {})
    preview_augments = list(champion.get("augments") or [])
    old_augments = list(old.get("augments") or [])

    full_augments: list[str] = []
    if augment_catalog:
        try:
            detail_href = champion.get("_detail_href") or f"champion-stats/{champion_id}"
            detail_html = fetcher(urljoin(base_url, detail_href))
            full_augments = parse_champion_detail_augments(detail_html, augment_catalog)
        except Exception:
            full_augments = []

    champion.pop("_detail_href", None)
    champion["items"] = old.get("items", [])
    if full_augments:
        champion["augments"] = full_augments
        return champion_id, champion, True

    if old_augments and len(old_augments) > len(preview_augments):
        champion["augments"] = old_augments
    elif preview_augments:
        champion["augments"] = preview_augments
    else:
        champion["augments"] = old_augments
    return champion_id, champion, False


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
