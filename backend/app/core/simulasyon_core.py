from app.core.slab_sabitleri import *
from app.models.slab import Slab
from typing import TypedDict
from decimal import Decimal
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

# Slab türündeki veriyi StalState e çevirir
# Simülasyonın core fonksiyonları için gerekli
def simulasyon_slab_to_slabstate(slab: Slab) -> SlabState:
    return{
        "slab_id": slab.slab_id,
        "kalinlik": slab.kalinlik,
        "genislik": slab.genislik,
        "sertlik": float(slab.sertlik),
        "kalite_sinifi": slab.kalite_sinifi,
        "teslim_tarihi": slab.teslim_tarihi,
        "sicaklik": float(slab.sicaklik),
        "durum": slab.durum,
        "olusturma_tarihi": slab.olusturma_tarihi        
    }

# Core için çevirdiğimiz veriyi model tarafında kullanılması içi Slab a çevirir
def simulasyon_slabstate_to_slab(slab_dic: SlabState, slab: Slab) -> Slab:
    slab.slab_id = slab_dic["slab_id"]
    slab.kalinlik = slab_dic["kalinlik"]
    slab.genislik = slab_dic["genislik"]
    slab.sertlik = Decimal(slab_dic["sertlik"])
    slab.kalite_sinifi = slab_dic["kalite_sinifi"]
    slab.teslim_tarihi = slab_dic["teslim_tarihi"]
    slab.sicaklik = Decimal(slab_dic["sicaklik"])
    slab.durum = slab_dic["durum"]
    slab.olusturma_tarihi = slab_dic["olusturma_tarihi"]
    return slab


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