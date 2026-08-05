import os
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.monitor import Monitor

from app.rl.egitim_ortam_olusturucu import egitim_state_olustur, egitim_slab_vektor
from app.rl.egitim_simulasyon import egitim_simulasyon_calistir
from app.rl.egitim_env import SlabTakvimiEnv


def mask_fn(env: SlabTakvimiEnv) -> np.ndarray:
    return env.action_masks()


def env_olustur(rank: int, seed: int = 0):
    def _init():
        env = SlabTakvimiEnv(
            max_steps=2000,
            reward_fn=None,
            simulate_fn=egitim_simulasyon_calistir,
            state_fn=egitim_state_olustur,
            slab_fn=egitim_slab_vektor,
        )
        env = ActionMasker(env, mask_fn)
        env = Monitor(env)
        env.reset(seed=seed + rank)
        return env
    return _init


if __name__ == "__main__":
    N_ENVS = os.cpu_count() or 8   # örn. 8 çekirdek varsa 8 paralel env
    policy_kwargs = dict(
    net_arch=dict(pi=[128, 128], vf=[128, 128])
)
    vec_env = SubprocVecEnv(
        [env_olustur(rank=i) for i in range(N_ENVS)],
        start_method="fork",  # Linux'ta varsayılan, sorun olursa "spawn" dene
    )
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
        n_steps=2048 // N_ENVS,   # toplam rollout boyutu (n_steps * n_envs) sabit kalsın diye böldüm
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        ent_coef=0.01,
        tensorboard_log="./tensorboard_logs/",
        policy_kwargs=policy_kwargs,
    )

    TOPLAM_TIMESTEP = 600_000
    model.learn(total_timesteps=TOPLAM_TIMESTEP, progress_bar=True)

    model.save("models/denemeler/slab_takvimleme_ppo")
    vec_env.save("models/denemeler/vecnormalize_stats.pkl")
    print("Eğitim tamamlandı, model kaydedildi.")