"""Karar puanı, ham veri, gerekçeler ve deney ayarlarını birlikte dışa aktarır."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .data import CRITERIA, LABELS, SUBJECTIVE
from .scoring import Candidate, criterion_rankings, weight_vector


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value, digits=2):
    return "—" if value is None else f"{value:.{digits}f}"


def _links(refs: list[str], sources: dict) -> str:
    return ", ".join(f"[{sources[key]['title']}]({sources[key]['url']})" for key in refs)


def render_report(snapshot, config, candidates, ranking, weight_sensitivity, rating_sensitivity, ml, metadata) -> str:
    weights = weight_vector(config)
    w_by_id = {row["coach_id"]: row for row in weight_sensitivity}
    r_by_id = {row["coach_id"]: row for row in rating_sensitivity}
    c_by_id = {c.coach_id: c for c in candidates}
    lines = [
        "# Fenerbahçe teknik direktör laboratuvarı — inceleme sürümü", "",
        f"Kaynaklara erişim: **{snapshot['snapshot_date']}**. Kapsam: `{metadata['scope']}`; son takım: `{metadata['last_team']}`.", "",
        "Bu rapor seçtiğimiz kriterlere göre karar desteği sağlar. Ağırlıklar ve editoryal puanlar gelecekteki başarıdan öğrenilmedi. K-Means yalnızca aday profillerini gruplar.", "",
        "## Ham veriler ve 1–10 değerlendirmeleri", "",
        "PPG = (3 × galibiyet + beraberlik) / maç. Kupa maçlarında analitik puan eşdeğeridir. Kaynakların penaltı sınıflandırması tamamen uyumlaştırılmadı.", "",
        "| Aday | Son maçlı/seçilen takım | Maç | Son PPG | Kariyer PPG | İletişim | Uyum | Büyük kulüp | Yerel derbi | Avrupa |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in candidates:
        raw = c.raw
        fields = [c.name, raw["evaluated_last_team"], str(raw["last_team_games"])]
        fields += [fmt(raw[key]) for key in CRITERIA]
        lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "**— = puanlanmadı.** Özellikle derbi dökümleri eksiktir. Model, eksik 1–10 puanına nötr 5.5 atar; bunu gözlem veya başarı puanı saymaz.", "",
              "## Varsayılan sıralama", "",
              "| Sıra | Aday | Karar puanı /100 | Ağırlık senaryolarında birincilik | Ağırlık + puan senaryolarında birincilik |",
              "|---:|---|---:|---:|---:|"]
    for row in ranking:
        key = row["coach_id"]
        lines.append(f"| {row['rank']} | {row['name']} | {row['score']:.2f} | {w_by_id[key]['scenario_first_share']:.1%} | {r_by_id[key]['scenario_first_share']:.1%} |")
    lines += ["", "Birincilik payları yalnızca tanımlanan varsayım senaryolarındaki sıralama sıklığıdır; işe alındığında başarılı olma olasılığı değildir. Puan aralıkları istatistiksel güven aralığı değildir.", "",
              "## Hesaplama ve ayarlar", "",
              "| Kriter | Ağırlık |", "|---|---:|"]
    lines += [f"| {LABELS[key]} | {weights[i]:.0%} |" for i, key in enumerate(CRITERIA)]
    lines += ["", "PPG 0–3 aralığından, editoryal/Avrupa puanları 1–10 aralığından [0,1]'e çevrilir. Karar puanı = 100 × Σ(ağırlık × normalize özellik). Adaylara göre min–max ölçeği kullanılmaz.", "",
              f"Son takım için önsel güç: **{config['last_team_prior_matches']:g} maç**. Önsel PPG, seçilen son görev çıkarıldıktan sonraki kariyerden hesaplanır. Ayarlanmış PPG = (son görev puanı + önsel güç × önceki kariyer PPG) / (son görev maçı + önsel güç). Önceki görev yoksa nötr 1.5 kullanılır. Sıfır maçta ham PPG tanımsız kalır.", "",
              "| Aday | Ham son PPG | Sıralamada kullanılan PPG | Kariyer maçı | Kayıt tarihi |",
              "|---|---:|---:|---:|---|"]
    for c in candidates:
        lines.append(f"| {c.name} | {fmt(c.raw['last_team_ppg'])} | {fmt(c.raw['last_team_ppg_model'])} | {c.raw['career_games']} | {c.raw['record_as_of']} |")
    lines += ["", "### Avrupa puanı", "",
              "Katsayılar: " + ", ".join(f"{key}={value:g}" for key, value in config["europe_coefficients"].items()) + ". Bunlar proje tercihidir, UEFA ülke katsayısı değildir.", "",
              "Tur puanları: " + ", ".join(f"{key}={value:g}" for key, value in config["stage_points"].items()) + ".", "",
              f"Avrupa = 1 + 0.9 × min(10, en yüksek [turnuva katsayısı × tur puanı] + {config['europe_title_bonus']:g} × min(kazanılan kupa, {config['europe_title_bonus_cap']})).",
              "", "En güçlü doğrulanmış ilerleme ve kupalar kullanılır; bu bir Avrupa maç kazanma oranı değildir. Millî takım turnuvaları dahil değildir. Sezonlar arası turnuva değişimlerinin tamamı ve rakip gücü modellenmedi.", "",
              "### ML ve duyarlılık", "",
              f"K-Means: **k={ml['k']}**; silhouette={fmt(ml['silhouette'], 3)}. k=2–4 denenir, tek kişilik kümeler elenir. Uygun ayrım yoksa k=1 kalır. StandardScaler ve PCA yalnızca profil analizi içindir; sıralama küme numarasını kullanmaz.", "",
              f"PCA ilk iki bileşenin açıkladığı varyans: {sum(ml['pca_explained_variance_ratio']):.1%}. Bu bir tahmin doğruluğu değildir.", "",
              f"Her analizde {metadata['simulations']:,} senaryo, seed={config['seed']}. Ağırlıklar Dirichlet dağılımından çekilir (yoğunluk={config['weight_concentration']:g}); sıfır ağırlıklar sıfır kalır. İkinci analizde editoryal puanlar güven düzeyine göre üçgensel dağılımla, puanlanmamış alanlar 1–10'da tekdüze dağılımla değişir. PPG örnekleme hatası bu analizde modellenmez.", "",
              "## Adayların gerekçeleri ve kaynakları", ""]
    for coach in snapshot["coaches"]:
        c = c_by_id[coach["id"]]
        lines += [f"### {coach['name']}", ""]
        tenure_refs = sorted({ref for row in coach["tenures"] for ref in row["source_ids"]})
        lines += ["Maç kayıtları: " + _links(tenure_refs, snapshot["sources"]), ""]
        for key in SUBJECTIVE:
            a = coach["assessments"][key]
            lines += [f"- **{LABELS[key]}: {fmt(a['score'])}/10** — {a['rationale']} Editoryal güven: `{a['confidence']}`. " + _links(a["source_ids"], snapshot["sources"])]
        lines.append("")
        for event in coach["european_records"]:
            lines += [f"- Avrupa kanıtı: {event['season']} {event['team']}, {event['competition']} / {event['stage']}. " + _links(event["source_ids"], snapshot["sources"])]
        lines.append("")
        lines += [f"- {note}" for note in (*coach["notes"], *c.warnings)]
        lines.append("")
    lines += ["## Yorumlama sınırları", "",
              "Sekiz aday, teknik direktör başarı tahmini için yeterli etiketli eğitim verisi değildir. İletişim ve uyum puanları saha içi/saha dışı psikometrik ölçüm değildir; gerekçeli proje varsayımlarıdır. Derbi örnekleri seçilmiş kanıtlardır, kariyerin tam maç listesi değildir. Büyük kulüp kriteri ve Avrupa kriteri kısmen aynı başarıları ödüllendirebilir; son takım PPG ile kariyer PPG de ilişkilidir.", "",
              "Lig zorluğu, kadro/bütçe, fikstür, görev süresi, maaş, sözleşme, müsaitlik ve güncel Fenerbahçe kadrosuna oyuncu bazında uyum modellenmedi. Ülke/lig ve millî takım maçları tam eşdeğer değildir. Kaynaklara bugün erişilmiş olması bütün kayıtların bugüne kadar tam olduğu anlamına gelmez.", "",
              "Sonraki araştırma: tam maç listeleriyle tek penaltı kuralı, tam yerel derbi dökümü ve daha büyük teknik direktör-sezon verisi toplamak. Gerçek bir hedef tanımlanırsa zaman bazlı doğrulamayla denetimli ML eklenebilir.", "",
              "README ve GitHub yayını, kod incelemesinden sonraki aşamadır.", ""]
    return "\n".join(lines)


def export_results(output, snapshot, config, candidates, ranking, weight_sensitivity, rating_sensitivity, ml, metadata):
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "features.csv", [c.raw for c in candidates])
    write_csv(output / "ranking.csv", ranking)
    write_csv(output / "criterion_rankings.csv", criterion_rankings(candidates))
    write_csv(output / "sensitivity_weights.csv", weight_sensitivity)
    write_csv(output / "sensitivity_ratings.csv", rating_sensitivity)
    write_csv(output / "ml_profiles.csv", ml["profiles"])
    write_json(output / "ml_diagnostics.json", ml)
    write_json(output / "run_metadata.json", metadata)
    write_json(output / "effective_config.json", config)
    warnings = [{"coach_id": c.coach_id, "warnings": c.warnings} for c in candidates]
    write_json(output / "data_warnings.json", warnings)
    report = render_report(snapshot, config, candidates, ranking, weight_sensitivity, rating_sensitivity, ml, metadata)
    (output / "report.md").write_text(report, encoding="utf-8")
