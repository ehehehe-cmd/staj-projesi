import numpy as np
import gymnasium as gym
from app.rl.egitim_ortam_olusturucu import egitim_slab_uret, egitim_Sslabstate_to_normalizasyon
from gymnasium import spaces
from app.core.uzay_bilgileri import *
from app.core.slab_sabitleri import *
from app.rl.constants import *

class SlabTakvimiEnv(gym.Env):
    metadata = {"render_modes": []}


    # İçeride kullanıcağımız fonksiyonları içeriye koy
    def __init__(self,
            max_steps: int = 10000,
            reward_fn = None,
            simulate_fn = None,
            state_fn = None,
            slab_fn = None,
            zorluk_pencere: int = 4,
            ):
        super().__init__()

        self.hedef_km = HEDEF_KM
        self.toplam_uzunluk_km = 0.0
        self.zorluk_gecmisi = [] #geçmişteki zorlukları tutmak için
        self.zorluk_pencere = zorluk_pencere
        self.ilk_adim = True

        self.action_space = spaces.Discrete(20)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(havuz_boyutu + 1,ozellik_sayisi), dtype=np.float32
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
        self.toplam_uzunluk_km = 0
        self.zorluk_gecmisi = []
        self.ilk_adim = True
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
            reward = -5.0 # TODO İLERİDE DÜZENLE
            terminated = False
            truncated= self.current_step >= self.max_steps
            info = {"action_mask": mask, "invalid_aciton": True}
            return self.state, reward, terminated, truncated, info

        secilen_slab = self.state[action].copy()
        secilen_slab_gercek = self.slabstate[action].copy()

        onceki_slab_gercek = self.slabstate[20].copy()
        onceki_slab = self.state[20].copy()

        # Ödül Modülü -> dışardan verilmişse onu çağır, verilmemişse override ı kullan
        reward = self._compute_reward(secilen_slab_gercek, onceki_slab_gercek)

        # Secilen slabı havuzdan çıkart, yerine yenisini koy
        self.state[action], self.slabstate[action] = self._get_replacement_slab()

        # 21. satırı seçilen slab ile güncelle
        self.state[20] = secilen_slab
        self.slabstate[20] = secilen_slab_gercek


        self.toplam_uzunluk_km += float(secilen_slab_gercek[KEY_CIKIS_UZUNLUK]) / 1000.0

        # Simülasyon modülü -> Her adımda veya belirli aralıklarla durumu ilerlet
        # (sıcaklık düşüşü, durum güncellemesi gibi)
        if self.simulate_fn is not None:
            self.slabstate = self.simulate_fn(50, self.slabstate)
            self.state = egitim_Sslabstate_to_normalizasyon(self.slabstate)

        
        self.current_step += 1
        terminated = self._is_episode_done()
        truncated = self.current_step >= self.max_steps

        info = {"action_mask": self._get_action_mask()}

        assert not np.isnan(reward), f"Reward NaN geldi! secilen={secilen_slab_gercek}"
        assert not np.any(np.isnan(self.state)), f"State içinde NaN var! step={self.current_step}"
        #print("****************slablstate****************")
        #print(self.slabstate[1])
        #print("****************slab*******************")
        #print(self.state[1])
        #print("****************************************")

        return self.state, reward, terminated, truncated, info

    #***************************
    # MASKELEME
    #***************************

    # 20 boyutlu boolean maske. Ture = seçilebilir, False = seçilemez
    # Geçiş ksııtlarını bir önceki slaba göre kontrol et
    def _get_action_mask(self) -> np.ndarray:
        onceki_slab = self.slabstate[20]
        mask = np.ones(20, dtype=bool)

        if self.ilk_adim:
            return mask

        onceki_slab = self.slabstate[20]

        for i in range(20):
            aday = self.slabstate[i]
            genislik_farki = onceki_slab[KEY_GIRIS_GENISLIK] - aday[KEY_GIRIS_GENISLIK]
            kalinli_farki = onceki_slab[KEY_CIKIS_KALINLIK] - aday[KEY_CIKIS_KALINLIK]
            
            if abs(genislik_farki) > GENISLIK_LIMIT:
                mask[i] = False
                continue
            if abs(kalinli_farki) > KALINLIK_LIMIT:
                mask[i] = False
                continue
            
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

    def _get_replacement_slab(self) -> np.ndarray:
        if self.slab_fn is not None:
            slab = egitim_slab_uret()
            return self.slab_fn(slab), slab

        raise NotImplementedError("slab_fn verilmedi ve _get_replacement_slab override edilmedi")
        
    def _compute_reward(self, secilen_slab_gercek: np.ndarray, onceki_slab_gercek: np.ndarray) -> float:
        if self.reward_fn is not None:
                return self.reward_fn(secilen_slab_gercek, onceki_slab_gercek, self.state)

        if self.ilk_adim:
            r_genislik = 0.0
            r_kalinlik = 0.0
        else:
            genislik_farki = onceki_slab_gercek[KEY_GIRIS_GENISLIK] - secilen_slab_gercek[KEY_GIRIS_GENISLIK]
            kalinlik_farki = onceki_slab_gercek[KEY_CIKIS_KALINLIK] - secilen_slab_gercek[KEY_CIKIS_KALINLIK]

            # Eğer doğru yönde (azalan) küçük fark iyi, tersi yönde ise ceza katalanarak artar
            r_genislik = (genislik_farki / GENISLIK_LIMIT) if genislik_farki >= 0 \
                else -2.0 * (abs(genislik_farki) / GENISLIK_LIMIT)

            r_kalinlik = (kalinlik_farki / KALINLIK_LIMIT) if kalinlik_farki >= 0 \
                else -2.0 * (abs(kalinlik_farki) / KALINLIK_LIMIT)

        sicaklik_ham = float(secilen_slab_gercek[KEY_SICAKLIK])
        r_sicaklik = (sicaklik_ham - ortam_sicakligi_cel) / (max_sicaklik_cel - ortam_sicakligi_cel)
        r_sicaklik = float(np.clip(r_sicaklik, 0.0, 1.0))

        yeni_zorluk = bool(secilen_slab_gercek[KEY_ZORLUK])
        r_zorluk = self._zorluk_pattern_odulu(yeni_zorluk)
        self.zorluk_gecmisi.append(yeni_zorluk)

        reward = (
            W_GENISLIK * r_genislik +
            W_KALINLIK * r_kalinlik +
            W_SICAKLIK * r_sicaklik +
            W_ZORLUK * r_zorluk
        )

        self.ilk_adim = False


        return float(reward)

    def _zorluk_pattern_odulu(self, yeni_zorluk: bool) -> float:
        son_pencere = self.zorluk_gecmisi[-self.zorluk_pencere:]
        son_zor_sayisi = sum(son_pencere)

        if yeni_zorluk:
            return 1.0 if son_zor_sayisi == 0 else -1.0
        else:
            return 0.1


    def _is_episode_done(self) -> bool:
        return self.toplam_uzunluk_km >= self.hedef_km    
        