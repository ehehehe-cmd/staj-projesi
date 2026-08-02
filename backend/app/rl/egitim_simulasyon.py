from app.core.simulasyon_core import SlabState, simulayson_ilerlet, simulasyon_slab_to_slabstate, simulasyon_slabstate_to_slab
from app.models.slab import Slab
from app.services.depo_servisi import depo_slab_üret


def egitim_simulasyon_calistir(dakika:int, slablar: list[SlabState]):
    for i, slab in enumerate(slablar):
        if i == 20:
            break
        slablar[i] =  simulayson_ilerlet(slab, dakika)
    return slablar
