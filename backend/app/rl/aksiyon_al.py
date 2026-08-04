import numpy as np
from sb3_contrib import MaskablePPO

_model = None

def model_yukleme(path: str = "models/denemeler/slab_takvimleme_ppo"):
    global _model
    if _model is None:
        _model = MaskablePPO.load(path)
    return _model


def aksiyon_sec(state: np.ndarray, action_mask: np.ndarray) -> int:
    # state: (21,7) normalize edilmiş gözlem
    # action_mask: (20,) boolean, env.action_masks() çıktısı

    model = model_yukleme()

    action, _states = model.predict(
        state,
        action_masks=action_mask,
        deterministic=True,
    )

    return int(action)