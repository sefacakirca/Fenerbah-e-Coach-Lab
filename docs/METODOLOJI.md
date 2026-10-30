# Modelin amacı ve tercihleri

Amaç, sekiz adayı açıkça tanımlanmış kriterlere göre karşılaştırmak. Sonuç, gelecekteki Fenerbahçe performansının tahmini değildir. Ana sıralama çok kriterli bir karar modelidir; ML kısmı etiketsiz profil analizidir.

## Varsayılan Fenerbahçe profili

Bu projede yüksek tempo, önde baskı, hücum üretimi, kapanan rakiplere karşı çözüm ve büyük kulüp baskısında istikrar hedefleniyor. Bu profil bizim inceleme varsayımımızdır; kulübün resmî strateji belgesi veya güncel kadronun oyuncu bazında analizi değildir. Profil değişirse `style_fit` puanlarını yeniden değerlendirmek gerekir.

## Yedi kriter

| Kriter | Tür | Ağırlık | Yorum |
|---|---|---:|---|
| Son takım PPG | Kaynaklı W/D/L'den türetilir | %15 | Yakın deneyim; görev kısaysa oynak |
| Kariyer PPG | Görevlerin maç ağırlıklı toplamı | %20 | Daha uzun geçmiş; lig ve kadro farklarına duyarlı |
| İletişim | Editoryal varsayım | %10 | Kamuya açık yaklaşım; oyuncu memnuniyet anketi yok |
| Oyun uyumu | Editoryal varsayım | %20 | Yukarıdaki hedef profile uyum |
| Büyük kulüp başarısı | Editoryal başarı değerlendirmesi | %10 | A takım başantrenörlüğünde kupa/istikrar; oyuncu kupaları sayılmaz |
| Yerel derbi | Eksik kanıta dayalı editoryal değerlendirme | %10 | Tam kariyer dökümü henüz yok; geniş belirsizlik |
| Avrupa başarısı | Açık kuralla türetilen tercih puanı | %15 | Turnuva katsayısı, en iyi tur ve kupa bonusu |

Başlangıç ağırlıkları uzmanlarca öğrenilmedi. %35 PPG, %30 iletişim/oyun uyumu ve %35 başarı geçmişi dengesini incelemek için seçildi. Kariyer/son görev ve büyük kulüp/Avrupa alanları ilişkilidir; aynı başarıya iki kez önem verme riski vardır. Duyarlılık analizi bu yüzden rapora dahildir.

## Editoryal puan çapaları

| Alan | 1–3 | 4–6 | 7–8 | 9–10 |
|---|---|---|---|---|
| İletişim | Güçlü uyum riski varsayımı | Karışık/sınırlı kanıt | Olumlu kamuya açık yaklaşım | Birden fazla bağlamda güçlü, bağımsız kanıt gerekir |
| Oyun uyumu | Hedef profille sınırlı örtüşme | Kısmi örtüşme | Çoğu hedefle uyum | Çok güçlü teorik uyum; uygulama yine belirsiz |
| Büyük kulüp | Kanıtlanmış büyük kulüp başarısı az/yok | Sınırlı kupa veya istikrar | Lig/Avrupa başarısı | Birden fazla büyük kulüpte tekrarlanan üst düzey başarı |
| Yerel derbi | Zayıf kanıt | Karışık/sınırlı örnekler | Güçlü olumlu örnekler | Kapsamlı ve istikrarlı üstünlük kanıtı gerekir |

Bir puanın düşük olması, kişinin özel hayatı veya karakteri hakkında yargı değildir. Özellikle iletişim puanları ölçüm değil, bu proje için düzenlenebilir başlangıç varsayımlarıdır. Güven etiketleri kalibre edilmiş olasılık değildir. Derbi puanları sistematik maç oranı yerine seçilmiş örneklere dayanır; örnek seçme yanlılığı vardır. Yeterli kanıt toplanmayan Nagelsmann, Emre ve Kuyt için ham derbi puanı `null` kaldı; modelin kullandığı 5.5 ayrı bir nötr atamadır.

Derbi, şehir/bölge temelli yerel rekabeti ifade eder: Milano, İstanbul, Ruhr ve Atina/Pire gibi. Bayern–Dortmund, Juventus–Inter veya millî takım rekabetleri bu sürümde yerel derbi kanıtı olarak kullanılmadı. Her hocanın tam derbi maç listesini toplamak, bu kriteri güçlendirmek için öncelikli sonraki iştir.

## Kaynak ve kapsam

30 Ekim 2026'da internetten Wikipedia yönetici istatistik tabloları indirildi ve hücreleri `data/source_snapshots/` altında saklandı. Ana veriye yalnızca incelenen görev satırları aktarıldı. Kayıt tarihlerinin kişiden kişiye farklı olduğu `record_as_of` alanında görünür. Güncel görev durumları ile tablo güncelleme tarihleri ayrı ele alınır. Örneğin Tedesco'nun Wikipedia tablosunda olmayan Bologna dönemi [Sky Sport'un 16 Eylül 2026 tarihli haberinden](https://sport.sky.it/calcio/serie-a/2026/09/16/bologna-tedesco-esonero-palladino-allenatore-news) eklendi.

Sofascore ve Wikipedia sayılarının farklı olduğu görüldü; iki kaynağın toplamları birleştirilmedi. Bu sürümün PPG kayıtlarında Wikipedia takım satırları tercih edildi. İstisna ve uyuşmazlıklar ana verinin `notes` alanında yazılıdır. UEFA, federasyon ve kulüp sayfaları Avrupa/derbi kanıtlarını destekler. Bütün bağlantılar `data/coaches.json` içindeki `sources` sözlüğündedir. Bir kaynak, bizim verdiğimiz sayısal editoryal puanı doğrulamaz; o puanın dayandığı bağlamı sağlar.

Kulüp ve A millî takım başantrenörlüğü `senior` kapsamındadır. `club` millî takımları çıkarır. Genç, rezerv/feeder ve yardımcı antrenörlük görevleri dışarıda tutulur. Mendilibar'ın erken alt lig A takım görevleri dahildir; Basconia ve Athletic B görevleri hariçtir. Kaynaklarda listelenmeyen erken görevler olabilir; kapsam, belgelenmiş görevlerle sınırlıdır.

PPG bütün kayıtlar için `(3W + D) / N` olarak yeniden hesaplanır. Kaynakların penaltı serilerini galibiyet/beraberlik olarak sınıflandırması tamamen uyumlaştırılmadı. Bu nedenle sonuç, kusursuz bir ligler arası performans ölçüsü değildir. Gelecek veri sürümünde maç bazında tek sonuç kuralı kullanılmalı.

## Küçük örneklem ve sıfır maç

Varsayılan `last-played`, en son maç yönetilen görevi seçer. Kuyt'ın yeni Fenerbahçe görevi sıfır maç olduğundan Dordrecht kullanılır; güncel görevin PPG'si ayrıca boş gösterilir. `latest` politikasında son görev sıfır maç olsa da seçilir ve modelde eksik PPG'ye nötr 1.5 atanır.

Varsayılan son takım özelliği 20 maçlık önselle önceki kariyere çekilir. Seçilen son görevin maçları önselden çıkarılır. Bu yöntem Tedesco'nun dört Bologna maçının aşırı etkisini azaltır. 20 sayısı veriden öğrenilmiş optimum değildir; `--prior-matches 0` ile ham PPG senaryosu incelenebilir. Ham veriler değiştirilmez.

## Avrupa kuralı

Katsayılar `UCL=1.0, UEL=0.8, UECL=0.6`. Tur puanları ve bonuslar `config/default.json` içindedir. Bunlar resmî UEFA katsayıları değil, proje tercihleridir. En iyi ağırlıklı tur ve en fazla iki Avrupa kupası bonusu kullanılır; böylece çok uzun kariyeri sırf katılım sayısıyla ödüllendirmeyiz. Buna karşılık tekrar eden iyi performansın bir kısmını ve rakip gücünü kaybederiz.

## ML tercihi ve sonraki sürüm

[K-Means](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) standartlaştırılmış yedi özelliğe uygulanır. k=2–4 arasında tek kişilik küme üretmeyen en yüksek [silhouette](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) seçilir. PCA iki boyutlu profil koordinatları verir. Bu adımlar başarı sıralaması öğrenmez; skor, küme etiketinden bağımsızdır. Sekiz gözlem ve öznel girdiler yüzünden küme ayrımı keşifseldir.

Kendi verdiğimiz karar puanlarını Random Forest'a hedef yapıp aynı adayları yeniden tahmin etmek, başarıyı öğrenmek yerine puanlama kuralını taklit eder. Bu yüzden bu sürümde denetimli başarı iddiası yok. DL için de gerekçe yok.

Denetimli ML için daha büyük bir teknik direktör–sezon veri seti ve gerçek hedef gerekir: örneğin gelecek sezondaki bütçeye göre beklenen puanın üzerindeki performans. Maaş/kadro değeri, lig gücü, fikstür, sakatlıklar ve görev başlangıcındaki takım durumu eklenmeli. Eğitim/test zamanla ayrılmalı; aynı teknik direktörün ilişkili sezonları ve sonradan öğrenilen bilgiler veri sızıntısına karşı kontrol edilmeli. Bundan sonra basit bir regresyon veya ağaç modeli karşılaştırılabilir.

## İlk deneyin yorumu

Varsayılan ayarlarda Nagelsmann 72.80, Conte 70.44, Mendilibar 70.41 puan alıyor. Ham PPG senaryosunda Conte ve Mendilibar yer değiştiriyor. Bu küçük farkı kesin tercih gibi yorumlamamak gerekir. Editoryal puan belirsizliği eklendiğinde birincilik senaryo payları da belirgin değişiyor. Güncel sözleşme, maaş ve müsaitlik bu sonuçlarda yoktur.
