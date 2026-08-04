import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor

from app.rl.egitim_ortam_olusturucu import egitim_state_olustur, egitim_slab_vektor
from app.rl.egitim_simulasyon import egitim_simulasyon_calistir
from app.rl.egitim_env import SlabTakvimiEnv


def mask_fn(env: SlabTakvimiEnv) -> np.ndarray:
    return env.action_masks()


def env_olustur():
    env = SlabTakvimiEnv(
        max_steps=2000,
        reward_fn=None,
        simulate_fn=egitim_simulasyon_calistir,
        state_fn=egitim_state_olustur,
        slab_fn=egitim_slab_vektor,
    )
    env = ActionMasker(env, mask_fn)
    env = Monitor(env)          # ep_rew_mean / ep_len_mean için şart
    return env


if __name__ == "__main__":
    vec_env = DummyVecEnv([env_olustur])
    vec_env = VecNormalize(
        vec_env,
        norm_obs=True,
        norm_reward=True,
        clip_obs=10.0,
        clip_reward=10.0,
    )

    model = MaskablePPO(
        MaskableActorCriticPolicy,
        vec_env,
        verbose=1,
        learning_rate=2e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        ent_coef=0.01,
        tensorboard_log="./tensorboard_logs/",
    )

    TOPLAM_TIMESTEP = 200_000
    model.learn(total_timesteps=TOPLAM_TIMESTEP, progress_bar=True)

    model.save("models/denemeler/slab_takvimleme_ppo")
    vec_env.save("models/denemeler/vecnormalize_stats.pkl")
    print("Eğitim tamamlandı, model kaydedildi.")