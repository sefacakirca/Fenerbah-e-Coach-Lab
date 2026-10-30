"""Kaynak verisinin sınırlarını doğrular; hatalı girdiyi sessizce düzeltmez."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

CRITERIA = (
    "last_team_ppg", "career_ppg", "communication", "style_fit",
    "big_club", "derby", "europe",
)
SUBJECTIVE = ("communication", "style_fit", "big_club", "derby")
LABELS = {
    "last_team_ppg": "Son takım PPG", "career_ppg": "Kariyer PPG",
    "communication": "İletişim", "style_fit": "Oyun uyumu",
    "big_club": "Büyük kulüp", "derby": "Yerel derbi", "europe": "Avrupa",
}


def finite_number(value, label: str, lower=None, upper=None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: sonlu sayı bekleniyor")
    if (lower is not None and value < lower) or (upper is not None and value > upper):
        raise ValueError(f"{label}: aralık dışı ({value})")
    return float(value)


@dataclass(frozen=True)
class Record:
    games: int
    wins: int
    draws: int
    losses: int

    def __post_init__(self):
        for value in (self.games, self.wins, self.draws, self.losses):
            if type(value) is not int or value < 0:
                raise ValueError("Maç ve sonuç sayıları negatif olmayan tamsayı olmalı")
        if self.wins + self.draws + self.losses != self.games:
            raise ValueError("Galibiyet + beraberlik + mağlubiyet, maç sayısına eşit olmalı")

    @classmethod
    def from_dict(cls, row: dict) -> Record:
        return cls(*(row[key] for key in ("games", "wins", "draws", "losses")))

    @property
    def points(self) -> int:
        return 3 * self.wins + self.draws

    @property
    def ppg(self) -> float | None:
        return self.points / self.games if self.games else None

    def __add__(self, other: Record) -> Record:
        return Record(*(a + b for a, b in zip(self.values(), other.values())))

    def __sub__(self, other: Record) -> Record:
        return Record(*(a - b for a, b in zip(self.values(), other.values())))

    def values(self) -> tuple[int, int, int, int]:
        return self.games, self.wins, self.draws, self.losses


def total_record(tenures: list[dict]) -> Record:
    result = Record(0, 0, 0, 0)
    for tenure in tenures:
        result += Record.from_dict(tenure)
    return result


def _validate_source_ids(value, sources: dict):
    if isinstance(value, dict):
        if "source_ids" in value:
            refs = value["source_ids"]
            if not isinstance(refs, list) or not refs or any(ref not in sources for ref in refs):
                raise ValueError(f"Geçersiz veya boş kaynak listesi: {refs}")
        for child in value.values():
            _validate_source_ids(child, sources)
    elif isinstance(value, list):
        for child in value:
            _validate_source_ids(child, sources)


def validate_snapshot(data: dict) -> dict:
    if data.get("schema_version") != 1:
        raise ValueError("Desteklenmeyen veri şeması")
    snapshot_date = date.fromisoformat(data["snapshot_date"])
    sources = data["sources"]
    if not sources:
        raise ValueError("Kaynak listesi boş olamaz")
    for source in sources.values():
        if not source["url"].startswith("https://"):
            raise ValueError("Kaynak HTTPS bağlantısı olmalı")
        if date.fromisoformat(source["accessed_on"]) > snapshot_date:
            raise ValueError("Kaynağa erişim tarihi veri kesitinden sonra olamaz")
    ids = set()
    for coach in data["coaches"]:
        if not coach["id"] or coach["id"] in ids:
            raise ValueError("Teknik direktör kimlikleri benzersiz olmalı")
        ids.add(coach["id"])
        if date.fromisoformat(coach["record_as_of"]) > snapshot_date:
            raise ValueError("Kayıt tarihi veri kesitinden sonra olamaz")
        if not coach["tenures"]:
            raise ValueError("Görev listesi boş olamaz")
        tenure_keys = set()
        for row in coach["tenures"]:
            Record.from_dict(row)
            start = date.fromisoformat(row["started_on"])
            end = date.fromisoformat(row["ended_on"]) if row["ended_on"] else None
            if start > snapshot_date or (end and (end < start or end > snapshot_date)):
                raise ValueError(f"Görev tarihleri geçersiz: {row['team']}")
            if row["kind"] not in {"club", "national", "reserve", "youth", "assistant"}:
                raise ValueError("Bilinmeyen görev kapsamı")
            key = row["team"], row["started_on"]
            if key in tenure_keys:
                raise ValueError("Aynı görev iki kez sayılamaz")
            tenure_keys.add(key)
        if set(coach["assessments"]) != set(SUBJECTIVE):
            raise ValueError("Dört öznel değerlendirme gerekli")
        for name, assessment in coach["assessments"].items():
            score = assessment["score"]
            if score is not None:
                finite_number(score, f"{coach['id']}.{name}", 1, 10)
            if assessment["confidence"] not in {"high", "medium", "low"}:
                raise ValueError("Geçersiz değerlendirme güveni")
            if not assessment["rationale"]:
                raise ValueError("Öznel puan gerekçesiz bırakılamaz")
            expected_status = "unrated" if score is None else "editorial"
            if assessment["status"] != expected_status:
                raise ValueError("Puan ve değerlendirme durumu tutarsız")
        unique_results = set()
        for result in coach["european_records"]:
            key = result["competition"], result["team"], result["season"]
            if key in unique_results:
                raise ValueError("Aynı Avrupa sezonu iki kez sayılamaz")
            unique_results.add(key)
    if len(ids) < 3:
        raise ValueError("Profil analizi için en az üç aday gerekli")
    _validate_source_ids(data["coaches"], sources)
    for check in data.get("source_checks", []):
        coach = next(c for c in data["coaches"] if c["id"] == check["coach_id"])
        if total_record(coach["tenures"]) != Record.from_dict(check["recomputed_all_rows"]):
            raise ValueError("Kaynak denetim toplamı güncel görevlerle uyuşmuyor")
        if check["source_id"] not in sources:
            raise ValueError("Kaynak denetim bağlantısı eksik")
    return data


def load_snapshot(path: Path) -> dict:
    return validate_snapshot(json.loads(path.read_text(encoding="utf-8")))


def validate_config(config: dict) -> dict:
    if set(config["weights"]) != set(CRITERIA):
        raise ValueError("Ağırlık anahtarları yedi kriterle aynı olmalı")
    for key, value in config["weights"].items():
        finite_number(value, f"weight.{key}", 0)
    if sum(config["weights"].values()) <= 0:
        raise ValueError("En az bir ağırlık pozitif olmalı")
    coefficients = config["europe_coefficients"]
    if set(coefficients) != {"UCL", "UEL", "UECL"}:
        raise ValueError("Üç Avrupa turnuva katsayısı gerekli")
    for key, value in coefficients.items():
        finite_number(value, key, 0, 1)
    if not coefficients["UCL"] > coefficients["UEL"] > coefficients["UECL"] > 0:
        raise ValueError("Katsayı sırası UCL > UEL > UECL > 0 olmalı")
    expected_stages = (
        "qualifying", "group", "knockout_playoff", "round_of_16",
        "quarter_final", "semi_final", "finalist", "winner",
    )
    if set(config["stage_points"]) != set(expected_stages):
        raise ValueError("Avrupa tur puanları eksik veya bilinmeyen tur var")
    stages = [finite_number(config["stage_points"][key], key, 0, 10) for key in expected_stages]
    if any(a >= b for a, b in zip(stages, stages[1:])):
        raise ValueError("Tur puanları başarı ilerledikçe artmalı")
    finite_number(config["europe_title_bonus"], "Kupa bonusu", 0)
    cap = config["europe_title_bonus_cap"]
    if type(cap) is not int or cap < 0:
        raise ValueError("Kupa bonus sınırı negatif olmayan tamsayı olmalı")
    finite_number(config["last_team_prior_matches"], "Önsel maç sayısı", 0)
    concentration = finite_number(config["weight_concentration"], "Dirichlet yoğunluğu", 0)
    if concentration == 0:
        raise ValueError("Dirichlet yoğunluğu pozitif olmalı")
    if set(config["subjective_half_width"]) != {"high", "medium", "low"}:
        raise ValueError("Üç öznel belirsizlik aralığı gerekli")
    for value in config["subjective_half_width"].values():
        finite_number(value, "Öznel puan yarı aralığı", 0, 9)
    if type(config["seed"]) is not int or config["seed"] < 0:
        raise ValueError("Seed negatif olmayan tamsayı olmalı")
    return config


def load_config(path: Path) -> dict:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))
