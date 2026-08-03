import random
import numpy as np
from app.core.slab_sabitleri import *
from app.core.uzay_bilgileri import *
from app.core.simulasyon_core import ortam_sicakligi_cel
from app.services.ortam_servisi import ortam_normalize
from app.core.simulasyon_core import SlabState



# DB den bağımsız bilgisayarda tutulan slablar üretir
def egitim_slab_uret() -> SlabState:
    sicaklik = random.randrange(min_sicaklik_cel, max_sicaklik_cel)

    giris = random.randrange(min_genislik_mm, max_genislik_mm)
    cikis = giris + (random.randrange(-1* genislik_sapma, genislik_sapma))
    zorluk = (genislik_sapma + (cikis - giris)) / (2 * genislik_sapma) # %lik değer alır
    
    return {
        "cikis_kalinlik": random.uniform(min_kalinlik_mm, max_kalinlik_mm),
        "giris_genislik": giris,
        "cikis_genislik": cikis,
        "sicaklik": sicaklik,
        "cikis_uzunluk": random.randrange(cikis_uzunluk_min, cikis_uzunluk_max),
        "zorluk": zorluk,
        "kalan_gun": random.uniform(0, max_gun),
    }


# TODO buralar değişicek öneli!!
# Eğitimde simülasyona Slab verisi sokmam lazım normalize olmamış halde
# Ortam servisindeki normalize etme foksiyonu ile birlikte vektör döndürür
def egitim_slab_vektor(slab: SlabState) -> SlabState:
    
    return [
        ortam_normalize(slab["cikis_kalinlik"], min_kalinlik_mm, max_kalinlik_mm),
        ortam_normalize(slab["giris_genislik"], min_genislik_mm, max_genislik_mm),
        ortam_normalize(slab["cikis_genislik"], slab["cikis_genislik"] - 10, slab["cikis_genislik"] + 10), #TODO buraya bi bak
        ortam_normalize(slab["sicaklik"], ortam_sicakligi_cel, max_sicaklik_cel),
        ortam_normalize(slab["cikis_uzunluk"], cikis_uzunluk_min, cikis_uzunluk_max),
        ortam_normalize(slab["zorluk"], 0, 100),
        ortam_normalize(slab["kalan_gun"], 0, max_gun),
        ]




# 20 tanelik bir havuz oluşturur
def egitim_havuzu_uret() -> list[SlabState]:
    return [egitim_slab_uret() for _ in range(havuz_boyutu)]



# Bir tane np.array bir tane list[SlabState] döndürür
# list simülasyonun ilerletilmesinden sorumlu olur ve normalize edilmemiş halde olur
def egitim_state_olustur(son_secilen: dict | None) -> np.ndarray:
    havuz = egitim_havuzu_uret()
    state = np.zeros((havuz_boyutu + 1, ozellik_sayisi), dtype=np.float32)
    normal_slab_verisi: list[dict | None] = [None] * (havuz_boyutu + 1)
    normal_slab_verisi[20] = {"cikis_kalinlik":0,"giris_genislik":0,"cikis_genislik":0,"sicaklik":0,"cikis_uzunluk":0,"zorluk":0,"kalan_gun":0}
    #print(state)
    #print(normal_slab_verisi)

    for i, slab in enumerate(havuz):
        state[i] = egitim_slab_vektor(slab)
        normal_slab_verisi[i] = slab
        
    if son_secilen is not None:
        state[havuz_boyutu] = egitim_slab_vektor(son_secilen)
        normal_slab_verisi[havuz_boyutu] = son_secilen

    return state, normal_slab_verisi

# SlabState'i normalize edip np.ndarray' e çeviren fonksiyon
def egitim_Sslabstate_to_normalizasyon(havuz: list[SlabState]):
    state = np.zeros((havuz_boyutu + 1, ozellik_sayisi), dtype=np.float32)
    for i, slab in enumerate(havuz):
            state[i] = egitim_slab_vektor(slab)
            
    return state
