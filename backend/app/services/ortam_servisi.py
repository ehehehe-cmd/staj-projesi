from datetime import date
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Slab
from app.core.slab_sabitleri import *
from app.core.uzay_bilgileri import *
from app.models.takvimleme_detay import TakvimlemeDetay
from app.models.takvimleme import Takvimleme
import numpy as np




# DB den modelin seçim yapacağı özelliği "depoda" olan veriyi çeker
def ortam_secim_verisi_okuma(db: Session):

    depodakiler = db.query(Slab).filter(Slab.durum == "depoda").all()

    ortam_slab_yazdır(depodakiler)

    return depodakiler


# Modelin daha iyi anlayabilmesi için gereken normalizasyon formülü 
def ortam_normalize(deger:float, min_deger:float, max_deger:float) -> float:
    return (deger - min_deger)/(max_deger - min_deger)

# Tek bir slab ın normalize edilmiş verileri
def ortam_slab_vektoru(slab: Slab) -> list[float]:
    kalan_gun = (slab.teslim_tarihi - date.today()).days
    return [
        ortam_normalize(slab.cikis_kalinlik, min_kalinlik_mm, max_kalinlik_mm),
        ortam_normalize(slab.giris_genislik, min_genislik_mm, max_genislik_mm),
        ortam_normalize(slab.cikis_genislik, slab.giris_genislik - 10, slab.giris_genislik + 10),
        ortam_normalize(slab.sicaklik, ortam_sicakligi_cel, max_sicaklik_cel),
        ortam_normalize(slab.cikis_uzunluk, cikis_uzunluk_min, cikis_uzunluk_max),
        ortam_normalize(slab.zorluk, 0, 100),
        ortam_normalize(kalan_gun, 0, max_gun)
    ]

# Şuanda aktf olan takvimin db sini getirir
def ortam_aktif_takvimleme_id_getir(db: Session):
    aktif = db.query(Takvimleme).filter(Takvimleme.aktif_mi == True).first()
    return aktif.takvimleme_id if aktif else None

# Aktif takvimde olan ve son seçilen slabı getirir
def ortam_son_secilen_slab_getir(db: Session, takvimleme_id: int) -> Slab | None:
    son_kayit = (
        db.query(TakvimlemeDetay)
        .filter(TakvimlemeDetay.takvimleme_id == takvimleme_id)
        .order_by(TakvimlemeDetay.sira_no.desc())
        .first()
    )
    if son_kayit is None:
        return None
    return db.query(Slab).filter(Slab.slab_id == son_kayit.slab_id).first()

# Slabları yazdırır
def ortam_slab_yazdır(slablar):

    for s in slablar:
        print(s.slab_id, s.kalite_sinifi, s.durum)

# Modeli için gerekli state i oluşturur
def ortam_state_olustur(db: Session):
    takvimleme_id = ortam_aktif_takvimleme_id_getir(db)
    depodaki_slablar = ortam_secim_verisi_okuma(db)

    state = np.zeros((havuz_boyutu + 1, ozellik_sayisi))
    id_eslemesi={}

    # 0-19: havuzaki adaylar 
    for i, slab in enumerate(depodaki_slablar):
        state[i] = ortam_slab_vektoru(slab)
        id_eslemesi[i] = slab.slab_id

    # 20 en son seçilen slab
    son_slab = ortam_son_secilen_slab_getir(db, takvimleme_id)
    if son_slab is not None:
        state[havuz_boyutu] = ortam_slab_vektoru(son_slab)

    return state, id_eslemesi