# MetrOtoM

**Meteoroloji tabanlı talep tahmini ile perakende elektrik tedarikçileri ve aboneleri için erken uyarı platformu**

Yenilikçi Fikirler Kampı 2026 (Ege Teknopark · Aydem Perakende · Gediz Perakende) başvurusu.
Tema: *Yapay Zekâ ve Otonom Enerji Sistemleri — Talep tahmini, dinamik tarife ve enerji ticareti modelleri.*

Bu repo, başvuru aşamasında açık verilerle yaptığımız ön analizlerin kodunu, verisini ve sonuçlarını içerir. Tüm sonuçlar aşağıdaki komutlarla yeniden üretilebilir.

---

## Problem

Ege'de sıcak hava dalgaları elektrik tüketimini kısa sürede ve öngörülemez biçimde artırıyor. Perakende tedarikçi için bu üç soruna dönüşüyor:

1. **Dengesizlik maliyeti:** Önceden satın alınan enerji ile gerçekleşen tüketim arasındaki fark, piyasada maliyet olarak geri döner.
2. **Fatura şoku:** Sıcak dönemden sonra gelen yüksek faturalar şikâyet, geç ödeme ve memnuniyetsizlik yaratır.
3. **Müşteri kaybı riski:** Serbest tüketici limiti düştükçe yüksek fatura alan abone başka tedarikçiye geçebilir.

## Çözüm

Tek bir tahmin motoru, iki çıktı:

- **Perakende paneli:** Abone portföyünün 48 saatlik saatlik tüketim tahmini, belirsizlik aralığı, dengesizlik risk uyarısı ve fatura şoku yaşayacak aboneler için müşteri kaybı risk listesi.
- **Abone bildirimi:** Faturanın önceden gösterilmesi ve klima ya da sulama pompası kullanımını güneşli, ucuz saatlere kaydırma önerisi.

Abone tüketimini kaydırdıkça portföy talebi daha öngörülebilir hale gelir; dengesizlik maliyeti ve müşteri kaybı birlikte azalır.

Meteorolojik girdiler meteoroloji mühendislerimizce tasarlanır: hissedilen sıcaklık, soğutma ve ısıtma derece-saatleri, termal gecikme, ısı birikimi, güneşlenme, FAO-56 buharlaşma-terleme (tarımsal sulama), kentsel ısı adası düzeltmesi ve kıyı–iç kent (denizellik) ayrımı.

---

## Ön analizler ve bulgular

![Şekil 1](figures/sekil1_on_analizler.png)

*Şekil 1. (a) 48 saat önceden saatlik tahmin, meteorolojik girdisiz (A) ve girdili (B) model; (b) İzmir 2025 aylık mesken ve ticarethane tüketimi; (c) gece kentsel ısı adası şiddeti.*

| # | Analiz ve veri | Bulgu | MetrOtoM'a etkisi |
|---|---|---|---|
| 1 | **Saatlik ön test** — EPİAŞ 2024 Türkiye geneli saatlik tüketim, PTF, SMF; 7 şehrin saatlik hava verisi | MAPE %4,66 → %4,41; sıcak hava dalgası günlerinde %4,89 → %4,30. Yaklaşık dengesizlik maliyeti: tüm dönem −%11, yaz −%14, sıcak günler −%22 | Meteorolojik girdiler tahmin motorunun çekirdeği |
| 2 | **Termal gecikme ve ısı birikimi** — aynı veri | En güçlü ilişki 1–2 saat önceki sıcaklıkla; ısı birikimi etkisi 1–2 gün belirgin, 3–4 günde sönüyor | 2 saatlik gecikme ve çok günlük birikim girdileri |
| 3 | **Segment duyarlılığı** — EPİAŞ il bazlı aylık veri; Manisa, Aydın, Denizli, Muğla; Nisan → Temmuz 2025 | Günlük tüketim: mesken +%30, ticarethane +%75, tarımsal sulama ~6 kat, sanayi +%5. Ticarethanede serbest tüketici payı %57–73, meskende 4 ilin toplamında %3'ün altında | Mesken, ticarethane ve sulama odaklı segment modelleri |
| 4 | **Aylık hava–tüketim ilişkisi** — İzmir 2025, 12 ay | Derece-günler ticarethanedeki aylık değişimin %92'sini, meskendekinin %82'sini açıklıyor. Mesken zirvesi en sıcak aydan (Temmuz) bir ay sonra (Ağustos); büyük olasılıkla sayaç okuma dönemi | Fatura sıcaktan haftalar sonra geliyor: erken uyarı penceresi |
| 5 | **Kentsel ısı adası** — MODIS 1 km yüzey sıcaklığı, 5 şehir, 2024–2025 | Gece kent–kırsal farkı İzmir'de yazın 1,7°C. Izgara hava verisi İzmir'de yaz gecesi soğutma ihtiyacını yaklaşık %38 düşük gösteriyor. Ağustos mesken zirvesini açıklamıyor | Abone konumuna göre ısı adası düzeltme katsayısı |
| 6 | **Denizellik** — MODIS, kıyı ve iç kentler | İç kentlerde ısı adası yazın en güçlü; kıyıdaki Bodrum'da yazın en zayıf (0,7°C), kışın en güçlü (1,1°C) | Kıyı ve iç kentler için ayrı mevsimsel katsayı |

Ayrıntılı sayılar `results/` klasöründeki JSON ve CSV dosyalarındadır.

### Dikkat edilmesi gerekenler

- Saatlik testte hava girdisi olarak **gerçekleşen** hava değerleri kullanıldı; gerçek hava tahminiyle kazanç bir miktar azalabilir.
- Saatlik tüketim **Türkiye geneli**dir; bölge bazlı saatlik veri açık değildir.
- Model B, 45 haftanın 24'ünde model A'dan daha iyi; kazanç özellikle sıcak dönemlerde ortaya çıkıyor.
- Dengesizlik maliyeti, PTF ve SMF ile %3 marjlı basitleştirilmiş bir kuralla **yaklaşık** hesaplandı. TL değerleri tüm Türkiye tüketimini tek bir portföy varsayar; oran olarak yorumlanmalıdır.
- Aylık analizler 12 gözleme dayanır; sonuçlar **ön bulgudur**.
- MODIS **yüzey** sıcaklığını ölçer; gece hava sıcaklığına yakındır ama aynı değildir. Sadece bulutsuz günleri görür.

---

## Klasör yapısı

```
analysis/
  ortak.py                     veri yükleme yardımcıları
  01_saatlik_ontest.py         saatlik ön test (genişleyen pencere, XGBoost) ~3 dk
  02_termal_gecikme.py         saat ve gün ölçeğinde gecikme
  03_segment_duyarlilik.py     4 il, Nisan → Temmuz 2025
  04_izmir_aylik.py            İzmir 2025 aylık hava–tüketim regresyonu
  05_kentsel_isi_adasi.py      ısı adası, denizellik, ızgara düzeltmesi
  06_sekil.py                  Şekil 1
gee/
  kentsel_isi_adasi.js         Google Earth Engine kodu (MODIS verisini üretir)
data/
  epias/                       2024 saatlik tüketim, PTF, SMF
  epias_il/                    il bazlı aylık Tüketim Miktarları (2025)
  hava/                        7 şehir saatlik hava verisi (2024–2025)
  modis/                       kentsel ısı adası çıktısı (2024–2025)
results/                       analiz çıktıları (JSON, CSV)
figures/                       grafikler
```

## Çalıştırma

```bash
pip install -r requirements.txt
cd analysis
python 01_saatlik_ontest.py
python 02_termal_gecikme.py
python 03_segment_duyarlilik.py
python 04_izmir_aylik.py
python 05_kentsel_isi_adasi.py
python 06_sekil.py
```

MODIS verisini yeniden üretmek için `gee/kentsel_isi_adasi.js` dosyasını [Google Earth Engine Code Editor](https://code.earthengine.google.com)'a yapıştırıp çalıştırın; Tasks sekmesinden CSV'yi dışa aktarın.

## Veri kaynakları

| Veri | Kaynak |
|---|---|
| Saatlik gerçek zamanlı tüketim, PTF, SMF | [EPİAŞ Şeffaflık Platformu](https://seffaflik.epias.com.tr) |
| İl bazlı aylık tüketim miktarları (profil grubuna göre) | EPİAŞ Şeffaflık Platformu › Elektrik Tüketim › Tüketici Bilgisi › Tüketim Miktarları (veri kaynağı: dağıtım şirketleri) |
| Saatlik hava verisi | [Open-Meteo Historical Weather API](https://open-meteo.com) (CC BY 4.0) |
| Yüzey sıcaklığı | NASA MODIS MOD11A2 v061, arazi örtüsü MCD12Q1, yükseklik SRTM; Google Earth Engine üzerinden |

EPİAŞ verileri kaynak gösterilerek kullanılabilir. Veriler bu repoda yalnızca analizlerin tekrarlanabilmesi için bulunmaktadır.

## Yöntem kaynakları

- Allen, R.G. vd. (1998). *Crop Evapotranspiration – FAO Irrigation and Drainage Paper 56.* FAO.
- Hersbach, H. vd. (2020). The ERA5 global reanalysis. *QJRMS*, 146(730), 1999–2049.
- Chen, T., Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD '16*.
- Hochreiter, S., Schmidhuber, J. (1997). Long Short-Term Memory. *Neural Computation*, 9(8).
- Hong, T., Fan, S. (2016). Probabilistic electric load forecasting: A tutorial review. *IJF*, 32(3).

## Ekip

Samsun Üniversitesi

- **Safiye Özkan** — Yazılım Mühendisliği
- **Zeynep Dikbaş** — İklim Bilimi ve Meteoroloji Mühendisliği
- **Nida Özen** — İklim Bilimi ve Meteoroloji Mühendisliği
- **Ceyda Köprülü** — İklim Bilimi ve Meteoroloji Mühendisliği
