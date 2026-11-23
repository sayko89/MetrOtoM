"""Analiz 3 – Segment duyarlılığı (Ege'nin 4 ili, Nisan → Temmuz 2025).

Soru: Hangi tüketici segmenti sıcak aylarda ne kadar artıyor; serbest tüketici payı nedir?
Veri: EPİAŞ Şeffaflık > Tüketici Bilgisi > Tüketim Miktarları (il bazlı, aylık).
Gün sayısı farkı için günlük ortalamaya çevrilir (Nisan 30, Temmuz 31 gün).
"""
import json
from ortak import RESULTS, GUN, epias_il

d = epias_il()
d = d[d.il.isin(["manisa", "aydin", "denizli", "mugla"]) & d.ay.isin([4, 7])]
g = d.groupby(["segment", "ay"]).toplam.sum().unstack()
g["gunluk_degisim_%"] = ((g[7] / GUN[7]) / (g[4] / GUN[4]) - 1) * 100
il = d[d.segment == "Mesken"].groupby(["il", "ay"]).toplam.sum().unstack()
il["gunluk_degisim_%"] = ((il[7] / GUN[7]) / (il[4] / GUN[4]) - 1) * 100
tem = d[d.ay == 7].groupby(["segment", "il"])[["serbest", "toplam"]].sum()
tem["serbest_pay_%"] = tem.serbest / tem.toplam * 100
out = {"segment_gunluk_degisim_%": g["gunluk_degisim_%"].round(1).to_dict(),
       "mesken_il_gunluk_degisim_%": il["gunluk_degisim_%"].round(1).to_dict(),
       "temmuz_serbest_tuketici_payi_%": {f"{s}/{i}": round(v, 1) for (s, i), v in tem["serbest_pay_%"].items()
                                           if s in ("Mesken", "Ticarethane")}}
json.dump(out, open(RESULTS / "03_segment_duyarlilik.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
