from app.core.slab_sabitleri import *
from typing import TypedDict
from datetime import datetime

soguma_katsayisi = 0.01


class SlabState(TypedDict):
    slab_id: int
    kalinlik: float
    genislik: float
    sertlik: float
    kalite_sinifi: str
    teslim_tarihi: datetime
    sicaklik: float
    durum: str
    olusturma_tarihi: datetime


# BU MODÜLE SADECE SlabState GELEBİLİR DİKKATLİ OL
  
def simulayson_ilerlet(slab: SlabState, dakika: float) -> SlabState:
    for _ in range(dakika):
        slab = simulasyon_bir_dakika_uygula(slab)
    return slab


def simulasyon_bir_dakika_uygula(slab: SlabState) -> SlabState:
    slab["sicaklik"] = ortam_sicakligi_cel + (slab["sicaklik"]- ortam_sicakligi_cel) *(1 - soguma_katsayisi)

    ilerleme = (max_sicaklik_cel - slab["sicaklik"])/(max_sicaklik_cel - ortam_sicakligi_cel)
    ilerleme = max(0.0, min(1.0,ilerleme))

    slab["sertlik"] = min_sertlik + (max_sertlik - min_sertlik) * ilerleme
    return slab