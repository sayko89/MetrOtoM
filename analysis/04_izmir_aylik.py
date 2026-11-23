"""Analiz 4 – Aylık hava–tüketim ilişkisi (İzmir 2025, 12 ay).

Soru: Soğutma ve ısıtma derece-günleri aylık tüketimin ne kadarını açıklıyor; mesken
tüketimi sıcaklığa gecikmeyle mi yanıt veriyor?
Yöntem: Günlük ortalama tüketim ~ sabit + günlük ort. CDD(22°C) + günlük ort. HDD(15°C), en küçük kareler.
"ayni_ay": o ayın havası; "onceki_ay": bir önceki ayın havası; "iki_ay_ort": ikisinin ortalaması.
Ayrıca hissedilen sıcaklıkla CDD ve Temmuz/Ağustos ısı göstergeleri.
Not: 12 gözlem; sonuçlar ön bulgudur.
"""
import json
import numpy as np
import pandas as pd
from ortak import RESULTS, GUN, epias_il, hava, r2

d = epias_il()
d = d[(d.il == "izmir") & (d.yil == 2025)]
p = d.pivot_table(index="ay", columns="segment", values="toplam", aggfunc="sum").div(GUN, axis=0)
h = hava("izmir").loc["2025"]
t, at = h.t.resample("D").mean(), h["at"].resample("D").mean()
m = pd.DataFrame({"T": t.groupby(t.index.month).mean(),
                  "CDDd": (t - 22).clip(lower=0).groupby(t.index.month).sum() / GUN,
                  "HDDd": (15 - t).clip(lower=0).groupby(t.index.month).sum() / GUN,
                  "CDDd_hiss": (at - 22).clip(lower=0).groupby(at.index.month).sum() / GUN})
onceki = lambda s: s.shift(1, fill_value=s.iloc[-1])


def fit(y, *cols):
    X = np.c_[np.ones(len(y)), *cols]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return round(r2(y, X @ b), 2), b


out = {"aylik_gunluk_tuketim_MWh": p[["Mesken", "Ticarethane", "Tarımsal Sulama", "Sanayi"]].round(0).to_dict(),
       "aylik_ort_sicaklik_C": m["T"].round(1).to_dict(), "R2": {}}
for seg in ["Mesken", "Ticarethane", "Sanayi"]:
    y = p[seg].values
    out["R2"][seg] = {
        "ayni_ay": fit(y, m.CDDd, m.HDDd)[0],
        "onceki_ay": fit(y, onceki(m.CDDd), onceki(m.HDDd))[0],
        "iki_ay_ort": fit(y, (m.CDDd + onceki(m.CDDd)) / 2, (m.HDDd + onceki(m.HDDd)) / 2)[0],
        "ayni_ay_hissedilen": fit(y, m.CDDd_hiss, m.HDDd)[0],
    }
r2v, b = fit(p.Mesken.values, (m.CDDd + onceki(m.CDDd)) / 2, (m.HDDd + onceki(m.HDDd)) / 2)
out["mesken_her_1_CDD_gun_basina_artis_%"] = round(b[1] / b[0] * 100, 1)
out["mesken_mayis_agustos_artis_%"] = round((p.Mesken[8] / p.Mesken[5] - 1) * 100, 1)

# Temmuz ve Ağustos ısı göstergeleri
gost = {}
for mo in (7, 8):
    x = h[h.index.month == mo]
    gece = x[(x.index.hour >= 22) | (x.index.hour < 6)]
    gost[mo] = {"ort_T": round(x.t.mean(), 1), "ort_Tmin": round(x.t.resample("D").min().mean(), 1),
                "gece_hissedilen": round(gece["at"].mean(), 1), "gece_25C_ustu_saat": int((gece["at"] > 25).sum()),
                "nem_%": round(x.rh.mean())}
out["temmuz_agustos_gostergeler"] = gost
m.round(2).join(p.round(0)).to_csv(RESULTS / "04_izmir_aylik_tablo.csv")
json.dump(out, open(RESULTS / "04_izmir_aylik.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
