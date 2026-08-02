from datetime import date
from app.core.database import SessionLocal
from app.models import Slab
from app.services.depo_servisi import depo_slab_ekle
from app.services.ortam_servisi import ortam_state_olustur, ortam_secim_verisi_okuma
from app.rl.egitim_ortam_olusturucu import egitim_havuzu_uret, egitim_state_olustur
from app.services.simulasyon_servisi_DB import simulasyon_DB_calistir
db = SessionLocal()

# depo_servisi deneme 
depo_slab_ekle(db)

# ortam_servisi deneme
'''
state, id_eslemesi = ortam_state_olustur(db)

print("State shape:", state.shape)      # (21, 5) olmalı
print("\nSatır 0 (1. slab):", state[0])
print("Satır 1 (2. slab):", state[1])
print("Satır 2 (boş slot):", state[2])   # tamamen sıfır olmalı
print("Satır 19 (boş slot):", state[19]) # tamamen sıfır olmalı
print("Satır 20 (önceki slab):", state[20])  # henüz seçim yoksa sıfır olmalı

print("\nID eşlemesi:", id_eslemesi)
'''

# egitim_ortam_olusturucu servisi deneme

#havuz = egitim_havuzu_uret()
'''
state = egitim_state_olustur(son_secilen=None)

print("State shape:", state.shape)   # (21, 5) olmalı
print("Satır 0:", state[0])          # dolu, 0-1 arası değerler
print("Satır 20:", state[20])        # sıfır (henüz seçim yok)
'''

# Simülasyon denemeleri
# simulasyon_DB_calistir(db, 5)


db.close()


