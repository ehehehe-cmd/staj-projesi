import numpy as np
from app.rl.egitim_ortam_olusturucu import egitim_state_olustur, egitim_slab_vektor
from app.rl.egitim_env import SlabTakvimiEnv


# --- Geçici (dummy) fonksiyonlar, reward ve simulate henüz hazır değil ---

def dummy_reward_fn(secilen_slab, onceki_slab, state):
    return float(np.random.uniform(-1, 1))

def dummy_state_fn():
    return np.random.uniform(0, 100, size=(21, 5)).astype(np.float32)

def dummy_slab_fn():
    return np.random.uniform(0, 100, size=(5,)).astype(np.float32)


# --- Env'i kur ---

env = SlabTakvimiEnv(
    max_steps=10,
    reward_fn=dummy_reward_fn,
    simulate_fn=None,          # ileride simulate_fn=senin_fonksiyonun olarak eklenecek
    state_fn=egitim_state_olustur,   # kendi state_fn'inle değiştir
    slab_fn=egitim_slab_vektor,     # kendi slab_fn'inle değiştir
)

# --- Test döngüsü ---

obs, info = env.reset()
print("İlk state şekli:", obs.shape)          # (21, 5) olmalı
print("İlk action mask:", info["action_mask"])  # şu an hepsi True (kısıt eklenmedi)

toplam_odul = 0.0

for adim in range(10):
    mask = info["action_mask"]

    # Şu an tüm aksiyonlar geçerli (mask hepsi True), rastgele seçelim
    gecerli_aksiyonlar = np.where(mask)[0]
    action = int(np.random.choice(gecerli_aksiyonlar))

    obs, reward, terminated, truncated, info = env.step(action)
    toplam_odul += reward

    print(f"Adım {adim:2d} | Aksiyon: {action:2d} | Ödül: {reward:6.3f} "
          f"| Terminated: {terminated} | Truncated: {truncated}")

    if terminated or truncated:
        print("Episode bitti, reset ediliyor...")
        obs, info = env.reset()

print("\nToplam ödül:", toplam_odul)
print("Son state şekli:", obs.shape)