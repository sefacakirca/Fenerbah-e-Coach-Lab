from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import sklearn

from .data import load_config, load_snapshot, validate_config
from .ml import profile_candidates
from .reporting import export_results
from .scoring import build_candidates, rank_candidates
from .sensitivity import simulate

ROOT = Path(__file__).resolve().parents[1]


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Pozitif tamsayı gerekli")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fenerbahçe teknik direktör adayları: karar desteği ve keşifsel ML")
    parser.add_argument("--data", type=Path, default=ROOT / "data/coaches.json")
    parser.add_argument("--config", type=Path, default=ROOT / "config/default.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--scope", choices=("senior", "club"), default="senior",
                        help="senior: A takım kulüp + millî takım; club: yalnızca kulüp")
    parser.add_argument("--last-team", choices=("last-played", "latest"), default="last-played",
                        help="Son maç yönetilen görev veya sıfır maç olsa da en yeni görev")
    parser.add_argument("--prior-matches", type=float, help="Son görev için önsel güç; 0 ham PPG kullanır")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--simulations", type=positive_int, default=10_000)
    args = parser.parse_args(argv)
    try:
        snapshot = load_snapshot(args.data)
        config = load_config(args.config)
        if args.prior_matches is not None:
            config["last_team_prior_matches"] = args.prior_matches
        if args.seed is not None:
            config["seed"] = args.seed
        validate_config(config)
        candidates = build_candidates(snapshot, config, args.scope, args.last_team)
        ranking = rank_candidates(candidates, config)
        ml = profile_candidates(candidates, config["seed"])
        weight_sensitivity = simulate(candidates, config, args.simulations)
        rating_sensitivity = simulate(candidates, config, args.simulations, vary_ratings=True)
        metadata = {
            "snapshot_date": snapshot["snapshot_date"],
            "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
            "effective_config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            "scope": args.scope, "last_team": args.last_team, "simulations": args.simulations,
            "python": sys.version.split()[0], "numpy": np.__version__, "scikit_learn": sklearn.__version__,
        }
        export_results(args.output, snapshot, config, candidates, ranking, weight_sensitivity,
                       rating_sensitivity, ml, metadata)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Hata: {error}", file=sys.stderr)
        return 2
    print(f"Veri kesiti: {snapshot['snapshot_date']} | kapsam: {args.scope} | politika: {args.last_team}")
    print("\nSıra  Aday                       Karar puanı /100")
    for row in ranking:
        print(f"{row['rank']:>4}  {row['name']:<26} {row['score']:>8.2f}")
    print(f"\nKeşifsel ML: K-Means k={ml['k']}; küme numarası başarı sırası değildir.")
    print("Senaryo birincilik payları başarı olasılığı değildir.")
    for c in candidates:
        for warning in c.warnings:
            print(f"Veri notu — {c.name}: {warning}")
    print(f"\nRapor: {(args.output / 'report.md').resolve()}")
    return 0
