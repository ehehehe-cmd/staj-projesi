import random
import numpy as np
from app.core.slab_sabitleri import *
from app.core.uzay_bilgileri import *
from app.core.simulasyon_core import ortam_sicakligi_cel
from app.services.ortam_servisi import ortam_normalize



# DB den bağımsız bilgisayarda tutulan slablar üretir
def egitim_slab_uret() -> dict:

    sicaklik = random.randrange(min_sicaklik_cel, max_sicaklik_cel),
    
    ilerleme = (max_sicaklik_cel - sicaklik)/(max_sicaklik_cel - ortam_sicakligi_cel)
    ilerleme = max(0.0, min(1.0,ilerleme))
    
    sertlik = min_sertlik + (max_sertlik - min_sertlik) * ilerleme
    return {
        "kalinlik": random.uniform(min_kalinlik_mm, max_kalinlik_mm),
        "genislik": random.uniform(min_genislik_mm, max_genislik_mm),
        "sertlik": sertlik,
        "sicaklik": sicaklik,
        "kalan_gun": random.uniform(0, max_gun),
    }


# TODO buralar değişicek öneli!!
# Eğitimde simülasyona Slab verisi sokmam lazım normalize olmamış halde
# Ortam servisindeki normalize etme foksiyonu ile birlikte vektör döndürür
def egitim_slab_vektor() -> list[float]:
    slab = egitim_slab_uret()
    return [
        ortam_normalize(slab["kalinlik"], min_kalinlik_mm, max_kalinlik_mm),
        ortam_normalize(slab["genislik"], min_genislik_mm, max_genislik_mm),
        ortam_normalize(slab["sertlik"], min_sertlik, max_sertlik),
        ortam_normalize(slab["sicaklik"], min_sicaklik_cel, max_sicaklik_cel),
        ortam_normalize(slab["kalan_gun"], 0, max_gun),
        ]




# 20 tanelik bir havuz oluşturur
def egitim_havuzu_uret() -> list[dict]:
    return [egitim_slab_uret() for _ in range(havuz_boyutu)]




def egitim_state_olustur(son_secilen: dict | None) -> np.ndarray:
    havuz = egitim_havuzu_uret()
    state = np.zeros((havuz_boyutu + 1, ozellik_sayisi), dtype=np.float32)
    for i, slab in enumerate(havuz):
        state[i] = egitim_slab_vektor()

    if son_secilen is not None:
        state[havuz_boyutu] = egitim_slab_vektor()

    return state

