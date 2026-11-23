"""Analiz 2 – Termal gecikme ve ısı birikimi.

Soru: Sıcaklık tüketime kaç saat gecikmeyle yansıyor; ısı birikimi kaç gün sürüyor?
Yöntem: 2024 yazında (Haz–Eyl) model A'nın (hava girdisiz) hatası, ağırlıklı ulusal hissedilen
sıcaklığın k saat önceki değeriyle ve son n günün ortalama soğutma derece-gününe göre ilişkilendirilir.
Gereksinim: önce 01_saatlik_ontest.py çalıştırılmalı.
Not: Model A geçmiş tüketimi girdi olarak kullandığından çok günlük etkinin bir kısmı gizlenmiş olabilir.
"""
import json
import pandas as pd
from ortak import RESULTS

r = pd.read_csv(RESULTS / "01_saatlik_tahminler.csv", index_col=0, parse_dates=True)
s = r["2024-06-01":"2024-09-30"]
hata = s.y - s.A_takvim
at = r.nat_at
saatlik = {k: round(float(hata.corr(at.shift(k).loc[s.index])), 3) for k in range(0, 9)}
dh, dat = hata.resample("D").mean(), at.resample("D").mean()
cdd = (dat - 22).clip(lower=0)
gunluk = {n: round(float(dh.corr(cdd.rolling(n).mean().loc[dh.index])), 3) for n in [1, 2, 3, 4, 5, 7, 10]}
out = {"saat_gecikmesi_korelasyon": saatlik, "son_n_gun_CDD_korelasyon": gunluk}
json.dump(out, open(RESULTS / "02_termal_gecikme.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
