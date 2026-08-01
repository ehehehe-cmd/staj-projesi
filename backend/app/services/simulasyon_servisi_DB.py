from app.core.simulasyon_core import SlabState, simulayson_ilerlet
from app.services.ortam_servisi import ortam_secim_verisi_okuma
from app.models.slab import Slab
from sqlalchemy.orm import Session
from decimal import Decimal

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

def simulasyon_DB_calistir(db: Session, dakika_secim: int):
    slablar = ortam_secim_verisi_okuma(db)
    db_verisi = slablar.copy()
    for i, slab in enumerate(slablar):
        slab_state = simulasyon_slab_to_slabstate(slab)
        ilerlemis_slab_state = simulayson_ilerlet(slab=slab_state, dakika=dakika_secim)
        db_verisi[i]  = simulasyon_slabstate_to_slab(ilerlemis_slab_state, db_verisi[i])
        print("değişti")
    db.commit()
    print("comitlendi")
