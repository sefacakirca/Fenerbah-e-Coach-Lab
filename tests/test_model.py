"""Karar mantığı, veri hataları ve anlamlı sınır durumları için regresyon testleri."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from fbcoach.cli import main
from fbcoach.data import CRITERIA, Record, load_config, load_snapshot, total_record, validate_config, validate_snapshot
from fbcoach.ml import profile_candidates
from fbcoach.scoring import Candidate, build_candidates, european_score, rank_candidates
from fbcoach.sensitivity import simulate

ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = load_snapshot(ROOT / "data/coaches.json")
        cls.config = load_config(ROOT / "config/default.json")

    def candidates(self, **kwargs):
        return build_candidates(self.snapshot, self.config, **kwargs)

    def candidate(self, key, **kwargs):
        return next(c for c in self.candidates(**kwargs) if c.coach_id == key)

    def test_ppg_is_weighted_by_matches(self):
        # 1 maçta 3, 9 maçta 0 puan: görev PPG'lerinin ortalaması 1.5 olmaz.
        record = Record(1, 1, 0, 0) + Record(9, 0, 0, 9)
        self.assertAlmostEqual(record.ppg, 0.3)

    def test_no_match_is_missing_not_zero_success(self):
        self.assertIsNone(Record(0, 0, 0, 0).ppg)
        c = self.candidate("kuyt", last_team="latest")
        self.assertIsNone(c.raw["last_team_ppg"])
        self.assertIn("last_team_ppg", c.missing)
        self.assertEqual(c.values[0], 0.5)

    def test_last_played_policy_is_explicit(self):
        c = self.candidate("kuyt")
        self.assertEqual(c.raw["latest_appointment"], "Fenerbahçe")
        self.assertEqual(c.raw["evaluated_last_team"], "FC Dordrecht")
        self.assertAlmostEqual(c.raw["last_team_ppg"], 47 / 39)
        self.assertTrue(c.warnings)

    def test_club_scope_removes_national_team(self):
        c = self.candidate("nagelsmann", scope="club")
        self.assertEqual(c.raw["evaluated_last_team"], "Bayern Münih")
        self.assertEqual(c.raw["career_games"], 315)
        self.assertEqual(self.candidate("montella", scope="club").raw["evaluated_last_team"], "Adana Demirspor")

    def test_reserve_teams_excluded(self):
        c = self.candidate("mendilibar")
        self.assertEqual(c.raw["career_games"], 1104 - 82 - 38 - 38)

    def test_small_sample_smoothing_leaves_last_out(self):
        c = self.candidate("tedesco")
        self.assertAlmostEqual(c.raw["last_team_ppg"], 0.25)
        prior_ppg = (3 * 124 + 56) / 247
        expected = (1 + 20 * prior_ppg) / 24
        self.assertAlmostEqual(c.raw["last_team_ppg_model"], expected)
        self.assertGreater(c.raw["last_team_ppg_model"], 0.25)

    def test_zero_prior_restores_raw_ppg(self):
        config = copy.deepcopy(self.config)
        config["last_team_prior_matches"] = 0
        for c in build_candidates(self.snapshot, config):
            self.assertEqual(c.raw["last_team_ppg"], c.raw["last_team_ppg_model"])

    def test_unknown_derby_is_explicit_neutral(self):
        c = self.candidate("nagelsmann")
        self.assertIsNone(c.raw["derby"])
        self.assertIn("derby", c.missing)
        self.assertEqual(c.values[CRITERIA.index("derby")], 0.5)

    def test_contribution_sum_explains_total(self):
        for row in rank_candidates(self.candidates(), self.config):
            self.assertAlmostEqual(sum(row[f"contribution_{key}"] for key in CRITERIA), row["score"])
            self.assertTrue(0 <= row["score"] <= 100)

    def test_weight_scale_does_not_change_result(self):
        config = copy.deepcopy(self.config)
        config["weights"] = {key: value * 100 for key, value in config["weights"].items()}
        before = rank_candidates(self.candidates(), self.config)
        after = rank_candidates(self.candidates(), config)
        np.testing.assert_allclose([r["score"] for r in before], [r["score"] for r in after])

    def test_adding_weak_candidate_does_not_rescale_other_scores(self):
        candidates = self.candidates()
        before = {r["coach_id"]: r["score"] for r in rank_candidates(candidates, self.config)}
        weak = Candidate("weak", "Weak", (0,) * 7, {}, {}, (), ())
        after = {r["coach_id"]: r["score"] for r in rank_candidates(candidates + [weak], self.config)}
        for key in before:
            self.assertEqual(before[key], after[key])

    def test_europe_coefficients_have_expected_order(self):
        scores = [european_score([{"competition": comp, "stage": "semi_final"}], self.config)
                  for comp in ("UCL", "UEL", "UECL")]
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[1], scores[2])

    def test_europe_titles_and_no_appearance(self):
        self.assertEqual(european_score([], self.config), 1)
        self.assertAlmostEqual(self.candidate("mendilibar").raw["europe"], 9.1)
        self.assertLessEqual(european_score([{"competition": "UCL", "stage": "winner"}], self.config), 10)

    def test_sensitivity_reproducible_and_shares_sum_to_one(self):
        first = simulate(self.candidates(), self.config, 500, vary_ratings=True)
        second = simulate(self.candidates(), self.config, 500, vary_ratings=True)
        self.assertEqual(first, second)
        self.assertAlmostEqual(sum(r["scenario_first_share"] for r in first), 1)

    def test_tied_candidates_share_first_place(self):
        original = self.candidates()[0]
        clones = [Candidate(str(i), str(i), original.values, original.raw,
                            original.assessments, (), ()) for i in range(3)]
        rows = simulate(clones, self.config, 100)
        for row in rows:
            self.assertAlmostEqual(row["scenario_first_share"], 1 / 3)
            self.assertEqual(row["mean_rank"], 2)
        self.assertEqual([r["rank"] for r in rank_candidates(clones, self.config)], [1, 1, 1])

    def test_zero_weight_keeps_criterion_inactive_in_sensitivity(self):
        config = copy.deepcopy(self.config)
        config["weights"] = {key: float(key == "career_ppg") for key in CRITERIA}
        expected = rank_candidates(self.candidates(), config)[0]["coach_id"]
        rows = simulate(self.candidates(), config, 100, vary_ratings=True)
        self.assertEqual(rows[0]["coach_id"], expected)
        self.assertEqual(rows[0]["scenario_first_share"], 1)

    def test_kmeans_recovers_clear_synthetic_profiles(self):
        points = [0.05, 0.06, 0.07, 0.08, 0.90, 0.91, 0.92, 0.93]
        candidates = [Candidate(str(i), str(i), (value,) * 7, {}, {}, (), ()) for i, value in enumerate(points)]
        model = profile_candidates(candidates)
        labels = [row["cluster"] for row in model["profiles"]]
        self.assertEqual(model["k"], 2)
        self.assertEqual(len(set(labels[:4])), 1)
        self.assertEqual(len(set(labels[4:])), 1)
        self.assertNotEqual(labels[0], labels[-1])

    def test_identical_profiles_have_no_invented_clusters(self):
        candidates = [Candidate(str(i), str(i), (0.5,) * 7, {}, {}, (), ()) for i in range(4)]
        model = profile_candidates(candidates)
        self.assertEqual(model["k"], 1)
        self.assertIsNone(model["silhouette"])
        self.assertEqual(model["pca_explained_variance_ratio"], [0, 0])

    def test_curated_wdl_appear_in_saved_source_tables(self):
        for coach in self.snapshot["coaches"]:
            tables = json.loads((ROOT / "data/source_snapshots" / f"{coach['id']}.json").read_text(encoding="utf-8"))
            for tenure in coach["tenures"]:
                if f"wiki_{coach['id']}" not in tenure["source_ids"]:
                    continue
                expected = [str(value) for value in Record.from_dict(tenure).values()]
                matches = [row for row in tables["rows"]
                           if any(row[i:i + 4] == expected for i in range(len(row) - 3))]
                self.assertTrue(matches, (coach["id"], tenure["team"], expected))

    def test_end_to_end_exports_reproducible_artifacts(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for path in (first, second):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(["--output", path, "--simulations", "100"]), 0)
            for filename in ("features.csv", "ranking.csv", "report.md", "ml_diagnostics.json", "run_metadata.json"):
                self.assertEqual((Path(first) / filename).read_bytes(), (Path(second) / filename).read_bytes())


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((ROOT / "data/coaches.json").read_text(encoding="utf-8"))
        self.config = load_config(ROOT / "config/default.json")

    def test_inconsistent_wdl_rejected(self):
        with self.assertRaises(ValueError):
            Record(10, 5, 3, 3)

    def test_negative_and_boolean_counts_rejected(self):
        for values in [(-1, -1, 0, 0), (1, True, 0, 0)]:
            with self.assertRaises(ValueError):
                Record(*values)

    def test_nan_editorial_score_rejected(self):
        self.snapshot["coaches"][0]["assessments"]["communication"]["score"] = float("nan")
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_out_of_scale_editorial_score_rejected(self):
        self.snapshot["coaches"][0]["assessments"]["style_fit"]["score"] = 11
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_unknown_source_rejected(self):
        self.snapshot["coaches"][0]["tenures"][0]["source_ids"] = ["invented"]
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_duplicate_tenure_rejected(self):
        self.snapshot["coaches"][0]["tenures"].append(self.snapshot["coaches"][0]["tenures"][0])
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_duplicate_european_season_rejected(self):
        coach = self.snapshot["coaches"][0]
        coach["european_records"].append(coach["european_records"][0])
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_negative_weight_rejected(self):
        self.config["weights"]["career_ppg"] = -1
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_all_zero_weights_rejected(self):
        self.config["weights"] = dict.fromkeys(CRITERIA, 0)
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_bad_europe_coefficient_order_rejected(self):
        self.config["europe_coefficients"]["UECL"] = 1
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_nan_prior_rejected(self):
        self.config["last_team_prior_matches"] = float("nan")
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_future_record_rejected(self):
        self.snapshot["coaches"][0]["record_as_of"] = "2030-01-01"
        with self.assertRaises(ValueError):
            validate_snapshot(self.snapshot)

    def test_cli_invalid_config_fails_without_output(self):
        with tempfile.TemporaryDirectory() as path:
            output = Path(path) / "results"
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["--output", str(output), "--prior-matches", "-1"])
            self.assertEqual(code, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
