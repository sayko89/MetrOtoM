"""Ortak veri yükleme yardımcıları."""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

SEHIRLER = ["izmir", "manisa", "aydin", "denizli", "bodrum", "istanbul", "ankara"]
EGE = ["izmir", "manisa", "aydin", "denizli", "bodrum"]
GUN = pd.Series([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], index=range(1, 13))


def hava(sehir: str) -> pd.DataFrame:
    """Open-Meteo saatlik hava verisi (yerel saat)."""
    d = pd.read_csv(DATA / "hava" / f"{sehir}_2024_2025.csv", skiprows=3, parse_dates=["time"]).set_index("time")
    d.columns = ["t", "rh", "at", "ws", "cc", "rad", "pr"]
    return d


def epias_saatlik() -> pd.DataFrame:
    """EPİAŞ 2024 saatlik Türkiye geneli gerçek zamanlı tüketim, PTF ve SMF."""
    y = pd.read_excel(DATA / "epias" / "gercek_zamanli_tuketim_2024.xlsx").set_index("Tarih")["Tüketim Miktarı(MWh)"].rename("y")
    ptf = pd.read_excel(DATA / "epias" / "ptf_2024.xlsx").set_index("Tarih")["PTF (TL/MWh)"].rename("ptf")
    smf = pd.read_excel(DATA / "epias" / "smf_2024.xlsx").set_index("Tarih")["SMF (TL/MWh)"].rename("smf")
    d = pd.concat([y, ptf, smf], axis=1)
    return d[d.index < "2025-01-01"]


def epias_il() -> pd.DataFrame:
    """EPİAŞ il bazlı aylık Tüketim Miktarları (profil grubuna göre). top = üç sütunun toplamı (MWh)."""
    rows = []
    for f in sorted((DATA / "epias_il").glob("*.xlsx")):
        il, donem = f.stem.split("_")
        d = pd.read_excel(f)
        d.columns = ["il_adi", "segment", "serbest", "st_hakki_yok", "st_kullanmayan"]
        d["il"], d["yil"], d["ay"] = il, int(donem[:4]), int(donem[5:])
        rows.append(d)
    d = pd.concat(rows, ignore_index=True)
    d["toplam"] = d.serbest + d.st_hakki_yok + d.st_kullanmayan
    return d


def r2(y, yhat):
    y, yhat = np.asarray(y), np.asarray(yhat)
    return float(1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum())
