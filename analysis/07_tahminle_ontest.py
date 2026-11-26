"""Analiz 7 – Gerçek hava tahminiyle ön test.

Soru: Analiz 1'deki kazanç, hava için gerçekleşen değerler yerine 2 gün önce yapılmış
tahminler kullanıldığında da sürüyor mu? (Sistemin gerçek çalışma koşulu budur.)

Veri: Open-Meteo Previous Runs API, "previous_day2" değişkenleri: her saat için 2 gün önceki
model koşusunun tahmini (1 Mart – 31 Aralık 2024, 7 şehir).
Yöntem: Analiz 1 ile aynı genişleyen pencere (haftalık yeniden eğitim, 48 saat önceden).
  A          : takvim + ≥48 saat gecikmeli tüketim (hava yok)
  B_gercek   : A + gerçekleşen hava (üst sınır; Analiz 1'deki B'nin karşılığı)
  B_tahmin   : eğitim gerçekleşen havayla, test haftası 2 gün önceki tahminle
Tutarlılık için hissedilen sıcaklık iki veri setinde de aynı formülle (BoM/Steadman) hesaplanır,
bu yüzden B_gercek sayıları Analiz 1'deki B'den biraz farklı olabilir.
Çalışma süresi ~3 dk.
"""
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from ortak import DATA, RESULTS, SEHIRLER, hava, epias_saatlik

df = epias_saatlik()
idx = df.index


def hissedilen(t, rh, ws_kmh):
    e = rh / 100 * 6.105 * np.exp(17.27 * t / (237.7 + t))
    return t + 0.33 * e - 0.70 * (ws_kmh / 3.6) - 4.0


def tahmin(sehir):
    d = pd.read_csv(DATA / "hava_tahmin" / f"{sehir}_2gun_once_2024.csv", skiprows=3, parse_dates=["time"]).set_index("time")
    d.columns = ["t", "rh", "cc", "rad", "ws"]
    return d


def oznitelik(kaynak):
    wx = pd.DataFrame(index=idx)
    for c in SEHIRLER:
        m = kaynak(c).reindex(idx)
        at = hissedilen(m.t, m.rh, m.ws)
        wx[f"{c}_t"], wx[f"{c}_at"], wx[f"{c}_rh"], wx[f"{c}_rad"], wx[f"{c}_cc"] = m.t, at, m.rh, m.rad, m.cc
        wx[f"{c}_cdh"] = (at - 22).clip(lower=0)
        wx[f"{c}_hdh"] = (15 - m.t).clip(lower=0)
        wx[f"{c}_t_lag2"] = m.t.shift(2)
        wx[f"{c}_t_24"] = m.t.rolling(24, min_periods=1).mean()
        wx[f"{c}_cdh_72"] = wx[f"{c}_cdh"].rolling(72, min_periods=1).mean()
    W = {"istanbul": .45, "ankara": .2, "izmir": .15, "manisa": .05, "aydin": .05, "denizli": .05, "bodrum": .05}
    for v in ["t", "at", "cdh", "hdh", "rad"]:
        wx[f"nat_{v}"] = sum(W[c] * wx[f"{c}_{v}"] for c in W)
    wx["nat_cdh_72"] = wx.nat_cdh.rolling(72, min_periods=1).mean()
    return wx


wx_obs = oznitelik(hava)
wx_fc = oznitelik(tahmin)

cal = pd.DataFrame(index=idx)
cal["hour"], cal["dow"], cal["doy"], cal["month"] = idx.hour, idx.dayofweek, idx.dayofyear, idx.month
hol2 = pd.to_datetime(["2024-01-01", "2024-04-23", "2024-05-01", "2024-05-19", "2024-07-15", "2024-08-30", "2024-10-29"]
                      + [f"2024-04-{d:02d}" for d in range(10, 13)] + [f"2024-06-{d}" for d in range(16, 20)])
hol1 = pd.to_datetime(["2024-04-08", "2024-04-09", "2024-04-13", "2024-04-14", "2024-06-15", "2024-06-20",
                       "2024-06-21", "2024-10-28", "2024-12-31"])
day = idx.normalize()
cal["holiday"] = np.where(day.isin(hol2), 2, np.where(day.isin(hol1), 1, 0))
lag = pd.DataFrame(index=idx)
for L in [48, 72, 96, 168, 336]:
    lag[f"y_l{L}"] = df.y.shift(L)
lag["y_l168_mean"] = df.y.shift(48).rolling(168, min_periods=24).mean()

FA = list(cal.columns) + list(lag.columns)
FW = list(wx_obs.columns)
obs = pd.concat([cal, lag, wx_obs, df], axis=1).dropna(subset=FA + ["y"])
fc = pd.concat([cal, lag, wx_fc, df], axis=1).dropna(subset=FA + ["y"])

PARAMS = dict(n_estimators=600, max_depth=6, learning_rate=0.04, subsample=0.8, colsample_bytree=0.8,
              min_child_weight=5, reg_lambda=1.0, n_jobs=8, random_state=42)


def backtest(feats, test_data, start="2024-03-01", end="2025-01-01"):
    preds = []
    for a in pd.date_range(start, end, freq="7D"):
        b = min(a + pd.Timedelta(days=7), pd.Timestamp(end))
        tr = obs[obs.index < a - pd.Timedelta(hours=48)]           # eğitim: gerçekleşen hava
        te = test_data[(test_data.index >= a) & (test_data.index < b)]
        if len(te):
            m = xgb.XGBRegressor(**PARAMS).fit(tr[feats], tr.y)
            preds.append(pd.Series(m.predict(te[feats]), index=te.index))
    return pd.concat(preds)


res = obs.loc[obs.index >= "2024-03-01", ["y", "ptf", "smf"]].copy()
# Sıcak gün tanımı Analiz 1 ile aynı olsun diye Open-Meteo arşivinin hissedilen sıcaklığı kullanılır
W_ = {"istanbul": .45, "ankara": .2, "izmir": .15, "manisa": .05, "aydin": .05, "denizli": .05, "bodrum": .05}
res["nat_at"] = sum(w * hava(c)["at"].reindex(res.index) for c, w in W_.items())
res["A_takvim"] = backtest(FA, obs)
res["B_gercek"] = backtest(FA + FW, obs)
res["B_tahmin"] = backtest(FA + FW, fc)
res.to_csv(RESULTS / "07_tahminle_tahminler.csv")


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
    a_mape, a_cost = mape(r.y, r.A_takvim), dengesizlik(r, "A_takvim")
    out[name] = {}
    for m in ["A_takvim", "B_gercek", "B_tahmin"]:
        mp, cs = mape(r.y, r[m]), dengesizlik(r, m)
        out[name][m] = {"MAPE": round(mp, 2), "dengesizlik_TL": round(cs),
                        "MAPE_degisim_%": round((mp / a_mape - 1) * 100, 1),
                        "dengesizlik_degisim_%": round((cs / a_cost - 1) * 100, 1)}
    out[name]["saat"] = len(r)
ape = lambda c: (res.y - res[c]).abs() / res.y
wk = pd.DataFrame({c: ape(c).resample("W").mean() for c in ["A_takvim", "B_gercek", "B_tahmin"]})
out["haftalik_A_dan_iyi"] = {"hafta": len(wk), "B_gercek": int((wk.B_gercek < wk.A_takvim).sum()),
                             "B_tahmin": int((wk.B_tahmin < wk.A_takvim).sum())}
# tahmin hatası (sıcaklık, °C)
out["sicaklik_tahmin_hatasi_MAE_C"] = {c: round(float((tahmin(c).t - hava(c).t.reindex(tahmin(c).index)).abs().mean()), 2)
                                       for c in SEHIRLER}
json.dump(out, open(RESULTS / "07_tahminle_ontest.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
