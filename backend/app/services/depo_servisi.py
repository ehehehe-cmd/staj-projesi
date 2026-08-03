from datetime import date
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Slab
from app.core.slab_sabitleri import * #Fiziksel sınırların olduğu yer
from app.core.simulasyon_core import ortam_sicakligi_cel, soguma_katsayisi
import random


#Aralıklara göre slab'ı üreten fonksiyon 
def depo_slab_üret():
    sicaklik = random.randrange(min_sicaklik_cel, max_sicaklik_cel)

    giris = random.randrange(min_genislik_mm, max_genislik_mm)
    cikis = giris + (random.randrange(-1* genislik_sapma, genislik_sapma))
    zorluk = (genislik_sapma + (cikis - giris)) / 2 * genislik_sapma # %lik değer alır
    
    yeni_slab = Slab(
    cikis_kalinlik=random.randrange(min_kalinlik_mm, max_kalinlik_mm),
    giris_genislik=giris,
    cikis_genislik=cikis,
    sicaklik=sicaklik,
    cikis_uzunluk=random.randrange(cikis_uzunluk_min, cikis_uzunluk_max),
    zorluk = zorluk,
    kalite_sinifi=random.choice(kalite_sinifi_list),
    teslim_tarihi=rastgele_tarih(min_gun, max_gun),
    durum="depoda",
    )

    return yeni_slab


# Rastgele tarih üretir
def rastgele_tarih(min_gun_sayisi, max_gun_sayisi):
    bugun = date.today()
    rastgele_gun = random.randint(min_gun_sayisi, max_gun_sayisi)
    return bugun + timedelta(days = rastgele_gun)

# DB deki depoya slabı ekler
def depo_slab_ekle(db: Session):

    yeni_slab = depo_slab_üret()

    db.add(yeni_slab)
    db.commit()
    db.refresh(yeni_slab)

    print("Eklenen slab ID:", yeni_slab.slab_id)