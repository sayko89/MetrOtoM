# Jüri soruları ve cevaplarımız

Jürinin bizi en çok şu dört soruyla sıkıştıracağını varsayıyoruz: **"Bu gerçekten çalışıyor mu?"**, **"Veri nereden?"**, **"Yapay zekâ tam olarak ne yapıyor?"** ve **"Neden siz?"**. Cevaplar kısa ve ezberlenebilir tutuldu. Her rakamın kaynağı `results/` klasöründeki bir dosyadır; köşeli parantez içinde analiz numarası var.

**Altın kural:** Ölçmediğimiz bir şeyi ölçmüş gibi söylemiyoruz. "Hedefliyoruz" ile "ölçtük" ayrımını her cevapta koruyoruz.

---

## 1. Problem ve uyum

**1. MetrOtoM tam olarak ne yapıyor?**
→ Havayı 48 saat önceden okuyup perakende abone portföyünün saatlik tüketimini belirsizlik aralığıyla tahmin ediyor. Perakendeciye dengesizlik riskini ve fatura şoku yaşayacak aboneleri, aboneye de faturasını önceden gösteriyor.

**2. Neden perakende şirketi için önemli?**
→ Perakendeci enerjiyi önceden satın alıyor. Tahmin tutmazsa fark dengesizlik maliyeti olarak geri dönüyor. Hava, tüketimin en büyük dış etkeni; sıcak hava dalgası tam bu riski büyütüyor.

**3. Fatura şoku gerçekten var mı?**
→ Ege'nin dört ilinde (Manisa, Aydın, Denizli, Muğla) Nisan'dan Temmuz 2025'e mesken tüketimi günlük bazda %30 arttı [3]. İzmir'de Mayıs'tan Ağustos'a %88 [4]. 2026'dan itibaren yıllık 4.000 kWh'i aşan aboneler maliyet bazlı tarifeye geçti, bu da sıçramayı faturaya daha sert yansıtıyor.

**4. Müşteri kaybıyla ne ilgisi var?**
→ Ege'nin dört ilinde ticarethane tüketiminin %57–73'ü zaten serbest tüketicilerde; meskende bu oran dört ilin toplamında %3'ün altında [3]. Rekabet ticarethanede yoğun, meskende yeni başlıyor. Yüksek fatura alan abone geçmeye en yatkın abone.

**5. Neden sanayiye odaklanmıyorsunuz?**
→ Sanayi havaya az duyarlı: Nisan'dan Temmuz'a sadece %5 arttı [3]. Mesken (+%30), ticarethane (+%75) ve tarımsal sulama (~6 kat) havayla oynuyor. Bizim meteoroloji avantajımız bu segmentlerde işe yarıyor.

---

## 2. Veri ve uygulanabilirlik

**6. Verileri nereden aldınız?**
→ Hepsi açık veri. Tüketim, PTF ve SMF: EPİAŞ Şeffaflık Platformu. Hava: Open-Meteo (geçmiş için ERA5 tabanlı arşiv, 2 gün önceki tahminler için Previous Runs). Kentsel ısı adası: NASA MODIS, Google Earth Engine üzerinden.

**7. Abone verisi olmadan nasıl çalışacak?**
→ Prototip açık verilerle çalışıyor; ön testi de böyle yaptık. Pilot aşamada Aydem ve Gediz Perakende'nin anonimleştirilmiş akıllı sayaç verisiyle model yeniden eğitilecek. 2026'dan itibaren takılan sayaçlar akıllı, yani bu veri giderek artıyor.

**8. Bu sistem şu anda çalışıyor mu?**
→ Tahmin motoru çalışıyor ve geriye dönük test edildi; kodu ve sonuçları açık repoda. Perakende paneli ve abone bildirimi şu an tasarım aşamasında, mentörlük sürecinde prototipini çıkaracağız.

**9. KVKK?**
→ Yalnızca anonimleştirilmiş ve toplulaştırılmış veri işlenir. Abone bildirimi şirketin kendi kanalından gider; biz kişisel veriyi şirket dışına çıkarmıyoruz.

**10. Bölge bazlı saatlik veri yokken nasıl Ege için konuşuyorsunuz?**
→ Saatlik testi Türkiye geneliyle yaptık, çünkü bölge bazlı saatlik veri açık değil. Ege için il bazlı aylık veriyi kullandık [3, 4]. Bölge bazlı saatlik doğrulama pilotun ilk işi.

---

## 3. Model ve yapay zekâ

**11. Yapay zekâ tam olarak ne yapıyor?**
→ Hava ile tüketim arasındaki doğrusal olmayan, zamana bağlı ilişkiyi öğreniyor. Örneğin aynı 35°C, Pazartesi öğlen ile bayram gecesinde farklı tüketim demek; ardışık üçüncü sıcak gün ile ilk sıcak gün de farklı. Bunu kurallarla yazmak mümkün değil.

**12. Neden XGBoost?**
→ Ani sıcaklık değişimleri gibi dış etkenlerin doğrusal olmayan etkisini iyi yakalıyor, hızlı ve hangi girdinin ne kadar etkili olduğunu gösterebiliyor. Ön testi XGBoost ile yaptık.

**13. Neden LSTM de var?**
→ Tüketimdeki uzun zamana bağlı örüntüleri ve ısı birikimini öğrenmesi için. Tam projede XGBoost ile birleştirilecek; ön testte henüz kullanmadık.

**14. Model yanlış tahmin ederse?**
→ Tek bir sayı değil, %10–%90 belirsizlik aralığı üretiyoruz; riskli saatler açıkça görünüyor. Nihai alım kararını insan veriyor.

**15. Basit bir modelle karşılaştırdınız mı?**
→ Evet, iki temel modelle: "geçen haftanın aynı saati" (MAPE %5,64) ve havayı bilmeyen XGBoost (%4,66). Meteorolojik girdili model %4,41 [1].

---

## 4. Sonuçlar (en çok buradan sıkıştırılırız)

**16. Ön testte ne buldunuz?**
→ Meteorolojik girdiler 48 saatlik tahmin hatasını %4,66'dan %4,41'e indirdi; yaklaşık dengesizlik maliyeti tüm dönemde %11, yazın %14, sıcak hava dalgası günlerinde %22 azaldı [1].

**17. Ama gerçekleşen havayı kullanmışsınız, gerçekte tahmin kullanılır.**
→ Doğru, bu yüzden testi 2 gün önce yapılmış gerçek model tahminleriyle tekrarladık [1b]. Kazancın büyük kısmı korundu: maliyet tüm dönemde −%10, yazın −%13,5, sıcak günlerde −%14. Yazın neredeyse hiç fark yok; sıcak günlerde biraz düşüyor, çünkü tahminin en zor olduğu günler bunlar.

**18. Bu TL rakamları gerçek mi?**
→ Hayır, yaklaşık. Dengesizlik fiyatını PTF ve SMF'den %3 marjlı basitleştirilmiş bir kuralla hesapladık ve tüm Türkiye tüketimini tek portföy varsaydık. Bu yüzden **oran** olarak sunuyoruz, TL olarak değil.

**19. Kazanç her zaman var mı?**
→ Hayır. Meteorolojik model 45 haftanın 24'ünde daha iyi [1]. Kazanç sıcak dönemlerde yoğunlaşıyor. Zaten MetrOtoM'un değeri de tam bu dönemlerde; ılık bir Nisan haftasında hava zaten tahmini zorlamıyor.

**20. Neden 48 saat?**
→ Perakendecinin gün öncesi piyasada pozisyon alabilmesi ve aboneye davranışını değiştirecek kadar önceden haber verebilmek için. Erken uyarı, ancak önlem alınacak zaman bırakırsa işe yarar.

**21. Abone gerçekten tüketimini kaydırır mı?**
→ Bunu henüz ölçmedik; formdaki H3 hipotezi bu. Pilotta sınırlı bir abone grubunda bildirimlerin etkisini ölçeceğiz. Kaydırma olmasa bile tahmin ve müşteri kaybı listesi tek başına değer üretiyor.

---

## 5. Meteoroloji (meteoroloji mühendislerimiz cevaplar)

**22. Termal gecikme nedir, ne buldunuz?**
→ Sıcaklığın tüketime anında değil, binaların ısıl ataleti yüzünden gecikmeyle yansıması. En güçlü ilişki 1–2 saat önceki sıcaklıkla çıktı [2]. Isı birikimi ise 1–2 gün belirgin, 3–4 günde sönüyor.

**23. Mesken tüketimi neden en sıcak ay Temmuz'da değil Ağustos'ta zirve yapıyor?**
→ Ağustos'ta zirve var ama sıcaklık bunu açıklamıyor: İzmir'de Temmuz her göstergede daha sıcak (ortalama 31,3°C'ye karşı 29,5°C, geceler de daha sıcak) [4]. Aynı şehirde ticarethanede bu kayma yok. En olası açıklama sayaç okuma dönemi: 15 Ağustos'ta okunan sayaç Temmuz'un yarısını da kapsıyor. Bu, faturanın sıcak dönemden haftalar sonra geldiğini, yani uyarı için zaman olduğunu gösteriyor. Kesinleştirmek için günlük veri gerekiyor.

**24. Bunu ısı birikimi ya da kentsel ısı adası açıklamaz mı?**
→ Test ettik, açıklamıyor. Isı birikimi saat ve gün ölçeğinde çalışıyor, ay ölçeğinde değil. İzmir'de ısı adasının Temmuz–Ağustos farkı 0,2°C'nin altında [5]. Nemi hesaba katmak (hissedilen sıcaklık) açıklamayı biraz artırıyor (%60'tan %68'e) ama kaymayı kapatmıyor.

**25. Kentsel ısı adası projeye ne katıyor?**
→ Hava verisi 10–25 km'lik ızgaradan geliyor ve kenti kırsaldan ayıramıyor. MODIS uydu verisiyle İzmir'de yazın kent geceleri kırsaldan ortalama 1,7°C daha sıcak çıktı. Bu farkı hesaba katınca İzmir'in yaz gecesi soğutma ihtiyacı %38 artıyor; 25°C'nin üstünde geçen gece saati 501'den 635'e çıkıyor [5]. Yani standart hava verisi kent merkezindeki aboneyi düşük tahmin ediyor; biz bunu konuma göre düzeltiyoruz.

**26. Uydu hava sıcaklığını mı ölçüyor?**
→ Hayır, yüzey sıcaklığını ölçüyor. Geceleri ikisi birbirine yakın ama aynı değil; %38'lik rakam bu yaklaşıma dayanıyor. Ayrıca uydu yalnız bulutsuz günleri görüyor.

**27. Denizellik ne demek, ne buldunuz?**
→ Denizin sıcaklığı yumuşatma etkisi. İç kentlerde ısı adası yazın en güçlü; kıyıdaki Bodrum'da ise tersine yazın en zayıf (0,7°C), kışın en güçlü (1,1°C) [5]. Yazın deniz meltemi ve sıcak deniz kıyıdaki kırsalı da geceleri sıcak tutuyor, fark kapanıyor. Bu yüzden kıyı ve iç kentler için ayrı mevsimsel katsayı kullanıyoruz.

**28. FAO-56 / ET₀ nedir, neden var?**
→ Bitkinin buharlaşma ve terlemeyle kaybettiği suyu hava verisinden hesaplayan standart yöntem (FAO-56 Penman-Monteith). Tarımsal sulama pompalarının ne zaman çalışacağını öngörmek için kullanıyoruz. Sulama tüketimi Nisan'dan Temmuz'a yaklaşık 6 kat artıyor [3].

**29. Ege şehirlerinin hava verisi gerçekten fark yaratıyor mu?**
→ Türkiye geneli testte Ege şehirlerini çıkarınca sıcak günlerdeki maliyet yaklaşık %3 kötüleşiyor [1]. Küçük ama ölçülebilir; bölge bazlı tüketimde bu payın çok daha büyük olmasını bekliyoruz, ama bunu henüz ölçmedik.

---

## 6. İş modeli, rakipler, ekip

**30. Bunu kim, neden satın alır?**
→ Önce Aydem ve Gediz Perakende'de pilot. Sonra piyasadaki tüm perakende tedarikçiler, çünkü hepsi aynı dengesizlik riskini taşıyor. Gelir modeli (varsayım): abone sayısına göre fiyatlanan yıllık yazılım lisansı.

**31. Piyasada talep tahmini yapan çözümler zaten yok mu?**
→ Var. Bizim farkımız üç şey: (1) meteoroloji uzmanlığıyla kurulan girdiler (termal gecikme, ısı adası, kıyı etkisi, ET₀), (2) aynı tahmini hem tedarikçiye hem aboneye çevirmek, (3) hava ile müşteri kaybını birbirine bağlamak.

**32. Aydem ve Gediz zaten yapay zekâ kullanıyor.**
→ Evet, örneğin çağrı merkezinde ayda yaklaşık 100 bin çağrıyı ses analiziyle inceliyorlar. MetrOtoM onu tamamlıyor: fatura kaynaklı çağrıyı fatura gelmeden önlemeye çalışıyor.

**33. ENERCAST ile ilişkisi ne?**
→ ENERCAST, ADM ve GDZ Elektrik'in yarışmasında 4. olan şebeke (trafo) erken uyarı projemizdi. MetrOtoM ayrı bir proje: hedefi şebeke değil, perakende tarafı ve abone. O deneyimden meteorolojiyi enerjiye bağlama becerisini ve oradaki eksikliğimizden ders aldık: bu kez ölçülmüş sonuçla geliyoruz.

**34. Neden siz?**
→ Üç meteoroloji mühendisi ve bir yazılım mühendisiyiz. Havanın tüketimi nasıl etkilediğini fiziksel olarak açıklayabilen ve bunu çalışan bir sisteme dökebilen bir ekibiz. Başvuru aşamasında altı analizi açık verilerle yaptık; kodu herkese açık.

**35. 12 aylık veriyle bu sonuçlara güvenilir mi?**
→ Aylık analizler ön bulgu; bunu açıkça söylüyoruz. Saatlik test ise binlerce saat üzerinde (Mart–Aralık 2024, 7.344 saat) ve iki ayrı hava kaynağıyla tutarlı.

---

## Ezberlenecek 5 cevap

1. **"Farkınız ne?"** → Meteoroloji uzmanlığıyla kurulan girdiler ve aynı tahmini hem tedarikçiye hem aboneye çevirmek.
2. **"Gerçekten işe yarıyor mu?"** → 2 gün önceki gerçek hava tahminiyle bile yazın dengesizlik maliyeti −%13,5, sıcak günlerde −%14.
3. **"Neden 48 saat?"** → Pozisyon almak ve aboneye önlem alacak zaman bırakmak için.
4. **"En büyük sınırlılığınız?"** → Bölge bazlı saatlik veriye erişim; pilotun ilk işi bu.
5. **"En büyük değeriniz?"** → Sıcağı tahmin etmek değil, tahmini perakendecinin ve abonenin eylemine dönüştürmek.

**Tek cümle:** *MetrOtoM, havayı 48 saat önceden okuyarak perakendeciye pozisyonunu, aboneye faturasını önceden gösterir; abone tüketimini kaydırdıkça dengesizlik maliyeti ve müşteri kaybı birlikte düşer.*
