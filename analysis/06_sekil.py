"""Şekil 1 – (a) saatlik ön test, (b) İzmir aylık tüketim, (c) gece kentsel ısı adası.
Gereksinim: 01_saatlik_ontest.py ve 04_izmir_aylik.py önce çalıştırılmalı."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ortak import DATA, RESULTS, FIGURES

INK, MUT, A, B, GRID = "#2b2b2b", "#6b6a63", "#eb6834", "#2a78d6", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.5, "axes.edgecolor": MUT,
                     "axes.labelcolor": INK, "xtick.color": MUT, "ytick.color": MUT})
r = pd.read_csv(RESULTS / "01_saatlik_tahminler.csv", index_col=0, parse_dates=True)
iz = pd.read_csv(RESULTS / "04_izmir_aylik_tablo.csv", index_col=0)
k = pd.read_csv(DATA / "modis" / "kentsel_isi_adasi_2024_2025.csv")
k["kia"], k["mo"] = k.kent_gece_C - k.kirsal_gece_C, k.ay.str[5:].astype(int)

fig, ax = plt.subplots(1, 3, figsize=(10, 3.0), gridspec_kw={"width_ratios": [1.5, 1.1, 1]})
w = r["2024-07-22":"2024-07-28"]
a = ax[0]
a.plot(w.index, w.y / 1000, color=INK, lw=1.6, label="Gerçekleşen")
a.plot(w.index, w.A_takvim / 1000, color=A, lw=1.6, label="A: takvim + geçmiş tüketim")
a.plot(w.index, w.B_meteo / 1000, color=B, lw=1.6, label="B: A + meteorolojik girdiler")
a.set_title("(a) 48 saat önceden tahmin, 22–28 Tem 2024", loc="left", fontsize=8, color=INK)
a.set_ylabel("Türkiye saatlik tüketim (GWh)")
a.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
a.legend(frameon=False, fontsize=6.5, loc="upper left"); a.set_ylim(33, 64)

b = ax[1]; mo = np.arange(1, 13)
b.plot(mo, iz.Mesken / 1000, color=B, lw=1.8, marker="o", ms=3, label="Mesken")
b.plot(mo, iz.Ticarethane / 1000, color=A, lw=1.8, marker="o", ms=3, label="Ticarethane")
b.axvspan(6.5, 7.5, color="#f3f2ee"); b.text(7, 22.3, "en sıcak ay", ha="center", fontsize=6.5, color=MUT)
b.set_xticks(mo); b.set_xticklabels(list("OŞMNMHTAEEKA"), fontsize=7); b.set_ylim(9, 23.5)
b.set_title("(b) İzmir 2025, aylık tüketim", loc="left", fontsize=8, color=INK)
b.set_ylabel("Günlük ortalama (GWh)"); b.legend(frameon=False, fontsize=6.5, loc="upper left")

c = ax[2]
cities, lab = ["Izmir", "Manisa", "Bodrum", "Aydin", "Denizli"], ["İzmir", "Manisa", "Bodrum", "Aydın", "Denizli"]
yaz = [k[(k.sehir == s) & k.mo.isin([6, 7, 8])].kia.mean() for s in cities]
kis = [k[(k.sehir == s) & k.mo.isin([12, 1, 2])].kia.mean() for s in cities]
x, bw = np.arange(5), .38
c.bar(x - bw / 2 - .01, yaz, bw, color=A, label="Yaz"); c.bar(x + bw / 2 + .01, kis, bw, color=B, label="Kış")
c.set_xticks(x); c.set_xticklabels(lab, fontsize=7); c.set_ylabel("Gece kent − kırsal (°C)"); c.set_ylim(0, 2.1)
c.set_title("(c) Kentsel ısı adası (MODIS)", loc="left", fontsize=8, color=INK)
c.legend(frameon=False, fontsize=6.5, loc="upper right")
for aa in ax:
    aa.grid(axis="y", color=GRID); aa.set_axisbelow(True)
    for s in ["top", "right"]:
        aa.spines[s].set_visible(False)
fig.tight_layout(w_pad=1.2)
fig.savefig(FIGURES / "sekil1_on_analizler.png", dpi=220)
print("figures/sekil1_on_analizler.png")
