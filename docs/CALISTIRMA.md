# İlk sürümü çalıştırma

Python 3.11 veya üzeri gerekiyor. Komutları proje klasöründe çalıştırın.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux için aynı komutlarda Python yolunu `.venv/bin/python` yapın.

`requirements-lock.txt` bu çalışmada doğrulanan bütün paket sürümlerini sabitler. `requirements.txt` yalnızca projenin doğrudan bağımlılıklarını içerir.

Çalışma sırasında internet gerekmez. Veriler `data/coaches.json` içinde sabitlenmiştir. Bağımlılık kurulumu ve isteğe bağlı kaynak yenilemesi internet kullanır.

```powershell
# Millî takım istatistiklerini dışarıda bırak
.\.venv\Scripts\python.exe main.py --scope club --output results/club

# Son takım puanını küçük örneklem düzeltmesi olmadan kullan
.\.venv\Scripts\python.exe main.py --prior-matches 0 --output results/raw

# Kuyt'ın sıfır maçlı güncel Fenerbahçe görevini seç
.\.venv\Scripts\python.exe main.py --last-team latest --output results/latest

# Dört model tercihinin puan/sıra karşılaştırmasını yeniden üret
.\.venv\Scripts\python.exe -m fbcoach.experiments

# Yeni kaynak tablolarını inceleme klasörüne indir; ana veriyi değiştirmez
.\.venv\Scripts\python.exe tools/collect_sources.py --output work/source-review
```

`config/default.json` içindeki yedi ağırlığı ve Avrupa katsayılarını değiştirebilirsiniz. Ağırlıkların toplamı otomatik olarak 1'e ölçeklenir. `data/coaches.json` içindeki öznel puanları değiştirirken gerekçe ve kaynaklarını da güncelleyin. `null`, puanlanmamış alan demektir; modelde nötr 5.5 kullanılır.

`results/report.md` ham tabloyu, sıralamayı, puan gerekçelerini, kaynakları ve sınırları birlikte gösterir. `ranking.csv` her kriterin toplam skora katkısını içerir. `criterion_rankings.csv` kriter başına sıralamadır; eksik puanların sırası boş kalır. `features.csv` ham PPG'yi ve modelde kullanılan ayarlanmış PPG'yi ayrı sütunlarda saklar.

`sensitivity_weights.csv` yalnızca ağırlıkları; `sensitivity_ratings.csv` ağırlıklarla birlikte editoryal puanları değiştirir. `scenario_first_share`, verilen senaryolar arasında birinci çıkma payıdır. Gerçek hayatta başarılı olma olasılığı veya istatistiksel güven aralığı değildir.

`ml_profiles.csv` K-Means kümelerini ve PCA koordinatlarını; `ml_diagnostics.json` küme sayısı adaylarını ve silhouette sonuçlarını kaydeder. Küme numarası başarı sırası değildir. `run_metadata.json` veri/config özetlerini ve kütüphane sürümlerini; `effective_config.json` gerçekten kullanılan ayarları saklar.

Kaynak tablosu hücreleri `data/source_snapshots/` altında denetim için saklandı. Bu dosyalar ana veriye otomatik uygulanmaz. Güncellemede kapsam, penaltı sınıflandırması, eksik görevler ve görev tarihleri incelenmelidir.

Bu sürüm depo içinden `python main.py` ile çalıştırılmak üzere hazırlanmıştır. Türkçe ve İngilizce proje tanıtımı için [README.md](../README.md) dosyasını inceleyin. Lisans tercihi ve GitHub yayını kod incelemesinden sonraki aşamadır.
