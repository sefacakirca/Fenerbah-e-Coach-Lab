# Fenerbahçe Coach Lab ⚽

**Veriden tartışılabilir bir teknik direktör tercihine.**  
**From football data to a coaching decision you can explain.**

Python ile sekiz teknik direktörü karşılaştıran; kaynaklı istatistikleri, gerekçeli değerlendirmeleri ve keşifsel makine öğrenmesini bir araya getiren futbol analitiği projesi.

A Python football analytics project combining sourced statistics, documented assessments and exploratory machine learning to compare eight head coaches.

**Python 3.11+ · NumPy · scikit-learn · K-Means · PCA · Sensitivity analysis**

[Türkçe](#turkce) · [English](#english) · [Sonuç raporu / Results](results/report.md) · [Model ayarları / Configuration](config/default.json)

---

<a id="turkce"></a>

## Türkçe

### Proje ne yapıyor?

Fenerbahçe için teknik direktör seçimini yedi kriter üzerinden inceleyen, ağırlıkları ve puan gerekçeleri açık bir karar destek modeli sunuyor. Her adayın toplam puanını hangi kriterlerin oluşturduğunu görebilir, tercihleri değiştirerek sıralamayı yeniden üretebilirsiniz.

Karar puanı ağırlıklı bir değerlendirmedir. ML tarafında K-Means benzer aday profillerini gruplar; PCA bu profilleri iki boyutta incelemek için koordinatlar üretir. Etiketli bir gelecek başarı veri seti kullanılmadığı için modelin çıktısı şampiyonluk ya da işe alım başarısı olasılığı olarak yorumlanamaz.

### Adaylar

Abdullah Avcı · Antonio Conte · Julian Nagelsmann · José Luis Mendilibar · Domenico Tedesco · Emre Belözoğlu · Vincenzo Montella · Dirk Kuyt

### Değerlendirme kriterleri

| Kriter | Veri / değerlendirme | Varsayılan ağırlık |
|---|---|---:|
| Son takımda maç başına puan | Galibiyet, beraberlik ve maç sayısından hesaplanır | %15 |
| Kariyerde maç başına puan | Kapsamdaki görevlerin maç ağırlıklı toplamı | %20 |
| Oyuncularla iletişim | Gerekçeli, düzenlenebilir 1–10 değerlendirmesi | %10 |
| Oyun tarzının Fenerbahçe'ye uyumu | Tanımlanan hedef profile göre 1–10 değerlendirmesi | %20 |
| Büyük kulüplerde başarı | Başantrenörlükteki başarı geçmişine göre 1–10 değerlendirmesi | %10 |
| Yerel derbilerde başarı | Toplanan kanıtlara dayalı 1–10 değerlendirmesi | %10 |
| Avrupa kupalarında başarı | Turnuva, ulaşılan tur ve kupa bonusundan türetilir | %15 |

İletişim ve oyun uyumu puanları doğrudan ölçülmüş oyuncu memnuniyeti veya taktik performans verisi değildir. Puanların gerekçeleri ve kaynakları [veri dosyasında](data/coaches.json) ve [ayrıntılı raporda](results/report.md) bulunur.

### Hızlı başlangıç

Python 3.11 veya üzerini kullanın. Komutları proje klasöründe çalıştırın; sanal ortamı etkinleştirmek gerekmez.

**Windows / PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe main.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python main.py
```

Sonuçlar `results/` klasörüne yazılır. İlk olarak [results/report.md](results/report.md) dosyasını açın. Paket kurulumu internet kullanır; sabitlenmiş veriyle model çalıştırmak için internet gerekmez.

`requirements-lock.txt` doğrulanan bütün paket sürümlerini, `requirements.txt` doğrudan bağımlılıkları içerir.

### Model nasıl hesaplıyor?

```text
Ham PPG = (3 × galibiyet + beraberlik) / maç

Ayarlanmış son takım PPG =
    (son görev puanı + önsel maç sayısı × önceki kariyer PPG)
    / (son görev maçı + önsel maç sayısı)

Karar puanı = 100 × Σ(ağırlık × normalize kriter)
```

PPG değerleri 0–3, değerlendirmeler 1–10 aralığından `[0, 1]` aralığına çevrilir. Adaylara bağlı min–max normalizasyonu kullanılmaz. Böylece yeni bir aday eklemek mevcut adayların puan ölçeğini değiştirmez.

Son görev için varsayılan önsel güç **20 maçtır**; önceki kariyer hesaplanırken seçilen son görevin maçları çıkarılır. Bu tercih küçük örneklemlerin etkisini azaltır. Ham PPG her zaman ayrı saklanır; `--prior-matches 0` düzeltmeyi kapatır.

Avrupa katsayıları **Şampiyonlar Ligi = 1.0**, **Avrupa Ligi = 0.8**, **Konferans Ligi = 0.6** olarak tanımlanır. Bunlar projenin tercihleridir. Tur puanları ve bonuslar [config/default.json](config/default.json) içindedir:

```text
Avrupa puanı = 1 + 0.9 × min(
    10,
    en iyi [turnuva katsayısı × tur puanı] + 0.5 × min(kupa sayısı, 2)
)
```

### İlk veri kesitinin sonuçları

**Kaynaklara erişim: 30 Ekim 2026.** Aşağıdaki tablo `senior`, `last-played` ve 20 maçlık önsel ile üretilmiştir. Her adayın kayıt güncelliği ayrıca saklanır; bu tablo canlı sıralama değildir.

| Sıra | Teknik direktör | Karar puanı /100 |
|---:|---|---:|
| 1 | Julian Nagelsmann | 72.80 |
| 2 | Antonio Conte | 70.44 |
| 3 | José Luis Mendilibar | 70.41 |
| 4 | Vincenzo Montella | 60.76 |
| 5 | Domenico Tedesco | 60.64 |
| 6 | Abdullah Avcı | 52.80 |
| 7 | Emre Belözoğlu | 49.73 |
| 8 | Dirk Kuyt | 35.87 |

Ham PPG kullanıldığında Conte ve Mendilibar yer değiştirir. [Senaryo karşılaştırması](results/scenario_comparison.csv), sonucun tercihlerimize ne kadar bağlı olduğunu gösterir.

### Farklı varsayımları dene

Aşağıdaki PowerShell komutlarında macOS/Linux için Python yolunu `.venv/bin/python` olarak değiştirin.

```powershell
# Yalnızca kulüp kariyerini değerlendir
.\.venv\Scripts\python.exe main.py --scope club --output results/club

# Son takımda ham PPG kullan
.\.venv\Scripts\python.exe main.py --prior-matches 0 --output results/raw

# Sıfır maçlı olsa da en yeni görevi seç
.\.venv\Scripts\python.exe main.py --last-team latest --output results/latest

# Dört model tercihinin puanlarını ve sıralarını karşılaştır
.\.venv\Scripts\python.exe -m fbcoach.experiments

# Komut satırı seçeneklerini görüntüle
.\.venv\Scripts\python.exe main.py --help
```

Ağırlıkları ve Avrupa katsayılarını [config/default.json](config/default.json) üzerinden düzenleyebilirsiniz. Ağırlıkların toplamı otomatik olarak 1'e ölçeklenir. Öznel puanları değiştirirken [data/coaches.json](data/coaches.json) içindeki gerekçeleri de güncelleyin.

### ML ve belirsizlik analizi

- **K-Means:** standartlaştırılmış yedi özelliğe uygulanır. `k=2–4` denenir; tek kişilik kümeler elenir ve kalanlar arasında en yüksek silhouette seçilir. Uygun aday kalmazsa tek küme kullanılır.
- **PCA:** iki boyutlu profil koordinatları ve açıklanan varyansı üretir. Küme numarası başarı sırası, açıklanan varyans tahmin doğruluğu değildir.
- **Duyarlılık analizi:** varsayılan olarak her biri 10.000 senaryodan oluşan iki analiz çalışır. İlkinde ağırlıklar; ikincisinde ağırlıklarla birlikte editoryal puanlar değişir. Varsayılan seed `42`'dir.

`scenario_first_share`, tanımlanan senaryolarda birinci çıkma payıdır. Gelecekte başarılı olma olasılığı değildir; simülasyon yüzdelikleri istatistiksel güven aralığı olarak yorumlanmamalıdır.

### Veriler ve kapsam

İstatistikler Wikipedia görev tablolarından; Avrupa ve derbi kanıtları UEFA, federasyon, kulüp sayfaları ve ilgili haber/röportajlardan derlenmiştir. Kaynak bağlantıları, erişim tarihleri, notlar ve gerekçeler [data/coaches.json](data/coaches.json) içindedir. İndirilen tablo hücreleri [data/source_snapshots/](data/source_snapshots/) altında saklanır.

`senior` kulüp ve A millî takım başantrenörlüğünü, `club` yalnızca kulüp görevlerini kapsar. Alt lig A takım görevleri dahildir; genç, rezerv/feeder ve yardımcı antrenörlük görevleri dışarıda tutulur.

Kaynakları yeniden indirmek için:

```powershell
.\.venv\Scripts\python.exe tools/collect_sources.py --output work/source-review
```

Bu komut inceleme dosyaları oluşturur; ana veri setini güncellemez. Görevleri, kapsamı ve maç sayısı farklılıklarını inceleyerek aktarın.

### Sonuçları yorumlarken

- Sekiz aday ve editoryal girdiler keşifsel karşılaştırma için kullanılır. Denetimli başarı modeli eğitilmemiştir.
- Nagelsmann, Emre ve Kuyt için yeterli yerel derbi kaydı toplanmadı. Ham değer `null`, modelde kullanılan nötr puan **5.5**'tir.
- Veri kesitinde Kuyt'ın Fenerbahçe görevi sıfır maçtır. `last-played` Dordrecht'i seçer; `latest` politikasında tanımsız PPG modelde nötr **1.5** ile temsil edilir.
- Lig gücü, kadro/bütçe, fikstür, maaş, sözleşme, müsaitlik ve güncel kadroya oyuncu bazında uyum modellenmez. Penaltı serilerinin kaynaklardaki sınıflandırması tamamen uyumlaştırılmamıştır.
- Son takım/kariyer PPG ile büyük kulüp/Avrupa başarısı birbiriyle ilişkilidir; aynı başarı birden fazla kriteri etkileyebilir.

Varsayımların ayrıntıları: [METODOLOJI.md](docs/METODOLOJI.md). Ek kullanım açıklamaları: [CALISTIRMA.md](docs/CALISTIRMA.md). Bu iki belge ve üretilen ayrıntılı raporlar Türkçedir.

### Testler ve geliştirme

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

İlk sürümde **33 test** Windows/Python 3.11.9 ile geçti. Testler maç kayıtlarını, kapsam filtrelerini, eksik veriyi, puan katkılarını, simülasyonları, ML sınır durumlarını ve çıktıların tekrar üretilebilirliğini denetler. [GitHub Actions](.github/workflows/tests.yml) Python 3.11 ve 3.12 için yapılandırılmıştır; yerel doğrulama kaydı [verification.txt](results/verification.txt) içindedir.

Sonraki araştırma adımları: tam derbi dökümleri, maç bazında ortak sonuç kuralı ve gerçek bir hedefle daha büyük teknik direktör–sezon veri seti. Böyle bir veri setinde zaman bazlı doğrulama ile denetimli ML karşılaştırılabilir.

---

<a id="english"></a>

## English

### What does this project do?

Fenerbahçe Coach Lab compares eight head coaches using seven criteria, explicit weights and documented reasoning. You can inspect each criterion's contribution, change the assumptions and reproduce the ranking.

The decision score is a weighted assessment. K-Means groups similar candidate profiles, while PCA provides coordinates for exploring them in two dimensions. No labelled future-success dataset is used, so the output cannot be interpreted as a probability of winning a title or succeeding after appointment.

### Candidates

Abdullah Avcı · Antonio Conte · Julian Nagelsmann · José Luis Mendilibar · Domenico Tedesco · Emre Belözoğlu · Vincenzo Montella · Dirk Kuyt

### Evaluation criteria

| Criterion | Data / assessment | Default weight |
|---|---|---:|
| Points per game at the last team | Calculated from wins, draws and games | 15% |
| Career points per game | Match-weighted totals across eligible tenures | 20% |
| Player communication | Documented, editable assessment on a 1–10 scale | 10% |
| Tactical fit for Fenerbahçe | 1–10 assessment against the assumed target profile | 20% |
| Success at major clubs | 1–10 assessment of achievements as head coach | 10% |
| Success in local derbies | 1–10 assessment based on collected evidence | 10% |
| European club competition success | Derived from competition, stage and trophy bonuses | 15% |

Communication and tactical-fit ratings are editorial assumptions rather than measured player satisfaction or tactical performance. Their reasoning and supporting sources are recorded in the [dataset](data/coaches.json) and [detailed report](results/report.md).

### Quick start

Use Python 3.11 or later. Run these commands from the project directory; activating the virtual environment is optional.

**Windows / PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe main.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python main.py
```

Outputs are written to `results/`. Start with [results/report.md](results/report.md). Installing dependencies requires internet access; running the model against the frozen dataset does not.

`requirements-lock.txt` pins all packages used in the verified environment. `requirements.txt` lists direct dependencies.

### How is the score calculated?

```text
Raw PPG = (3 × wins + draws) / games

Adjusted last-team PPG =
    (last-tenure points + prior matches × earlier-career PPG)
    / (last-tenure games + prior matches)

Decision score = 100 × Σ(weight × normalized criterion)
```

PPG is mapped from 0–3 to `[0, 1]`; ratings are mapped from 1–10 to `[0, 1]`. The model uses fixed scales rather than candidate-dependent min–max normalization, so adding a candidate does not change existing candidates' score scales.

The default prior strength is **20 matches**. The selected last tenure is removed when calculating the earlier-career prior. This reduces the influence of small samples. Raw PPG remains available separately; `--prior-matches 0` disables the adjustment.

European competition coefficients are **Champions League = 1.0**, **Europa League = 0.8** and **Conference League = 0.6**. These are project choices. Stage points and bonuses are defined in [config/default.json](config/default.json):

```text
European score = 1 + 0.9 × min(
    10,
    best [competition coefficient × stage points] + 0.5 × min(trophies, 2)
)
```

### Results from the first snapshot

**Sources accessed: 30 October 2026.** These results use `senior`, `last-played` and a 20-match prior. Each coach has a separate record cutoff date; this is a frozen experiment rather than a live ranking.

| Rank | Head coach | Decision score /100 |
|---:|---|---:|
| 1 | Julian Nagelsmann | 72.80 |
| 2 | Antonio Conte | 70.44 |
| 3 | José Luis Mendilibar | 70.41 |
| 4 | Vincenzo Montella | 60.76 |
| 5 | Domenico Tedesco | 60.64 |
| 6 | Abdullah Avcı | 52.80 |
| 7 | Emre Belözoğlu | 49.73 |
| 8 | Dirk Kuyt | 35.87 |

Conte and Mendilibar switch positions when raw last-team PPG is used. The [scenario comparison](results/scenario_comparison.csv) shows how modelling choices affect the results.

### Try different assumptions

For macOS/Linux, replace the Python executable in these PowerShell examples with `.venv/bin/python`.

```powershell
# Evaluate club tenures only
.\.venv\Scripts\python.exe main.py --scope club --output results/club

# Use raw last-team PPG
.\.venv\Scripts\python.exe main.py --prior-matches 0 --output results/raw

# Select the latest appointment, including zero-game tenures
.\.venv\Scripts\python.exe main.py --last-team latest --output results/latest

# Compare scores and ranks under four modelling choices
.\.venv\Scripts\python.exe -m fbcoach.experiments

# Show command-line options
.\.venv\Scripts\python.exe main.py --help
```

Edit weights and competition coefficients in [config/default.json](config/default.json). Weights are normalized to sum to 1. When editing subjective ratings, update their reasoning in [data/coaches.json](data/coaches.json) as well.

### Machine learning and sensitivity analysis

- **K-Means:** operates on seven standardized features. The model tries `k=2–4`, rejects solutions containing singleton clusters and selects the remaining solution with the highest silhouette score. If none qualify, it retains a single cluster.
- **PCA:** produces two-dimensional profile coordinates and explained variance. Cluster IDs are not quality ranks, and explained variance is not prediction accuracy.
- **Sensitivity analysis:** runs two experiments with 10,000 scenarios each by default. The first varies weights; the second varies weights and editorial ratings. The default seed is `42`.

`scenario_first_share` means the share of defined scenarios in which a candidate ranks first. It is not a probability of future success, and simulation percentiles are not statistical confidence intervals.

### Data and coverage

Statistics were compiled from Wikipedia tenure tables. European and derby evidence also uses UEFA, federation and club pages, plus relevant reports and interviews. URLs, access dates, notes and reasoning are stored in [data/coaches.json](data/coaches.json). Downloaded table cells are preserved under [data/source_snapshots/](data/source_snapshots/).

`senior` includes club and senior national-team head-coach tenures; `club` excludes national teams. Lower-division first-team jobs are included. Youth, reserve/feeder and assistant roles are excluded.

To download source tables for review:

```powershell
.\.venv\Scripts\python.exe tools/collect_sources.py --output work/source-review
```

This creates review files without updating the curated dataset. Review tenure coverage and differences in match counts before transferring changes.

### Interpretation limits

- Eight candidates and editorial inputs support exploratory comparison. No supervised success model has been trained.
- Comparable local-derby records are incomplete for Nagelsmann, Emre and Kuyt. Their raw values remain `null`; the model uses a neutral **5.5** rating.
- In this snapshot, Kuyt's Fenerbahçe appointment has zero games. `last-played` selects Dordrecht; `latest` keeps the undefined PPG and represents it with neutral **1.5** PPG in the model.
- League strength, squad/budget, fixtures, salary, contracts, availability and player-level fit with the current squad are not modelled. Penalty-shootout classifications have not been fully harmonized across sources.
- Last-team/career PPG and major-club/European achievements overlap; the same success may influence multiple criteria.

Further details are available in [METODOLOJI.md](docs/METODOLOJI.md) and [CALISTIRMA.md](docs/CALISTIRMA.md). Those documents, code comments, CLI messages and generated detailed reports are currently in Turkish; this README provides the English overview and usage guide.

### Tests and future work

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The initial version passed **33 tests** on Windows/Python 3.11.9. They cover match records, scope filters, missing data, score contributions, simulations, ML edge cases and reproducible exports. [GitHub Actions](.github/workflows/tests.yml) is configured for Python 3.11 and 3.12. The local verification log is stored in [verification.txt](results/verification.txt).

Next research steps include complete derby records, consistent match-level outcome rules and a larger coach–season dataset with an observed target. Such a dataset would allow supervised models to be evaluated using time-based validation.

---

## Proje yapısı / Project structure

```text
fenerbahce-coach-lab/
├── README.md                  # Türkçe / English
├── main.py                    # CLI entry point
├── config/default.json        # Weights, coefficients, prior and seed
├── data/
│   ├── coaches.json           # Curated records, ratings and sources
│   └── source_snapshots/      # Downloaded source table cells
├── fbcoach/
│   ├── data.py                # Validation and match records
│   ├── scoring.py             # Features, contributions and ranking
│   ├── ml.py                  # K-Means and PCA
│   ├── sensitivity.py         # Assumption sensitivity
│   ├── experiments.py         # Scenario comparison
│   ├── reporting.py           # CSV, JSON and Markdown exports
│   └── cli.py                 # Command-line options
├── tools/collect_sources.py   # Source review collector
├── tests/test_model.py        # Model and validation tests
├── docs/                      # Detailed Turkish documentation
├── results/                   # Reports and reproducibility metadata
└── .github/workflows/         # CI configuration
```

## Çıktılar / Outputs

| Dosya / File | İçerik / Contents |
|---|---|
| [report.md](results/report.md) | Ayrıntılı rapor ve kaynaklar / Detailed report and sources |
| [features.csv](results/features.csv) | Ham veriler ve ayarlanmış PPG / Raw values and adjusted PPG |
| [ranking.csv](results/ranking.csv) | Sıralama ve kriter katkıları / Ranking and criterion contributions |
| [criterion_rankings.csv](results/criterion_rankings.csv) | Kriter bazında sıralamalar / Per-criterion rankings |
| [sensitivity_weights.csv](results/sensitivity_weights.csv) | Ağırlık senaryoları / Weight sensitivity |
| [sensitivity_ratings.csv](results/sensitivity_ratings.csv) | Ağırlık ve puan senaryoları / Weight and rating sensitivity |
| [ml_profiles.csv](results/ml_profiles.csv) | Küme ve PCA koordinatları / Clusters and PCA coordinates |
| [ml_diagnostics.json](results/ml_diagnostics.json) | ML tanılaması / ML diagnostics |
| [scenario_comparison.csv](results/scenario_comparison.csv) | Dört tercihin karşılaştırması / Four modelling choices |
| [data_warnings.json](results/data_warnings.json) | Eksik veri ve kapsam notları / Missing-data and scope notes |
| [effective_config.json](results/effective_config.json) | Kullanılan ayarlar / Effective settings |
| [run_metadata.json](results/run_metadata.json) | Veri özeti ve sürümler / Data hash and runtime versions |

[Türkçe](#turkce) · [English](#english)
