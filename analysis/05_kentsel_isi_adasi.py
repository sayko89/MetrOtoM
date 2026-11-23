"""Analiz 5 – Kentsel ısı adası (KIA) ve denizellik.

Veri: MODIS MOD11A2 1 km yüzey sıcaklığı, gee/kentsel_isi_adasi.js ile Google Earth Engine'den
(5 şehir, 2024–2025 aylık; kent pikselleri ve benzer yükseklikteki kırsal pikseller).
Hipotezler:
  H-a: Gece KIA Ağustos'ta Temmuz'dan güçlü mü? (Ağustos mesken zirvesini açıklar mı)
  H-b: Kıyı ve iç kentlerde KIA'nın mevsimsel deseni farklı mı? (denizellik)
  H-c: KIA eklenince İzmir aylık mesken modelinin açıklama gücü artıyor mu?
Ek: İzmir'de yaz gecesi saatlerine KIA (yaz ort.) eklenince soğutma derece-saati ne kadar artıyor?
Not: Uydu yüzey sıcaklığını ölçer; gece hava sıcaklığına yakındır ama aynı değildir.
"""
import json
import numpy as np
import pandas as pd
from ortak import DATA, RESULTS, GUN, epias_il, hava, r2

k = pd.read_csv(DATA / "modis" / "kentsel_isi_adasi_2024_2025.csv")
k["kia_gece"] = k.kent_gece_C - k.kirsal_gece_C
k["kia_gunduz"] = k.kent_gunduz_C - k.kirsal_gunduz_C
k["yil"], k["ay"] = k.ay.str[:4].astype(int), k.ay.str[5:].astype(int)
mevsim = lambda a: "yaz" if a in (6, 7, 8) else ("kis" if a in (12, 1, 2) else "ara")
k["mevsim"] = k.ay.map(mevsim)
out = {"ortalama_KIA": k.groupby("sehir")[["kia_gece", "kia_gunduz"]].mean().round(2).to_dict(),
       "gece_KIA_mevsim": k.pivot_table(index="sehir", columns="mevsim", values="kia_gece").round(2).to_dict(),
       "H_a_temmuz_agustos": {s: {str(y): {"Tem": round(float(g[(g.yil == y) & (g.ay == 7)].kia_gece.iloc[0]), 2),
                                           "Agu": round(float(g[(g.yil == y) & (g.ay == 8)].kia_gece.iloc[0]), 2)}
                                  for y in (2024, 2025)} for s, g in k.groupby("sehir")}}

# H-c: İzmir 2025 aylık mesken
d = epias_il()
mes = d[(d.il == "izmir") & (d.yil == 2025) & (d.segment == "Mesken")].groupby("ay").toplam.sum() / GUN
t = hava("izmir").loc["2025"].t.resample("D").mean()
cdd = (t - 22).clip(lower=0).groupby(t.index.month).sum() / GUN
hdd = (15 - t).clip(lower=0).groupby(t.index.month).sum() / GUN
kia = k[(k.sehir == "Izmir") & (k.yil == 2025)].set_index("ay").kia_gece
y = mes.values


def adj_r2(X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rr = r2(y, X @ b)
    p = X.shape[1] - 1
    return round(rr, 2), round(1 - (1 - rr) * (len(y) - 1) / (len(y) - p - 1), 2)


out["H_c_izmir_mesken"] = {"CDD+HDD": adj_r2(np.c_[np.ones(12), cdd, hdd]),
                           "CDD+HDD+KIA": adj_r2(np.c_[np.ones(12), cdd, hdd, kia.values])}

# Izgara verisinin kaçırdığı gece soğutma ihtiyacı (İzmir, yaz 2025)
kia_yaz = float(k[(k.sehir == "Izmir") & (k.mevsim == "yaz")].kia_gece.mean())
h = hava("izmir").loc["2025-06":"2025-08"].t
gece = (h.index.hour >= 22) | (h.index.hour < 6)
base, adj = (h - 22).clip(lower=0), (h + gece * kia_yaz - 22).clip(lower=0)
out["izmir_yaz_KIA_duzeltmesi"] = {
    "kia_yaz_C": round(kia_yaz, 2),
    "gece_CDH_artis_%": round((adj[gece].sum() / base[gece].sum() - 1) * 100, 1),
    "toplam_CDH_artis_%": round((adj.sum() / base.sum() - 1) * 100, 1),
    "gece_25C_ustu_saat": [int((h[gece] > 25).sum()), int((h[gece] + kia_yaz > 25).sum())]}
json.dump(out, open(RESULTS / "05_kentsel_isi_adasi.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
