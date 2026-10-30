"""Wikipedia tablo hücrelerini denetim için indirir; model verisini değiştirmez.

python tools/collect_sources.py --output work/source-review
Yalnızca açık sayfalar; giriş, CAPTCHA veya engel aşma yok. Ağ hatası görünürdür.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

PAGES = {
    "avci": "Abdullah_Avc%C4%B1",
    "conte": "Antonio_Conte",
    "nagelsmann": "Julian_Nagelsmann",
    "mendilibar": "Jos%C3%A9_Luis_Mendilibar",
    "tedesco": "Domenico_Tedesco",
    "emre": "Emre_Bel%C3%B6zo%C4%9Flu",
    "montella": "Vincenzo_Montella",
    "kuyt": "Dirk_Kuyt",
}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = []
        self.cell = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"sup", "style", "script"}:
            self.skip += 1
        if tag == "tr":
            self.row = []
        if tag in {"td", "th"}:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None and self.skip == 0:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"sup", "style", "script"}:
            self.skip = max(0, self.skip - 1)
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        if tag == "tr" and self.row:
            self.rows.append(self.row)


def collect(slug: str) -> dict:
    url = f"https://en.wikipedia.org/wiki/{slug}"
    request = Request(url, headers={"User-Agent": "CoachLab/0.1 educational source review"})
    with urlopen(request, timeout=30) as response:
        document = response.read().decode("utf-8")
    anchor = re.search(r'id="(?:Managerial_statistics|Managerial_record|Managerial)"', document)
    if anchor is None:
        raise ValueError(f"Yönetici istatistikleri bölümü bulunamadı: {url}")
    start = document.find("<table", anchor.end())
    end = document.find("</table>", start)
    if start == -1 or end == -1:
        raise ValueError(f"Tablo şeması değişti: {url}")
    section = document[start:end + len("</table>")]
    parser = TableParser()
    parser.feed(section)
    if len(parser.rows) < 3:
        raise ValueError(f"Tablo eksik: {url}")
    return {
        "url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "table_sha256": hashlib.sha256(section.encode()).hexdigest(),
        "note": "Rowspan hücreleri genişletilmemiştir. İnceleyerek birleştirin; otomatik veri güncellemesi yok.",
        "rows": parser.rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("work/source-review"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for coach_id, slug in PAGES.items():
        record = collect(slug)
        (args.output / f"{coach_id}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{coach_id}: {len(record['rows'])} satır")


if __name__ == "__main__":
    main()
