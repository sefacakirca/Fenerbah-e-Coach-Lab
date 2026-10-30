"""Varsayım duyarlılığı; birincilik payı gerçek hayattaki başarı olasılığı değildir."""
from __future__ import annotations

import numpy as np

from .data import CRITERIA, SUBJECTIVE
from .scoring import Candidate, feature_matrix, weight_vector


def simulate(candidates: list[Candidate], config: dict, simulations=10_000, vary_ratings=False) -> list[dict]:
    if type(simulations) is not int or simulations < 1:
        raise ValueError("Simülasyon sayısı pozitif tamsayı olmalı")
    rng = np.random.default_rng(config["seed"])
    base = weight_vector(config)
    active = base > 0
    weights = np.zeros((simulations, len(CRITERIA)))
    weights[:, active] = rng.dirichlet(base[active] * config["weight_concentration"], size=simulations)
    features = np.broadcast_to(feature_matrix(candidates), (simulations, len(candidates), len(CRITERIA))).copy()
    if vary_ratings:
        for i, candidate in enumerate(candidates):
            for key in SUBJECTIVE:
                j = CRITERIA.index(key)
                assessment = candidate.assessments[key]
                if assessment["score"] is None:
                    features[:, i, j] = rng.uniform(0, 1, size=simulations)
                else:
                    mode = candidate.values[j]
                    width = config["subjective_half_width"][assessment["confidence"]] / 9
                    left, right = max(0.0, mode - width), min(1.0, mode + width)
                    if left < right:
                        features[:, i, j] = rng.triangular(left, mode, right, size=simulations)
    scores = np.einsum("snf,sf->sn", features, weights) * 100
    maximum = scores.max(axis=1, keepdims=True)
    # Tam eşitlikte her adaya eşit birincilik payı; ilk satırı kayırma yok.
    tied_first = np.isclose(scores, maximum, rtol=0, atol=1e-10)
    first_shares = tied_first / tied_first.sum(axis=1, keepdims=True)
    ties = np.isclose(scores[:, :, None], scores[:, None, :], rtol=0, atol=1e-10)
    greater = (scores[:, None, :] > scores[:, :, None]) & ~ties
    ranks = 1 + greater.sum(axis=2) + (ties.sum(axis=2) - 1) / 2
    rows = []
    for i, candidate in enumerate(candidates):
        rows.append({"coach_id": candidate.coach_id, "name": candidate.name,
                     "scenario_first_share": float(first_shares[:, i].mean()),
                     "mean_rank": float(ranks[:, i].mean()),
                     "rank_p10": float(np.quantile(ranks[:, i], 0.10)),
                     "rank_p90": float(np.quantile(ranks[:, i], 0.90)),
                     "score_p10": float(np.quantile(scores[:, i], 0.10)),
                     "score_p90": float(np.quantile(scores[:, i], 0.90)),
                     "simulations": simulations, "vary_ratings": vary_ratings})
    return sorted(rows, key=lambda row: (-row["scenario_first_share"], row["mean_rank"], row["coach_id"]))
