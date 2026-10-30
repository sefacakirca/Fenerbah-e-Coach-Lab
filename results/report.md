# Fenerbahçe teknik direktör laboratuvarı — inceleme sürümü

Kaynaklara erişim: **2026-10-30**. Kapsam: `senior`; son takım: `last-played`.

Bu rapor seçtiğimiz kriterlere göre karar desteği sağlar. Ağırlıklar ve editoryal puanlar gelecekteki başarıdan öğrenilmedi. K-Means yalnızca aday profillerini gruplar.

## Ham veriler ve 1–10 değerlendirmeleri

PPG = (3 × galibiyet + beraberlik) / maç. Kupa maçlarında analitik puan eşdeğeridir. Kaynakların penaltı sınıflandırması tamamen uyumlaştırılmadı.

| Aday | Son maçlı/seçilen takım | Maç | Son PPG | Kariyer PPG | İletişim | Uyum | Büyük kulüp | Yerel derbi | Avrupa |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Abdullah Avcı | Trabzonspor | 42 | 1.81 | 1.69 | 7.00 | 6.00 | 7.00 | 6.00 | 2.62 |
| Antonio Conte | Napoli | 91 | 1.96 | 1.98 | 6.00 | 7.00 | 10.00 | 8.00 | 7.48 |
| Julian Nagelsmann | Almanya | 37 | 2.05 | 1.88 | 8.00 | 9.00 | 8.00 | — | 8.20 |
| José Luis Mendilibar | Olympiacos | 127 | 2.08 | 1.47 | 8.00 | 8.00 | 8.00 | 6.50 | 9.10 |
| Domenico Tedesco | Bologna | 4 | 0.25 | 1.71 | 6.00 | 8.00 | 6.00 | 6.00 | 6.76 |
| Emre Belözoğlu | Kasımpaşa | 30 | 1.37 | 1.57 | 6.00 | 8.00 | 3.00 | — | 3.16 |
| Vincenzo Montella | Türkiye | 40 | 1.70 | 1.59 | 7.00 | 8.00 | 6.00 | 5.00 | 6.76 |
| Dirk Kuyt | FC Dordrecht | 39 | 1.21 | 1.10 | 7.00 | 6.00 | 1.00 | — | 1.00 |

**— = puanlanmadı.** Özellikle derbi dökümleri eksiktir. Model, eksik 1–10 puanına nötr 5.5 atar; bunu gözlem veya başarı puanı saymaz.

## Varsayılan sıralama

| Sıra | Aday | Karar puanı /100 | Ağırlık senaryolarında birincilik | Ağırlık + puan senaryolarında birincilik |
|---:|---|---:|---:|---:|
| 1 | Julian Nagelsmann | 72.80 | 89.2% | 52.0% |
| 2 | Antonio Conte | 70.44 | 10.2% | 24.3% |
| 3 | José Luis Mendilibar | 70.41 | 0.7% | 23.7% |
| 4 | Vincenzo Montella | 60.76 | 0.0% | 0.0% |
| 5 | Domenico Tedesco | 60.64 | 0.0% | 0.0% |
| 6 | Abdullah Avcı | 52.80 | 0.0% | 0.0% |
| 7 | Emre Belözoğlu | 49.73 | 0.0% | 0.0% |
| 8 | Dirk Kuyt | 35.87 | 0.0% | 0.0% |

Birincilik payları yalnızca tanımlanan varsayım senaryolarındaki sıralama sıklığıdır; işe alındığında başarılı olma olasılığı değildir. Puan aralıkları istatistiksel güven aralığı değildir.

## Hesaplama ve ayarlar

| Kriter | Ağırlık |
|---|---:|
| Son takım PPG | 15% |
| Kariyer PPG | 20% |
| İletişim | 10% |
| Oyun uyumu | 20% |
| Büyük kulüp | 10% |
| Yerel derbi | 10% |
| Avrupa | 15% |

PPG 0–3 aralığından, editoryal/Avrupa puanları 1–10 aralığından [0,1]'e çevrilir. Karar puanı = 100 × Σ(ağırlık × normalize özellik). Adaylara göre min–max ölçeği kullanılmaz.

Son takım için önsel güç: **20 maç**. Önsel PPG, seçilen son görev çıkarıldıktan sonraki kariyerden hesaplanır. Ayarlanmış PPG = (son görev puanı + önsel güç × önceki kariyer PPG) / (son görev maçı + önsel güç). Önceki görev yoksa nötr 1.5 kullanılır. Sıfır maçta ham PPG tanımsız kalır.

| Aday | Ham son PPG | Sıralamada kullanılan PPG | Kariyer maçı | Kayıt tarihi |
|---|---:|---:|---:|---|
| Abdullah Avcı | 1.81 | 1.77 | 636 | 2024-08-31 |
| Antonio Conte | 1.96 | 1.96 | 703 | 2026-05-24 |
| Julian Nagelsmann | 2.05 | 1.99 | 352 | 2026-06-29 |
| José Luis Mendilibar | 2.08 | 1.98 | 946 | 2026-09-08 |
| Domenico Tedesco | 0.25 | 1.49 | 251 | 2026-09-16 |
| Emre Belözoğlu | 1.37 | 1.46 | 196 | 2026-10-29 |
| Vincenzo Montella | 1.70 | 1.66 | 471 | 2026-10-05 |
| Dirk Kuyt | 1.21 | 1.15 | 109 | 2026-10-28 |

### Avrupa puanı

Katsayılar: UCL=1, UEL=0.8, UECL=0.6. Bunlar proje tercihidir, UEFA ülke katsayısı değildir.

Tur puanları: qualifying=1, group=2, knockout_playoff=3, round_of_16=4, quarter_final=6, semi_final=8, finalist=9, winner=10.

Avrupa = 1 + 0.9 × min(10, en yüksek [turnuva katsayısı × tur puanı] + 0.5 × min(kazanılan kupa, 2)).

En güçlü doğrulanmış ilerleme ve kupalar kullanılır; bu bir Avrupa maç kazanma oranı değildir. Millî takım turnuvaları dahil değildir. Sezonlar arası turnuva değişimlerinin tamamı ve rakip gücü modellenmedi.

### ML ve duyarlılık

K-Means: **k=2**; silhouette=0.222. k=2–4 denenir, tek kişilik kümeler elenir. Uygun ayrım yoksa k=1 kalır. StandardScaler ve PCA yalnızca profil analizi içindir; sıralama küme numarasını kullanmaz.

PCA ilk iki bileşenin açıkladığı varyans: 79.5%. Bu bir tahmin doğruluğu değildir.

Her analizde 10,000 senaryo, seed=42. Ağırlıklar Dirichlet dağılımından çekilir (yoğunluk=80); sıfır ağırlıklar sıfır kalır. İkinci analizde editoryal puanlar güven düzeyine göre üçgensel dağılımla, puanlanmamış alanlar 1–10'da tekdüze dağılımla değişir. PPG örnekleme hatası bu analizde modellenmez.

## Adayların gerekçeleri ve kaynakları

### Abdullah Avcı

Maç kayıtları: [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)

- **İletişim: 7.00/10** — Uzun Başakşehir görevinden hareketle istikrar odaklı bir iletişim varsayımı. Doğrudan oyuncu anketi yok. Editoryal güven: `low`. [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)
- **Oyun uyumu: 6.00/10** — Kontrollü yerleşim ve savunma dengesi olumlu; varsaydığımız yüksek tempo ve sürekli hücum profiline kısmi uyum. Editoryal güven: `low`. [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)
- **Büyük kulüp: 7.00/10** — Trabzonspor ile 2021/22 şampiyonluğu güçlü kanıt; Beşiktaş dönemi aynı düzeyde başarı üretmedi. Editoryal güven: `medium`. [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)
- **Yerel derbi: 6.00/10** — 2019 Galatasaray galibiyeti olumlu bir örnek. Tam kariyer derbi dökümü olmadığı için ihtiyatlı editoryal puan. Editoryal güven: `low`. [Beşiktaş 1-0 Galatasaray, 27 Ekim 2019](https://bjk.com.tr/tr/mac_merkezi/canli/14779)

- Avrupa kanıtı: 2022/23 Trabzonspor, UCL / qualifying. [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)
- Avrupa kanıtı: 2022/23 Trabzonspor, UEL / group. [Abdullah Avcı — managerial statistics](https://en.wikipedia.org/wiki/Abdullah_Avc%C4%B1)
- Avrupa kanıtı: 2022/23 Trabzonspor, UECL / knockout_playoff. [Trabzonspor–Basel, 2023 Konferans Ligi play-off](https://www.uefa.com/newsfiles/uefaeuropaconferenceleague/2023/2036615_LU.pdf)

- Alt yaş, rezerv ve yardımcı antrenörlük görevleri kapsam dışıdır.
- Sofascore ve Wikipedia takım maç sayıları farklıdır; bu sürüm Wikipedia takım satırlarını sabitler.

### Antonio Conte

Maç kayıtları: [Antonio Conte — managerial statistics](https://en.wikipedia.org/wiki/Antonio_Conte)

- **İletişim: 6.00/10** — Takım bağlılığı kurabilen yoğun talepkârlık; farklı kadrolarda aynı iletişim etkisinin süreceği belirsiz. Bu bir oyuncu memnuniyeti ölçümü değildir. Editoryal güven: `low`. [Inter coach Conte on the 2020 Europa League final](https://www.uefa.com/uefaeuropaleague/news/0260-102b58fe7eea-f9e0ce560045-1000--europa-league-final-inter-coach-conte-on-squaring-up-to-sevilla/), [Antonio Conte — managerial statistics](https://en.wikipedia.org/wiki/Antonio_Conte)
- **Oyun uyumu: 7.00/10** — Kanat bekleri, geçişler ve disiplin güçlü; mevcut kadro analiz edilmeden üçlü savunmaya uyum garanti edilemez. Editoryal güven: `low`. [Antonio Conte — managerial statistics](https://en.wikipedia.org/wiki/Antonio_Conte)
- **Büyük kulüp: 10.00/10** — Juventus, Chelsea, Inter ve Napoli ile üst lig şampiyonlukları; bu aday kümesindeki en güçlü tekrarlanan lig başarısı. Editoryal güven: `medium`. [Antonio Conte — managerial statistics](https://en.wikipedia.org/wiki/Antonio_Conte)
- **Yerel derbi: 8.00/10** — Inter ile 2021'de 3-0'lık Milan galibiyeti güçlü örnek. Puan, eksiksiz bir derbi kazanma oranı değildir. Editoryal güven: `low`. [Milan 0-3 Inter, 21 Şubat 2021](https://www.inter.it/en/news/2021-02-21-milan-0-3-inter-serie-a-2020-21)

- Avrupa kanıtı: 2019/20 Inter, UEL / finalist. [Inter coach Conte on the 2020 Europa League final](https://www.uefa.com/uefaeuropaleague/news/0260-102b58fe7eea-f9e0ce560045-1000--europa-league-final-inter-coach-conte-on-squaring-up-to-sevilla/)
- Avrupa kanıtı: 2012/13 Juventus, UCL / quarter_final. [Antonio Conte — managerial statistics](https://en.wikipedia.org/wiki/Antonio_Conte)

- Kaynak toplamı takım satırlarından yeniden doğrulandı: 703 maç, 408 galibiyet, 165 beraberlik, 130 mağlubiyet.
- Arezzo–Siena gibi erken görevlerin kaynak referansları daha zayıf; maç bazında tekrar doğrulama açık iş.

### Julian Nagelsmann

Maç kayıtları: [Julian Nagelsmann — managerial statistics](https://en.wikipedia.org/wiki/Julian_Nagelsmann)

- **İletişim: 8.00/10** — Oyuncuya göre iletişim ve rol tanımına önem veren kamuya açık yaklaşım üzerinden olumlu varsayım; bağımsız anket yok. Editoryal güven: `low`. [Nagelsmann tactics and style of play](https://learning.coachesvoice.com/cv/julian-nagelsmann-bayern-munich-red-bull-rangnick/), [Nagelsmann'ın Almanya'daki ilk iki yılı](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/julian-nagelsmann-first-two-years-germany)
- **Oyun uyumu: 9.00/10** — Ön alan baskısı, esnek yerleşim ve hücum varyasyonları tanımladığımız Fenerbahçe profiline güçlü uyum gösteriyor. Editoryal güven: `low`. [Nagelsmann tactics and style of play](https://learning.coachesvoice.com/cv/julian-nagelsmann-bayern-munich-red-bull-rangnick/)
- **Büyük kulüp: 8.00/10** — Bayern'de lig ve Süper Kupa başarıları var; Conte kadar farklı büyük kulüpte tekrarlanmış başarı yok. Editoryal güven: `medium`. [Julian Nagelsmann — managerial statistics](https://en.wikipedia.org/wiki/Julian_Nagelsmann)
- **Yerel derbi: —/10** — Seçilen sıkı yerel derbi tanımında yeterli karşılaştırılabilir kayıt toplanmadı. Bayern–Dortmund yerel derbi sayılmadı. Editoryal güven: `low`. [Julian Nagelsmann — managerial statistics](https://en.wikipedia.org/wiki/Julian_Nagelsmann)

- Avrupa kanıtı: 2019/20 RB Leipzig, UCL / semi_final. [2020 Leipzig–PSG yarı finali, teknik direktör Nagelsmann](https://www.uefa.com/newsfiles/UCL/2020/2030148_HR.pdf)

- Hoffenheim U19 kariyere katılmadı. Millî takım istenmezse --scope club kullanılır.
- Son görev millî takım; kulüp karşılaştırması için --scope club kullanılabilir.
- Ölçülmeyen alanlara nötr değer atandı: derby

### José Luis Mendilibar

Maç kayıtları: [José Luis Mendilibar — managerial statistics](https://en.wikipedia.org/wiki/Jos%C3%A9_Luis_Mendilibar)

- **İletişim: 8.00/10** — UEFA röportajındaki sade ve açık talimat yaklaşımı üzerinden olumlu değerlendirme; oyuncu anketi yerine yorumdur. Editoryal güven: `low`. [Mendilibar on his impact, philosophy and Europa League](https://www.uefa.com/uefaeuropaleague/news/0281-17f626397b3e-59ab2287f94a-1000--mendilibar-on-turning-tide-at-sevilla/)
- **Oyun uyumu: 8.00/10** — Önde baskı, direkt hücum ve anlaşılır roller güçlü uyum; sürekli topa sahip olmayı tek ölçüt kabul etmiyoruz. Editoryal güven: `low`. [Mendilibar on his impact, philosophy and Europa League](https://www.uefa.com/uefaeuropaleague/news/0281-17f626397b3e-59ab2287f94a-1000--mendilibar-on-turning-tide-at-sevilla/)
- **Büyük kulüp: 8.00/10** — Sevilla ve Olympiacos'ta Avrupa kupaları, Olympiacos'ta yerel lig başarısı; uzun İspanya kariyerinin tamamı elit kulüplerde geçmedi. Editoryal güven: `medium`. [Olympiacos 1-0 Fiorentina: Mendilibar'ın iki Avrupa kupası](https://www.uefa.com/uefaconferenceleague/news/028d-1b01e5ec31a5-144c1f00e4f3-1000--olympiacos-1-0-fiorentina-aet-el-kaabi-swoops-in-to-secure-/), [José Luis Mendilibar — managerial statistics](https://en.wikipedia.org/wiki/Jos%C3%A9_Luis_Mendilibar)
- **Yerel derbi: 6.50/10** — Olympiacos–Panathinaikos için seçilmiş galibiyet, beraberlik ve mağlubiyet örnekleri karışık tablo gösteriyor. Tam kariyer oranı yok. Editoryal güven: `low`. [Panathinaikos 2-2 Olympiacos, 19 Mayıs 2024](https://www.olympiacos.org/en/2024/05/20/mendilibar-and-now-the-final/), [Olympiacos 4-2 Panathinaikos, 30 Mart 2025](https://as.com/futbol/internacional/el-olympiacos-de-mendilibar-se-lleva-el-derbi-y-acaricia-el-titulo-n/), [Olympiacos 1-3 Panathinaikos, 10 Mart 2024](https://en.wikipedia.org/wiki/2023%E2%80%9324_Olympiacos_F.C._season)

- Avrupa kanıtı: 2022/23 Sevilla, UEL / winner. [Olympiacos 1-0 Fiorentina: Mendilibar'ın iki Avrupa kupası](https://www.uefa.com/uefaconferenceleague/news/028d-1b01e5ec31a5-144c1f00e4f3-1000--olympiacos-1-0-fiorentina-aet-el-kaabi-swoops-in-to-secure-/)
- Avrupa kanıtı: 2023/24 Olympiacos, UECL / winner. [Olympiacos 1-0 Fiorentina: Mendilibar'ın iki Avrupa kupası](https://www.uefa.com/uefaconferenceleague/news/028d-1b01e5ec31a5-144c1f00e4f3-1000--olympiacos-1-0-fiorentina-aet-el-kaabi-swoops-in-to-secure-/)

- Kaynak toplamı takım satırlarından doğrulandı: 1104 maç/448 galibiyet. Model rezerv/feeder görevlerini ayrıca çıkarır.
- Erken dönem alt lig görevleri dahildir; tüm maçlar aynı lig zorluğunu temsil etmez.
- Penaltı serilerinin kaynaklardaki sınıflandırması aynı olmayabilir; W/D/L kayıtları bu sürümde aynen kullanılır.

### Domenico Tedesco

Maç kayıtları: [Bologna: Tedesco sonrası Palladino, dört maçta bir beraberlik](https://sport.sky.it/calcio/serie-a/2026/09/16/bologna-tedesco-esonero-palladino-allenatore-news), [Domenico Tedesco — managerial statistics](https://en.wikipedia.org/wiki/Domenico_Tedesco)

- **İletişim: 6.00/10** — Farklı ülke ve kadrolara uyarlanma deneyimine sınırlı olumlu kredi; oyuncuların özel ilişkileri hakkında veri yok. Editoryal güven: `low`. [Domenico Tedesco — managerial statistics](https://en.wikipedia.org/wiki/Domenico_Tedesco)
- **Oyun uyumu: 8.00/10** — Pres, geçiş oyunu ve formasyon esnekliği hedef profille uyumlu; uygulama kadro ve hazırlık süresine bağlı. Editoryal güven: `low`. [Domenico Tedesco — managerial statistics](https://en.wikipedia.org/wiki/Domenico_Tedesco)
- **Büyük kulüp: 6.00/10** — Leipzig ile 2022 Almanya Kupası ve Schalke ile lig ikinciliği; büyük kulüplerde tekrarlanan lig şampiyonluğu yok. Editoryal güven: `medium`. [Domenico Tedesco — managerial statistics](https://en.wikipedia.org/wiki/Domenico_Tedesco)
- **Yerel derbi: 6.00/10** — 2017/18 Revierderby'de 4-4 ve 2-0 olumlu örnekler. Sonraki tüm derbiler derlenmediği için güçlü bir başarı oranı iddia edilmiyor. Editoryal güven: `low`. [Schalke: 2017/18 maç arşivi](https://schalke04.de/verein/tradition/alle-spiele-alle-tore/bundesliga/bundesliga-saison-2017-2018/)

- Avrupa kanıtı: 2021/22 RB Leipzig, UEL / semi_final. [Leipzig–Rangers 2022 yarı finali](https://datencenter.dfb.de/en/data-center/europa-league/18488/1/2337758)
- Avrupa kanıtı: 2018/19 Schalke 04, UCL / round_of_16. [Domenico Tedesco — managerial statistics](https://en.wikipedia.org/wiki/Domenico_Tedesco)

- Wikipedia istatistik tablosu Nisan 2026'da kalmıştı; Bologna'nın 4 maçlık görevi Sky Sport'un 16 Eylül raporundan ayrı eklendi.
- Dört maçlık son görev için ham PPG 0.25'tir; modelde örneklem küçüklüğü ayrıca ele alınır.
- Son görev yalnızca 4 maç; küçük örneklem.

### Emre Belözoğlu

Maç kayıtları: [Emre Belözoğlu — managerial statistics](https://en.wikipedia.org/wiki/Emre_Bel%C3%B6zo%C4%9Flu)

- **İletişim: 6.00/10** — Yerel futbol çevresine aşinalık ve açık oyun anlatımı üzerinden ihtiyatlı ön kabul; futbolculuk liderliği doğrudan teknik direktörlük puanı değildir. Editoryal güven: `low`. [Emre'nin pres, topa sahip olma ve geçiş oyunu anlatımı](https://as.com/futbol/primera/emre-guler-mejorara-con-xabi-n/)
- **Oyun uyumu: 8.00/10** — Kendi anlattığı pres, topa sahip olma ve hızlı geçiş hedef profille uyumlu. Maç verisiyle bağımsız taktik ölçüm yapılmadı. Editoryal güven: `low`. [Emre'nin pres, topa sahip olma ve geçiş oyunu anlatımı](https://as.com/futbol/primera/emre-guler-mejorara-con-xabi-n/)
- **Büyük kulüp: 3.00/10** — Fenerbahçe'de kısa süreli görev; Başakşehir Türkiye Kupası finali olumlu. Büyük kulüpte kazanılmış A takım teknik direktörlük şampiyonluğu sınırlı. Editoryal güven: `medium`. [Emre Belözoğlu — managerial statistics](https://en.wikipedia.org/wiki/Emre_Bel%C3%B6zo%C4%9Flu)
- **Yerel derbi: —/10** — Kısa Fenerbahçe görevi ve diğer İstanbul kulüpleri için tam, tutarlı yerel derbi örneklemi toplanmadı. Editoryal güven: `low`. [Emre Belözoğlu — managerial statistics](https://en.wikipedia.org/wiki/Emre_Bel%C3%B6zo%C4%9Flu)

- Avrupa kanıtı: 2022/23 İstanbul Başakşehir, UECL / round_of_16. [Başakşehir 1-4 Gent, Konferans Ligi son 16](https://www.tff.org/default.aspx?ftxtID=39755&pageID=267)

- 30 Ekim'deki doğrudan sayfa erişimi 29 Ekim itibarıyla 30 Kasımpaşa maçı gösterdi; eski arama özeti 29 maçtı. Kaydedilen tablo hücreleri esas alındı.
- Ölçülmeyen alanlara nötr değer atandı: derby

### Vincenzo Montella

Maç kayıtları: [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella)

- **İletişim: 7.00/10** — Farklı ülkelerdeki görevler ve Türkiye'de süreklilik üzerinden orta düzey olumlu varsayım. Oyuncu iletişimi için doğrudan anket yok. Editoryal güven: `low`. [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella)
- **Oyun uyumu: 8.00/10** — Topa sahip olma ve teknik oyunculara alan açma yaklaşımı uyumlu; millî takım oyununu kulübe aktarmak ayrıca değerlendirilmelidir. Editoryal güven: `low`. [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella)
- **Büyük kulüp: 6.00/10** — Milan ile Süper Kupa, Fiorentina ile Avrupa yarı finali; Sevilla ve ikinci Fiorentina dönemleri daha zayıf. Millî takım dereceleri kulüp kupası sayılmadı. Editoryal güven: `medium`. [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella), [Fiorentina 2015 Avrupa Ligi yarı finali](https://www.uefa.com/uefaeuropaleague/news/0221-0e90ba869e9f-10aa47988723-1000--steadfast-sevilla-finish-off-fiorentina/)
- **Yerel derbi: 5.00/10** — Milan dönemindeki yerel derbi örnekleri baskın başarıya işaret etmiyor. Kaydedilen 2017 beraberliği bir örnektir; tam derbi oranı değildir. Editoryal güven: `low`. [Inter 2-2 Milan, 15 Nisan 2017; Montella](https://www.inter.it/en/news/2017-04-15-inter-2-2-ac-milan), [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella)

- Avrupa kanıtı: 2014/15 Fiorentina, UEL / semi_final. [Fiorentina 2015 Avrupa Ligi yarı finali](https://www.uefa.com/uefaeuropaleague/news/0221-0e90ba869e9f-10aa47988723-1000--steadfast-sevilla-finish-off-fiorentina/)
- Avrupa kanıtı: 2017/18 Sevilla, UCL / quarter_final. [Vincenzo Montella — managerial statistics](https://en.wikipedia.org/wiki/Vincenzo_Montella)

- Son görev Türkiye; yalnızca kulüp senaryosunda son takım Adana Demirspor olur.
- Son görev millî takım; kulüp karşılaştırması için --scope club kullanılabilir.

### Dirk Kuyt

Maç kayıtları: [Kuyt takes interim charge of Fenerbahce](https://www.liverpoolfc.com/news/dirk-kuyt-takes-interim-charge-of-fenerbahce-ahead-of-clash-with-liverpool), [Dirk Kuyt — managerial statistics](https://en.wikipedia.org/wiki/Dirk_Kuyt)

- **İletişim: 7.00/10** — Fenerbahçe ortamını tanımasına sınırlı kredi; bu, futbolculuk itibarını teknik direktörlükte kanıtlanmış iletişim başarısı saymaz. Yüksek belirsizlik. Editoryal güven: `low`. [Kuyt takes interim charge of Fenerbahce](https://www.liverpoolfc.com/news/dirk-kuyt-takes-interim-charge-of-fenerbahce-ahead-of-clash-with-liverpool)
- **Oyun uyumu: 6.00/10** — Kısa A takım teknik direktörlük geçmişi nedeniyle hücum ve pres hedeflerine uyum hakkında sınırlı kanıt; Fenerbahçe deneyimi futbolculuk döneminden ayrı tutulur. Editoryal güven: `low`. [Dirk Kuyt — managerial statistics](https://en.wikipedia.org/wiki/Dirk_Kuyt)
- **Büyük kulüp: 1.00/10** — Büyük kulüpte maç yönetmiş başantrenör olarak henüz doğrulanmış başarı kaydı yok. Yardımcılık ve oyuncu kupaları sayılmaz; bu yetenek yokluğu demek değildir. Editoryal güven: `medium`. [Dirk Kuyt — managerial statistics](https://en.wikipedia.org/wiki/Dirk_Kuyt), [Kuyt takes interim charge of Fenerbahce](https://www.liverpoolfc.com/news/dirk-kuyt-takes-interim-charge-of-fenerbahce-ahead-of-clash-with-liverpool)
- **Yerel derbi: —/10** — Başantrenör olarak karşılaştırılabilir yerel derbi dökümü toplanmadı; oyunculuk derbileri kapsam dışı. Editoryal güven: `low`. [Dirk Kuyt — managerial statistics](https://en.wikipedia.org/wiki/Dirk_Kuyt)


- Fenerbahçe geçici görevi 0 maç: PPG tanımsızdır, sıfır başarı olarak kodlanmaz.
- Varsayılan last-played politikası Dordrecht'i kullanır. --last-team latest seçeneği 0 maçlı görevi eksik özellik olarak bırakır.
- Canlı Wikipedia Beerschot satırı 14/12/27; önbellekte 13/13/27 görülüyor. Bu sürüm doğrudan indirilen tabloyu sabitler; penaltı sınıflandırması farkı olabilir.
- Son görev Fenerbahçe (0 maç); son maçlı görev FC Dordrecht kullanıldı.
- Ölçülmeyen alanlara nötr değer atandı: derby

## Yorumlama sınırları

Sekiz aday, teknik direktör başarı tahmini için yeterli etiketli eğitim verisi değildir. İletişim ve uyum puanları saha içi/saha dışı psikometrik ölçüm değildir; gerekçeli proje varsayımlarıdır. Derbi örnekleri seçilmiş kanıtlardır, kariyerin tam maç listesi değildir. Büyük kulüp kriteri ve Avrupa kriteri kısmen aynı başarıları ödüllendirebilir; son takım PPG ile kariyer PPG de ilişkilidir.

Lig zorluğu, kadro/bütçe, fikstür, görev süresi, maaş, sözleşme, müsaitlik ve güncel Fenerbahçe kadrosuna oyuncu bazında uyum modellenmedi. Ülke/lig ve millî takım maçları tam eşdeğer değildir. Kaynaklara bugün erişilmiş olması bütün kayıtların bugüne kadar tam olduğu anlamına gelmez.

Sonraki araştırma: tam maç listeleriyle tek penaltı kuralı, tam yerel derbi dökümü ve daha büyük teknik direktör-sezon verisi toplamak. Gerçek bir hedef tanımlanırsa zaman bazlı doğrulamayla denetimli ML eklenebilir.

README ve GitHub yayını, kod incelemesinden sonraki aşamadır.
