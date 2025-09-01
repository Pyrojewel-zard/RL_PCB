"""
Main training script for PCB routing RL.
Linux fork-style warmup integrated:
- Offline prefill from NPZ via RLPCB_PREFILL_DIR (optional)
- Online parallel warmup (CPU-only workers) before training starts
"""

from typing import Any
from core.environment.environment import environment
from core.environment.parameters import parameters

import numpy as np
import torch
import sys
import os
import random

from run_config import cmdline_args, write_desc_log
from hyperparameters import load_hyperparameters_from_file
from model_setup import setup_model
from callbacks import log_and_eval_callback

# ==== Warmup helpers (Linux fork version) ====
from glob import glob
from src.training.parallel.warmup_manager import WarmupManager
from src.training.parallel.cfg_loader import load_parallel_warmup_cfg


# ----------------- Replay helpers -----------------

def _push_batch_to_replay(buf, batch):
    """Write a warmup batch into the replay buffer; supports dict or list((s,a,r,s2,d),...)."""
    if isinstance(batch, dict):
        S, A, R, S2, D = batch["S"], batch["A"], batch["R"], batch["S2"], batch["D"]
        for s, a, r, s2, dn in zip(S, A, R, S2, D):
            # 處理動作：如果是向量，使用原始向量；如果是標量，轉換為 int
            if isinstance(a, (list, tuple, np.ndarray)) and len(a) > 1:
                buf.add(s, a, float(r), s2, float(dn))
            else:
                buf.add(s, int(a), float(r), s2, float(dn))
    else:
        for (s, a, r, s2, dn) in batch:
            # 處理動作：如果是向量，使用原始向量；如果是標量，轉換為 int
            if isinstance(a, (list, tuple, np.ndarray)) and len(a) > 1:
                buf.add(s, a, float(r), s2, float(dn))
            else:
                buf.add(s, int(a), float(r), s2, float(dn))


def prefill_from_npz_dir(buf, dirpath: str, max_files=None, shuffle=True) -> int:
    """Import warmup NPZ files into replay buffer. Returns number of transitions imported."""
    files = sorted(glob(f"{dirpath}/prefill_*.npz"))
    if not files:
        print(f"[Prefill] no npz under {dirpath}")
        return 0
    if shuffle:
        np.random.shuffle(files)
    if max_files:
        files = files[:max_files]
    total = 0
    for f in files:
        d = np.load(f)
        for s, a, r, s2, dn in zip(d["S"], d["A"], d["R"], d["S2"], d["D"]):
            # 處理動作：如果是向量，使用原始向量；如果是標量，轉換為 int
            if isinstance(a, (list, tuple, np.ndarray)) and len(a) > 1:
                buf.add(s, a, float(r), s2, float(dn))
            else:
                buf.add(s, int(a), float(r), s2, float(dn))
            total += 1
    print(f"[Prefill] imported {total} transitions from {len(files)} files")
    return total


# ----------------- Seed / logging -----------------

best_reward = -np.inf  # New best model, you could save the agent here


def setup_seed(seed):
    random.seed(int(seed))     # Convert numpy int to Python int to avoid deprecation warning
    np.random.seed(seed)       # Seed numpy RNG
    torch.manual_seed(seed)    # Seed the RNG for all devices

    if torch.cuda.is_available():
        # Deterministic operations for CuDNN, it may impact performances
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def program_info(device):
    if device == "cuda":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device("cpu")

    print(f"using {device}")


def log_configuration(writer, args=None, cmdline_args=None, global_step=1):
    s = str("")

    if cmdline_args is not None:
        s += str(cmdline_args)
        s += "<br><br>"

    if args is not None:
        s += str(args).replace(",", "<br>")[10:-2]

    writer.add_text(tag="params", text_string=s, global_step=global_step)
    writer.flush()


# ----------------- Warmup integration (Linux fork) -----------------

def setup_warmup(
    replay_buffer,
    prefill_dir: str | None = None,
    prefill_max_files: int | None = None,
    use_online_warmup: bool = True,
    warmup_workers: int = 8,
    prefill_min: int | None = None,
    online_chunk: int = 1000,
    environment_obj: Any = None,
):
    """
    Call AFTER replay_buffer/model is created.
    Returns (mgr, online_stream):
      - mgr: WarmupManager or None
      - online_stream: generator (infinite stream) or None
    """
    # Keep training process free to use GPU; workers will be CPU-only internally.
    os.environ.setdefault("RLPCB_DISABLE_TB", "0")
    os.environ.setdefault("RLPCB_DISABLE_LOG", "0")
    os.environ.setdefault("RLPCB_LIGHT_MODE", "1")  # optional

    # 1) Optional: offline NPZ import
    if prefill_dir:
        prefill_from_npz_dir(replay_buffer, prefill_dir, max_files=prefill_max_files, shuffle=True)

    mgr = None
    online_stream = None
    if use_online_warmup:
        wcfg = load_parallel_warmup_cfg()  # reads src/training/parallel/warmup_config.json if present
        wcfg.setdefault("light_mode", True)
        wcfg.setdefault("base_seed", 1234)

        # Linux fork manager (prebuild envs in parent, inherit by fork)
        mgr = WarmupManager(
            env_ctor_path="src.training.parallel.env_factory:make_env",
            cfg_dict=wcfg,
            environment_obj=environment_obj,
            num_workers=int(warmup_workers),
        )

        # Default prefill target: 10% capacity, min 20k
        if prefill_min is None:
            cap = getattr(replay_buffer, "capacity", 200_000)
            prefill_min = max(20_000, int(0.1 * cap))

        # Eagerly prefill a small chunk to de-cold-start
        warmed = 0
        for wid, batch in mgr.collect(total_steps=prefill_min, chunk_per_worker=int(online_chunk)):
            _push_batch_to_replay(replay_buffer, batch)
            warmed += (len(batch["A"]) if isinstance(batch, dict) else len(batch))
            if warmed >= prefill_min:
                break

        # If you need continuous top-up during training, keep the stream:
        # (Your model.learn() encapsulates the training loop, so this is optional.)
        online_stream = mgr.collect(total_steps=None, chunk_per_worker=int(online_chunk))

    return mgr, online_stream


def drain_warmup_stream(online_stream, replay_buffer, max_chunks: int = 3):
    """
    If you want to sip a bit from the online warmup stream during training,
    call this inside your training loop (if you expose it).
    """
    if online_stream is None:
        return online_stream
    for _ in range(max_chunks):
        try:
            wid, new_batch = next(online_stream)
        except StopIteration:
            online_stream = None
            break
        _push_batch_to_replay(replay_buffer, new_batch)
    return online_stream


# ----------------- Training -----------------

def training_run(settings):
    setup_seed(seed=settings["seed"][settings["run"]])

    settings["log_dir"] = os.path.join(
        settings["tensorboard_dir"],
        settings["run_name"] + f'_{settings["run"]}_{settings["policy"]}'
    )

    # Create directory if it doesn't exist.
    if not os.path.isdir(settings["tensorboard_dir"]):
        os.makedirs(settings["tensorboard_dir"])

    # Create directory if it doesn't exist.
    if not os.path.isdir(settings["log_dir"]):
        os.makedirs(settings["log_dir"])

    hp = load_hyperparameters_from_file(settings["hyperparameters"])

    env_params = parameters({
        "pcb_file": settings["training_pcb"],
        "training_pcb": settings["training_pcb"],
        "evaluation_pcb": settings["evaluation_pcb"],
        "net": "",
        "use_dataAugmenter": True,
        "augment_position": True,
        "augment_orientation": True,
        "agent_max_action": 1,
        "agent_expl_noise": hp["expl_noise"],
        "debug": False,
        "max_steps": 200,
        "w": settings["w"],
        "o": settings["o"],
        "hpwl": settings["hpwl"],
        "seed": settings["seed"][settings["run"]],
        "ignore_power": True,
        "log_dir": settings["log_dir"],
        "idx": settings["pcb_idx"],
        "shuffle_idxs": settings["shuffle_training_idxs"],
    })

    env = environment(env_params)
    env.reset()

    model = setup_model(
        model_type=settings["policy"],
        train_env=env,
        hyperparameters=hp,
        device=settings["device"],
        early_stopping=settings["early_stopping"],
        verbose=settings["verbose"]
    )

    # === Offline NPZ prefill via env var (optional) ===
    prefill_dir = os.environ.get("RLPCB_PREFILL_DIR")
    if prefill_dir:
        # fetch the model's replay buffer
        rb = None
        for name in ("replay_buffer", "buffer", "rb", "memory"):
            if hasattr(model, name):
                rb = getattr(model, name)
                break
        if rb is not None:
            try:
                imported = prefill_from_npz_dir(rb, prefill_dir, max_files=None, shuffle=True)
                print(f"[Prefill] imported {imported} transitions from {prefill_dir}")
            except Exception as e:
                print(f"[Prefill] WARNING: failed to import from {prefill_dir}: {e}")
        else:
            print("[Prefill] WARNING: model has no replay buffer attribute; skip npz import")
    # === end offline prefill ===

    # === Online warmup prefill (Linux fork; CPU-only workers) ===
    # If your model exposes the replay buffer:
    replay_buffer = None
    for name in ("replay_buffer", "buffer", "rb", "memory"):
        if hasattr(model, name):
            replay_buffer = getattr(model, name)
            break

    mgr = None
    online_stream = None
    if replay_buffer is not None:
        # Use warmup_config.json defaults; override via code or env if needed.
        mgr, online_stream = setup_warmup(
            replay_buffer=replay_buffer,
            prefill_dir=None,               # you can still use RLPCB_PREFILL_DIR above
            prefill_max_files=None,
            use_online_warmup=False,        # 暫時禁用並行 warmup，避免除零問題
            warmup_workers=settings.get("warmup_workers", 8),
            prefill_min=None,               # defaults to max(20k, 0.1 * capacity)
            online_chunk=settings.get("warmup_chunk", 1000),
            environment_obj=env,
        )
    else:
        print("[Warmup] WARNING: no replay buffer found on model; skip online warmup.")

    # ---- regular training ----
    callback = log_and_eval_callback(
        log_dir=settings["log_dir"],
        settings=settings,
        hyperparameters=hp,
        model=model,
        eval_freq=settings["evaluate_every"],
        verbose=settings["verbose"],
        training_log="training.log",
        num_evaluations=16
    )

    write_desc_log(
        full_fn=os.path.join(settings["log_dir"], f'{settings["run_name"]}_desc.log'),
        settings=settings,
        hyperparameters=hp,
        model=model
    )

    model.explore_for_expert_targets(settings["target_exploration_steps"])
    model.learn(
        timesteps=settings["max_timesteps"],
        callback=callback,
        start_timesteps=settings["start_timesteps"],
        incremental_replay_buffer=settings["incremental_replay_buffer"]
    )

    # Close warmup manager if created
    if mgr is not None:
        try:
            mgr.close()
        except Exception:
            pass

    return [callback.best_metrics, callback.best_mean_metrics]


def main():
    args, settings = cmdline_args()

    if settings["redirect_stdout"] is True:
        redirection_file = os.path.join(
            settings["tensorboard_dir"],
            f"{settings['policy']}_{settings['experiment']}.stdout"
        )
        sys.stdout = open(redirection_file, "w", encoding="utf-8")

    if settings["redirect_stderr"] is True:
        redirection_file = os.path.join(
            settings["tensorboard_dir"],
            f"{settings['policy']}_{settings['experiment']}.stderr"
        )
        sys.stderr = open(redirection_file, "w", encoding="utf-8")

    program_info(args.device)

    mean_best_rewards = []
    mean_best_steps = []
    mean_best_mean_rewards = []
    mean_best_mean_steps = []

    for run in range(settings["runs"]):
        settings["run"] = run
        perf_metrics = training_run(settings=settings)

        mean_best_rewards.append(perf_metrics[0][0])
        mean_best_steps.append(perf_metrics[0][1])
        mean_best_mean_rewards.append(perf_metrics[1][0])
        mean_best_mean_steps.append(perf_metrics[1][1])

    print(f"mean best_reward = {np.mean(mean_best_rewards)}")
    print(f"mean best_step = {np.mean(mean_best_steps)}")
    print(f"mean best_mean_reward = {np.mean(mean_best_mean_rewards)}")
    print(f"mean best_mean_step = {np.mean(mean_best_mean_steps)}")


if __name__ == "__main__":
    main()
