"""python -m fbcoach.experiments: dört tercihi aynı veri üzerinde karşılaştır."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path

from .data import load_config, load_snapshot
from .reporting import write_csv
from .scoring import build_candidates, rank_candidates

ROOT = Path(__file__).resolve().parents[1]


def compare(snapshot: dict, config: dict) -> list[dict]:
    rows = {coach["id"]: {"coach_id": coach["id"], "name": coach["name"]} for coach in snapshot["coaches"]}
    cases = [
        ("baseline", "senior", "last-played", config["last_team_prior_matches"]),
        ("club", "club", "last-played", config["last_team_prior_matches"]),
        ("raw", "senior", "last-played", 0),
        ("latest", "senior", "latest", config["last_team_prior_matches"]),
    ]
    for label, scope, policy, prior in cases:
        effective = copy.deepcopy(config)
        effective["last_team_prior_matches"] = prior
        candidates = build_candidates(snapshot, effective, scope, policy)
        for result in rank_candidates(candidates, effective):
            rows[result["coach_id"]][f"{label}_score"] = result["score"]
            rows[result["coach_id"]][f"{label}_rank"] = result["rank"]
    return sorted(rows.values(), key=lambda row: row["baseline_rank"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/coaches.json")
    parser.add_argument("--config", type=Path, default=ROOT / "config/default.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/scenario_comparison.csv")
    args = parser.parse_args()
    rows = compare(load_snapshot(args.data), load_config(args.config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, rows)
    for row in rows:
        values = " | ".join(f"{case}: {row[f'{case}_score']:.2f} (#{row[f'{case}_rank']})"
                            for case in ("baseline", "club", "raw", "latest"))
        print(f"{row['name']}: {values}")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
