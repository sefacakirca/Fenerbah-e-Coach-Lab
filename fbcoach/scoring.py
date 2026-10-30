"""Veri -> yedi özellik -> açıklanabilir ağırlıklı karar puanı."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import CRITERIA, SUBJECTIVE, Record, total_record


@dataclass(frozen=True)
class Candidate:
    coach_id: str
    name: str
    values: tuple[float, ...]  # Her biri [0, 1]; sıra CRITERIA ile aynı.
    raw: dict
    assessments: dict
    missing: tuple[str, ...]
    warnings: tuple[str, ...]


def european_score(records: list[dict], config: dict) -> float:
    """En iyi ağırlıklı tur + en fazla iki kupaya bonus; sonuç 1–10."""
    strengths = []
    titles = 0
    for result in records:
        competition, stage = result["competition"], result["stage"]
        if competition not in config["europe_coefficients"] or stage not in config["stage_points"]:
            raise ValueError(f"Bilinmeyen Avrupa turnuvası/turu: {competition}/{stage}")
        strengths.append(config["europe_coefficients"][competition] * config["stage_points"][stage])
        titles += stage == "winner"
    best = max(strengths, default=0.0)
    bonus = min(titles, config["europe_title_bonus_cap"]) * config["europe_title_bonus"]
    return 1.0 + 0.9 * min(10.0, best + bonus)


def eligible_tenures(coach: dict, scope: str) -> list[dict]:
    if scope not in {"senior", "club"}:
        raise ValueError("Kapsam senior veya club olmalı")
    kinds = {"club", "national"} if scope == "senior" else {"club"}
    return sorted((row for row in coach["tenures"] if row["kind"] in kinds),
                  key=lambda row: row["started_on"])


def build_candidates(snapshot: dict, config: dict, scope="senior", last_team="last-played") -> list[Candidate]:
    if last_team not in {"last-played", "latest"}:
        raise ValueError("Son takım politikası last-played veya latest olmalı")
    result = []
    for coach in snapshot["coaches"]:
        tenures = eligible_tenures(coach, scope)
        if not tenures:
            raise ValueError(f"Kapsamda görev yok: {coach['name']}")
        career = total_record(tenures)
        if career.games == 0:
            raise ValueError(f"Kariyerinde maç kaydı yok: {coach['name']}")
        latest = tenures[-1]
        played = [row for row in tenures if row["games"] > 0]
        selected = played[-1] if last_team == "last-played" and played else latest
        last = Record.from_dict(selected)
        # Son görevi kariyer önselinden çıkar: aynı maçları önsele tekrar ekleme.
        prior_record = career - last
        prior_ppg = prior_record.ppg if prior_record.ppg is not None else 1.5
        strength = config["last_team_prior_matches"]
        adjusted = ((last.points + strength * prior_ppg) / (last.games + strength)
                    if last.games else None)
        europe = european_score(coach["european_records"], config)
        raw = {
            "coach_id": coach["id"], "name": coach["name"], "record_as_of": coach["record_as_of"],
            "scope": scope, "last_team_policy": last_team,
            "latest_appointment": latest["team"], "latest_appointment_games": latest["games"],
            "latest_appointment_ppg": Record.from_dict(latest).ppg,
            "evaluated_last_team": selected["team"], "last_team_games": last.games,
            "last_team_ppg": last.ppg, "last_team_ppg_model": adjusted,
            "career_games": career.games, "career_wins": career.wins,
            "career_draws": career.draws, "career_losses": career.losses,
            "career_ppg": career.ppg, "europe": europe,
        }
        missing = []
        warnings = []
        values = []
        for key in CRITERIA:
            if key in SUBJECTIVE:
                value = coach["assessments"][key]["score"]
                raw[key] = value
                normalized = (value - 1) / 9 if value is not None else 0.5
            elif key == "europe":
                value, normalized = europe, (europe - 1) / 9
            else:
                value = adjusted if key == "last_team_ppg" else career.ppg
                normalized = value / 3 if value is not None else 0.5
            if value is None:
                missing.append(key)
            if not 0 <= normalized <= 1:
                raise ValueError(f"Normalize özellik aralık dışı: {key}")
            values.append(normalized)
        if selected is not latest:
            warnings.append(f"Son görev {latest['team']} ({latest['games']} maç); son maçlı görev {selected['team']} kullanıldı.")
        if selected["kind"] == "national":
            warnings.append("Son görev millî takım; kulüp karşılaştırması için --scope club kullanılabilir.")
        if 0 < last.games < 20:
            warnings.append(f"Son görev yalnızca {last.games} maç; küçük örneklem.")
        if missing:
            warnings.append("Ölçülmeyen alanlara nötr değer atandı: " + ", ".join(missing))
        raw["missing_features"] = ",".join(missing)
        result.append(Candidate(coach["id"], coach["name"], tuple(values), raw,
                                coach["assessments"], tuple(missing), tuple(warnings)))
    return result


def weight_vector(config: dict) -> np.ndarray:
    weights = np.array([config["weights"][key] for key in CRITERIA], dtype=float)
    return weights / weights.sum()


def feature_matrix(candidates: list[Candidate]) -> np.ndarray:
    return np.asarray([candidate.values for candidate in candidates], dtype=float)


def rank_candidates(candidates: list[Candidate], config: dict) -> list[dict]:
    weights = weight_vector(config)
    contributions = feature_matrix(candidates) * weights * 100
    totals = contributions.sum(axis=1)
    rows = []
    for i, candidate in enumerate(candidates):
        tied = np.isclose(totals, totals[i], rtol=0, atol=1e-10)
        rank = 1 + int(((totals > totals[i]) & ~tied).sum())
        rows.append({"rank": rank, "coach_id": candidate.coach_id, "name": candidate.name,
                     "score": float(totals[i]),
                     **{f"contribution_{key}": float(contributions[i, j]) for j, key in enumerate(CRITERIA)}})
    return sorted(rows, key=lambda row: (-row["score"], row["coach_id"]))


def criterion_rankings(candidates: list[Candidate]) -> list[dict]:
    """Eksik editoryal puanlara başarı sırası atamaz; modeldeki nötr atamayı ayrıca gösterir."""
    rows = []
    for key in CRITERIA:
        observed = [c.raw[key] for c in candidates if c.raw[key] is not None]
        for candidate in candidates:
            value = candidate.raw[key]
            rank = None if value is None else 1 + sum(x > value for x in observed)
            rows.append({"criterion": key, "rank": rank, "coach_id": candidate.coach_id,
                         "name": candidate.name, "raw_value": value,
                         "model_unit_value": candidate.values[CRITERIA.index(key)],
                         "note": "nötr atama; gözlem yok" if value is None else
                         "sıralamada PPG ayarlanır" if key == "last_team_ppg" else ""})
    return rows
