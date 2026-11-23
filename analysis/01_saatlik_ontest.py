"""Analiz 1 – Saatlik ön test.

Soru: Meteorolojik girdiler, 48 saat önceden yapılan saatlik tüketim tahminini ve
dengesizlik maliyetini ne kadar iyileştiriyor?

Yöntem: Mart–Aralık 2024 boyunca her hafta, o haftadan 48 saat öncesine kadar bilinen
veriyle XGBoost yeniden eğitilir ve haftanın saatleri tahmin edilir (genişleyen pencere).
  naive : geçen haftanın aynı saati
  A     : takvim + ≥48 saat gecikmeli tüketim
  B     : A + 7 şehrin meteorolojik girdileri
  C     : B'den Ege şehirleri çıkarılmış hali (Ege'nin katkısını ölçmek için)
Dengesizlik maliyeti yaklaşık kuralla hesaplanır: eksik alım max(PTF,SMF)*1,03 ile,
fazla alım min(PTF,SMF)*0,97 ile kapatılır.

Not: Hava girdisi olarak gerçekleşen (arşiv) değerler kullanılmıştır; gerçek hava tahminiyle
kazanç bir miktar azalabilir. Tüketim Türkiye genelidir.
Çalışma süresi ~3 dk.
"""
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from ortak import RESULTS, SEHIRLER, EGE, hava, epias_saatlik

df = epias_saatlik()
idx = df.index

# --- Meteorolojik girdiler
wx = pd.DataFrame(index=idx)
for c in SEHIRLER:
    m = hava(c).reindex(idx)
    wx[f"{c}_t"], wx[f"{c}_at"], wx[f"{c}_rh"] = m.t, m["at"], m.rh
    wx[f"{c}_rad"], wx[f"{c}_cc"] = m.rad, m.cc
    wx[f"{c}_cdh"] = (m["at"] - 22).clip(lower=0)                 # soğutma derece-saati (hissedilen)
    wx[f"{c}_hdh"] = (15 - m.t).clip(lower=0)                     # ısıtma derece-saati
    wx[f"{c}_t_lag2"] = m.t.shift(2)                              # termal gecikme
    wx[f"{c}_t_24"] = m.t.rolling(24, min_periods=1).mean()       # ısı birikimi (gün)
    wx[f"{c}_cdh_72"] = wx[f"{c}_cdh"].rolling(72, min_periods=1).mean()  # ardışık sıcak günler
W = {"istanbul": .45, "ankara": .2, "izmir": .15, "manisa": .05, "aydin": .05, "denizli": .05, "bodrum": .05}
for v in ["t", "at", "cdh", "hdh", "rad"]:
    wx[f"nat_{v}"] = sum(W[c] * wx[f"{c}_{v}"] for c in W)
wx["nat_cdh_72"] = wx.nat_cdh.rolling(72, min_periods=1).mean()

# --- Takvim (2024 resmî tatil ve bayramlar)
cal = pd.DataFrame(index=idx)
cal["hour"], cal["dow"], cal["doy"], cal["month"] = idx.hour, idx.dayofweek, idx.dayofyear, idx.month
hol2 = pd.to_datetime(["2024-01-01", "2024-04-23", "2024-05-01", "2024-05-19", "2024-07-15", "2024-08-30", "2024-10-29"]
                      + [f"2024-04-{d:02d}" for d in range(10, 13)] + [f"2024-06-{d}" for d in range(16, 20)])
hol1 = pd.to_datetime(["2024-04-08", "2024-04-09", "2024-04-13", "2024-04-14", "2024-06-15", "2024-06-20",
                       "2024-06-21", "2024-10-28", "2024-12-31"])
day = idx.normalize()
cal["holiday"] = np.where(day.isin(hol2), 2, np.where(day.isin(hol1), 1, 0))

# --- Gecikmeli tüketim (≥48 saat: tahmin anında bilinen)
lag = pd.DataFrame(index=idx)
for L in [48, 72, 96, 168, 336]:
    lag[f"y_l{L}"] = df.y.shift(L)
lag["y_l168_mean"] = df.y.shift(48).rolling(168, min_periods=24).mean()

FA = list(cal.columns) + list(lag.columns)
F_WX = list(wx.columns)
F_WX_EGESIZ = [c for c in wx.columns if not any(c.startswith(e + "_") for e in EGE) and not c.startswith("nat_")]
data = pd.concat([cal, lag, wx, df], axis=1).dropna(subset=FA + ["y"])

PARAMS = dict(n_estimators=600, max_depth=6, learning_rate=0.04, subsample=0.8, colsample_bytree=0.8,
              min_child_weight=5, reg_lambda=1.0, n_jobs=8, random_state=42)


def backtest(feats, start="2024-03-01", end="2025-01-01"):
    preds = []
    for a in pd.date_range(start, end, freq="7D"):
        b = min(a + pd.Timedelta(days=7), pd.Timestamp(end))
        tr = data[data.index < a - pd.Timedelta(hours=48)]
        te = data[(data.index >= a) & (data.index < b)]
        if len(te):
            m = xgb.XGBRegressor(**PARAMS).fit(tr[feats], tr.y)
            preds.append(pd.Series(m.predict(te[feats]), index=te.index))
    return pd.concat(preds)


res = data.loc[data.index >= "2024-03-01", ["y", "ptf", "smf", "nat_at"]].copy()
res["naive"] = data.y_l168
res["A_takvim"] = backtest(FA)
res["B_meteo"] = backtest(FA + F_WX)
res["C_meteo_egesiz"] = backtest(FA + F_WX_EGESIZ)
res.to_csv(RESULTS / "01_saatlik_tahminler.csv")


def mape(a, p):
    return float(np.mean(np.abs(a - p) / a) * 100)


def dengesizlik(r, col):
    e = r.y - r[col]
    eksik = e.clip(lower=0) * (np.maximum(r.ptf, r.smf) * 1.03 - r.ptf)
    fazla = (-e).clip(lower=0) * (r.ptf - np.minimum(r.ptf, r.smf) * 0.97)
    return float((eksik + fazla).sum())


gunluk_at = res.nat_at.resample("D").max()
yaz = gunluk_at["2024-06-01":"2024-09-30"]
sicak = yaz[yaz >= yaz.quantile(.8)].index
segs = {"tum_test_mar_ara": res, "yaz_haz_eyl": res["2024-06-01":"2024-09-30"],
        "sicak_hava_dalgasi_gunleri": res[res.index.normalize().isin(sicak)]}
out = {}
for name, r in segs.items():
    out[name] = {m: {"MAPE": round(mape(r.y, r[m]), 2), "dengesizlik_TL": round(dengesizlik(r, m))}
                 for m in ["naive", "A_takvim", "B_meteo", "C_meteo_egesiz"]}
    out[name]["saat"] = len(r)
ape = lambda c: (res.y - res[c]).abs() / res.y
wk = pd.DataFrame({c: ape(c).resample("W").mean() for c in ["A_takvim", "B_meteo"]})
out["haftalik"] = {"hafta": len(wk), "B_daha_iyi": int((wk.B_meteo < wk.A_takvim).sum())}
out["sicak_gun_sayisi"] = len(sicak)
json.dump(out, open(RESULTS / "01_saatlik_ontest.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
