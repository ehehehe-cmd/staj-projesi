import numpy as np
from app.rl.egitim_ortam_olusturucu import egitim_state_olustur, egitim_slab_vektor
from app.rl.egitim_simulasyon import egitim_simulasyon_calistir
from app.rl.egitim_env import SlabTakvimiEnv
from app.rl.constants import *


# ============================================================
# 1) TEMEL KURULUM TESTİ — reward_fn=None, env'in kendi
#    _compute_reward / _get_action_mask mantığını kullanmasını
#    sağlıyoruz (dummy değil, gerçek davranışı test ediyoruz)
# ============================================================

env = SlabTakvimiEnv(
    max_steps=500,
    reward_fn=None,          # None -> env'in içindeki gerçek _compute_reward çalışır
    simulate_fn=egitim_simulasyon_calistir,
    state_fn=egitim_state_olustur,
    slab_fn=egitim_slab_vektor,
)

obs, info = env.reset()

print("=" * 60)
print("TEST 1: Şekil ve ilk mask kontrolü")
print("=" * 60)
print("İlk state şekli:", obs.shape)                       # (21, 7) olmalı
assert obs.shape == (21, 7), f"Beklenen (21,7), gelen {obs.shape}"

print("İlk action mask:", info["action_mask"])
assert info["action_mask"].all(), "İlk adımda kısıt olmamalı (ilk_adim=True bekleniyor)"
print("OK: ilk adımda tüm aksiyonlar serbest.\n")


# ============================================================
# 2) MASK DOĞRULUK TESTİ — bir adım attıktan sonra mask'in
#    gerçekten genişlik/kalınlık limitlerine göre çalıştığını
#    elle hesaplayıp env'in sonucuyla karşılaştırıyoruz
# ============================================================

print("=" * 60)
print("TEST 2: Bir adım sonrası mask fiziksel limitlere uyuyor mu")
print("=" * 60)

action = 4
obs, reward, terminated, truncated, info = env.step(action)
mask = info["action_mask"]

onceki_slab_gercek = env.slabstate[20]
manuel_mask = np.ones(20, dtype=bool)
for i in range(20):
    aday = env.slabstate[i]
    genislik_farki = onceki_slab_gercek[KEY_GIRIS_GENISLIK] - aday[KEY_GIRIS_GENISLIK]
    kalinlik_farki = onceki_slab_gercek[KEY_CIKIS_KALINLIK] - aday[KEY_CIKIS_KALINLIK]
    if abs(genislik_farki) > GENISLIK_LIMIT or abs(kalinlik_farki) > KALINLIK_LIMIT:
        manuel_mask[i] = False
    print(f"  i={i} | env={mask[i]} manuel={manuel_mask[i]} | "
          f"genislik_farki={onceki_slab_gercek[KEY_GIRIS_GENISLIK] - aday[KEY_GIRIS_GENISLIK]:.2f} "
          f"kalinlik_farki={onceki_slab_gercek[KEY_CIKIS_KALINLIK] - aday[KEY_CIKIS_KALINLIK]:.2f}")

assert np.array_equal(mask, manuel_mask), "env mask'i manuel hesaplananla eşleşmiyor!"
print("OK: mask, genişlik/kalınlık limitleriyle tutarlı.\n")


# ============================================================
# 3) GEÇERSİZ AKSİYON TESTİ — maskelenmiş bir aksiyon seçilirse
#    -100 ceza dönüyor mu, state değişmiyor mu
# ============================================================

print("=" * 60)
print("TEST 3: Geçersiz (maskelenmiş) aksiyon cezası")
print("=" * 60)

gecersiz_adaylar = np.where(~mask)[0]
if len(gecersiz_adaylar) > 0:
    invalid_action = int(gecersiz_adaylar[0])
    obs_before = env.state.copy()
    obs_after, reward, terminated, truncated, info = env.step(invalid_action)

    assert reward == -100.0, f"Geçersiz aksiyon ödülü -100 olmalı, gelen: {reward}"
    assert info.get("invalid_aciton") is True
    assert np.array_equal(obs_before, obs_after), "Geçersiz aksiyonda state değişmemeli"
    print(f"OK: aksiyon {invalid_action} maskelenmişti, -100 ceza alındı, state sabit kaldı.\n")
else:
    print("Bu turda tüm aksiyonlar geçerliydi, geçersiz aksiyon testi atlandı.\n")


# ============================================================
# 4) KÜMÜLATİF KM VE EPISODE BİTİŞ TESTİ
# ============================================================

print("=" * 60)
print("TEST 4: Kümülatif km artışı ve hedef_km'de episode bitişi")
print("=" * 60)

env.reset()
adim = 0
onceki_km = env.toplam_uzunluk_km
km_hic_azalmadi = True

while True:
    mask = env._get_action_mask()
    gecerli = np.where(mask)[0]
    if len(gecerli) == 0:
        print("Uyarı: geçerli aksiyon kalmadı, döngü kırılıyor.")
        break

    action = int(np.random.choice(gecerli))
    obs, reward, terminated, truncated, info = env.step(action)

    if env.toplam_uzunluk_km < onceki_km:
        km_hic_azalmadi = False
    onceki_km = env.toplam_uzunluk_km
    adim += 1

    if terminated:
        print(f"OK: episode {adim} adımda, toplam {env.toplam_uzunluk_km:.2f} km ile bitti "
              f"(hedef {HEDEF_KM} km).")
        assert env.toplam_uzunluk_km >= HEDEF_KM
        break
    if truncated:
        print(f"Uyarı: episode km hedefine ulaşmadan max_steps ile kesildi "
              f"({env.toplam_uzunluk_km:.2f} km).")
        break

assert km_hic_azalmadi, "toplam_uzunluk_km episode içinde asla azalmamalı"
print("OK: km her adımda monoton artıyor.\n")


# ============================================================
# 5) ZORLUK PATTERN ÖDÜLÜ TESTİ — 4 kolay sonrası zor'a bonus,
#    erken gelen zor'a ceza verildiğini kontrol ediyoruz
# ============================================================

print("=" * 60)
print("TEST 5: Zorluk pattern ödülü mantığı")
print("=" * 60)

env.reset()
env.zorluk_gecmisi = [False, False, False, False]  # 4 kolay geçmiş simüle et
odul_zamaninda_zor = env._zorluk_pattern_odulu(True)
print("4 kolaydan sonra zor seçim ödülü:", odul_zamaninda_zor)
assert odul_zamaninda_zor > 0, "4 kolaydan sonra zor seçim pozitif ödül almalı"

env.zorluk_gecmisi = [False, True, False, False]  # araya erken zor girmiş
odul_erken_zor = env._zorluk_pattern_odulu(True)
print("Erken gelen zor seçim ödülü:", odul_erken_zor)
assert odul_erken_zor < 0, "Pencere içinde zaten zor varken yeni zor seçim negatif olmalı"
print("OK: zorluk pattern ödülü beklenen yönde çalışıyor.\n")


# ============================================================
# 6) SABİT AKSİYONLA KISA DÖNGÜ — orijinal test senin verdiğin
#    formatta, ama artık gerçek mask/reward ile ve invalid
#    aksiyon durumunda otomatik geçerli aksiyona düşerek
# ============================================================

print("=" * 60)
print("TEST 6: 10 adımlık genel akış (log çıktısı)")
print("=" * 60)

obs, info = env.reset()
toplam_odul = 0.0

for adim in range(10):
    mask = info["action_mask"]
    gecerli_aksiyonlar = np.where(mask)[0]

    tercih_edilen = 4
    action = tercih_edilen if mask[tercih_edilen] else int(np.random.choice(gecerli_aksiyonlar))

    obs, reward, terminated, truncated, info = env.step(action)
    toplam_odul += reward

    print(f"Adım {adim:2d} | Aksiyon: {action:2d} | Ödül: {reward:7.3f} "
          f"| Km: {env.toplam_uzunluk_km:6.2f} "
          f"| Terminated: {terminated} | Truncated: {truncated}")

    if terminated or truncated:
        print("Episode bitti, reset ediliyor...")
        obs, info = env.reset()

print("\nToplam ödül:", toplam_odul)
print("Son state şekli:", obs.shape)

print("\n" + "=" * 60)
print("TÜM TESTLER TAMAMLANDI")
print("=" * 60)