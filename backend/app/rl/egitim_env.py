import numpy as np
import gymnasium as gym
from app.rl.egitim_ortam_olusturucu import egitim_slab_uret, egitim_Sslabstate_to_normalizasyon
from gymnasium import spaces

class SlabTakvimiEnv(gym.Env):
    metadata = {"render_modes": []}


    # İçeride kullanıcağımız fonksiyonları içeriye koy
    def __init__(self,
            max_steps: int = 100,
            reward_fn = None,
            simulate_fn = None,
            state_fn = None,
            slab_fn = None,
            ):
        super().__init__()

        self.action_space = spaces.Discrete(20)
        self.observation_space = spaces.Box(
            low=np.inf, high=np.inf, shape=(21,5), dtype=np.float32
        )

        self.max_steps = max_steps
        self.current_step = 0
        self.state: np.ndarray | None = None

        # Dışardan enjekte edilen modül fonksiyonları
        # Verilmezse override edilen _compute_reward vb. metodları kullanır
        self.reward_fn = reward_fn
        self.simulate_fn = simulate_fn
        self.state_fn = state_fn
        self.slab_fn = slab_fn


        #*******************************
        # ANA FONKSİYONLAR
        #*******************************

        # Her reset atıldığında çalışacak fonksiyon
        # Sıfırlamaya yarar.
        # İlk başlangıç durumu
    def reset(self, seed = None, options = None):
        super().reset(seed=seed)
        self.current_step = 0
        # ANCHOR BURDA KALDIK! ÖNEMLİ YER!! 
        # TODO: Asıl SlabState verisi 
        # TODO: Satate üreten fonksiyon
        self.state, self.slabstate = self._generate_initial_state(son_secilen=None)

        info = {"action_mask": self._get_action_mask()}
        return self.state, info

    # Bir sonraki adıma geçme fonksiyonu       
    def step(self, action: int):
        mask = self._get_action_mask()

        # Geçersiz (maskelenmiş) aksiyon seçilirse büyük ceza ver
        if not mask[action]:
            reward = -100.0 # TODO İLERİDE DÜZENLE
            terminated = False
            truncated= self.current_step >= self.max_steps
            info = {"action_mask": mask, "invalid_aciton": True}
            return self.state, reward, terminated, truncated, info

        secilen_slab = self.state[action].copy()
        secilen_slab_gercek = self.slabstate[action].copy()

        onceki_slab_gercek = self.slabstate[20].copy()
        onceki_slab = self.state[20].copy()

        # Ödül Modülü -> dışardan verilmişse onu çağır, verilmemişse override ı kullan
        reward = self._compute_reward(secilen_slab, onceki_slab)

        # Secilen slabı havuzdan çıkart, yerine yenisini koy
        self.state[action], self.slabstate[action] = self._get_replacement_slab()

        # 21. satırı seçilen slab ile güncelle
        self.state[20] = secilen_slab
        self.slabstate[20] = secilen_slab_gercek

        # Simülasyon modülü -> Her adımda veya belirli aralıklarla durumu ilerlet
        # TODO ilerletme sürecini planla
        # (sıcaklık düşüşü, durum güncellemesi gibi)
        if self.simulate_fn is not None:
            self.slabstate = self.simulate_fn(50, self.slabstate)
            self.state = egitim_Sslabstate_to_normalizasyon(self.slabstate)

        self.current_step += 1
        terminated = self._is_episode_done()
        truncated = self.current_step >= self.max_steps

        info = {"action_mask": self._get_action_mask()}
        print(self.slabstate[1])
        #print(self.state)

        return self.state, reward, terminated, truncated, info

    #***************************
    # MASKELEME
    #***************************

    # 20 boyutlu boolean maske. Ture = seçilebilir, False = seçilemez
    # Geçiş ksııtlarını bir önceki slaba göre kontrol et
    def _get_action_mask(self) -> np.ndarray:
        onceki_slab = self.state[20]
        mask = np.ones(20, dtype=bool)

        for i in range(20):
            aday = self.state[i]
            # TODO: kendi kısıt fonksiyonlarını buraya ekle, örnek:
            # if abs(aday[1] - onceki_slab[1]) > GENISLIK_LIMIT:
            #     mask[i] = False
            pass
        return mask

    # SAKIN FONKSİYONUN ADINI DEĞİŞTİRME
    def action_masks(self) -> np.ndarray:
        return self._get_action_mask()

    #***********************
    # TODO İLERİDE FONKSİYONLAR EKLENİCEK
    #***********************


    def _generate_initial_state(self, son_secilen) -> np.ndarray:
        if self.state_fn is not None:
            return self.state_fn(son_secilen)

        # Fonksiyon verilmediyse alt sınıftan bu metodu overridelasın
        raise NotImplementedError("state_fn verilmedi ve _generate_initial_state override edilmedi")
    # ANCHOR buray tamamen düznle
    def _get_replacement_slab(self) -> np.ndarray:
        if self.slab_fn is not None:
            slab = egitim_slab_uret()
            return self.slab_fn(slab), slab

        raise NotImplementedError("slab_fn verilmedi ve _get_replacement_slab override edilmedi")
        
    def _compute_reward(self, secilen_slab: np.ndarray, onceki_slab: np.ndarray) -> float:
        if self.reward_fn is not None:
                return self.reward_fn(secilen_slab, onceki_slab, self.state)
        raise NotImplementedError("reward_fn verilmedi ve _compute_reward override edilmedi")

    def _is_episode_done(self) -> bool:
        # TODO: bitiş koşulu (örn. depo boşaldı, vardiya bitti vb.)
        return False    


# ----------------------------------------------------------------------
# KULLANIM ÖRNEKLERİ (algoritma seçildikten sonra)
# ----------------------------------------------------------------------
 
# --- Kendi modüllerinle env oluşturma (dependency injection) ---
# from odul_modulu import hesapla_odul
# from simulasyon_modulu import ilerlet
# from ortam_yardimci import baslangic_state_uret
# from depo_modulu import yeni_slab_getir
#
# env = SlabTakvimEnv(
#     reward_fn=hesapla_odul,
#     simulate_fn=ilerlet,
#     state_fn=baslangic_state_uret,
#     slab_fn=yeni_slab_getir,
# )
 
# --- Env doğrulama ---
# from gymnasium.utils.env_checker import check_env
# check_env(env)
 
# --- MaskablePPO (sb3-contrib) ---
# from sb3_contrib import MaskablePPO
# from sb3_contrib.common.wrappers import ActionMasker
#
# def mask_fn(env):
#     return env._get_action_mask()
#
# env = ActionMasker(SlabTakvimEnv(), mask_fn)
# model = MaskablePPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100_000)
 
# --- DQN (manuel maskeleme, ekstra kütüphane gerekmez) ---
# Not: SB3'ün vanilla DQN'i action_masks() metodunu otomatik kullanmaz.
# Karar anında (predict sonrası) Q-değerlerini elle maskelemen gerekir:
#
# from stable_baselines3 import DQN
# model = DQN("MlpPolicy", SlabTakvimEnv(), verbose=1)
# model.learn(total_timesteps=100_000)
#
# # Karar Modülü'nde tahmin yaparken:
# q_values = model.q_net(obs_tensor)
# mask = env._get_action_mask()
# q_values[~mask] = -np.inf
# action = q_values.argmax()
        