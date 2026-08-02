from app.core.simulasyon_core import SlabState, simulayson_ilerlet, simulasyon_slab_to_slabstate, simulasyon_slabstate_to_slab
from app.services.ortam_servisi import ortam_secim_verisi_okuma
from app.models.slab import Slab
from sqlalchemy.orm import Session




def simulasyon_DB_calistir(db: Session, dakika_secim: int):
    slablar = ortam_secim_verisi_okuma(db)
    db_verisi = slablar.copy()
    for i, slab in enumerate(slablar):
        slab_state = simulasyon_slab_to_slabstate(slab)
        ilerlemis_slab_state = simulayson_ilerlet(slab=slab_state, dakika=dakika_secim)
        db_verisi[i]  = simulasyon_slabstate_to_slab(ilerlemis_slab_state, db_verisi[i])
    db.commit()
