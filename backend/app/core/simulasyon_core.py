from app.core.slab_sabitleri import *
from app.models.slab import Slab
from typing import TypedDict
from decimal import Decimal
from datetime import datetime

soguma_katsayisi = 0.01


class SlabState(TypedDict):
    slab_id: int
    cikis_kalinlik: float
    giris_genislik: float
    cikis_genislik: float
    sicaklik: float
    cikis_uzunluk: float
    zorluk: float
    kalite_sinifi: str
    teslim_tarihi: datetime
    durum: str
    olusturma_tarihi: datetime

# Slab türündeki veriyi StalState e çevirir
# Simülasyonın core fonksiyonları için gerekli
def simulasyon_slab_to_slabstate(slab: Slab) -> SlabState:
    return{
        "slab_id": slab.slab_id,
        "cikis_kalinlik": slab.cikis_kalinlik,
        "giris_genislik": slab.giris_genislik,
        "cikis_genislik": slab.cikis_genislik,
        "sicaklik": float(slab.sicaklik),
        "cikis_uzunluk": slab.cikis_uzunluk,
        "zorluk": slab.zorluk,
        "kalite_sinifi": slab.kalite_sinifi,
        "teslim_tarihi": slab.teslim_tarihi,
        "durum": slab.durum,
        "olusturma_tarihi": slab.olusturma_tarihi        
    }

# Core için çevirdiğimiz veriyi model tarafında kullanılması içi Slab a çevirir
def simulasyon_slabstate_to_slab(slab_dic: SlabState, slab: Slab) -> Slab:
    slab.slab_id = slab_dic["slab_id"]
    slab.cikis_kalinlik = slab_dic["cikis_kalinlik"]
    slab.giris_genislik = slab_dic["giris_genislik"]
    slab.cikis_genislik = slab_dic["cikis_genislik"]
    slab.sicaklik = Decimal(slab_dic["sicaklik"])
    slab.cikis_uzunluk = slab_dic["cikis_uzunluk"]
    slab.kalite_sinifi = slab_dic["kalite_sinifi"]
    slab.teslim_tarihi = slab_dic["teslim_tarihi"]
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
    return slab