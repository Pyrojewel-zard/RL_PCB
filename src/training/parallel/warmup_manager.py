# -*- coding: utf-8 -*-
from __future__ import annotations
import multiprocessing as mp
import os, uuid
from typing import Dict, Any, Generator, Tuple

# 全局缓存（fork 后可见）
_GLOBAL_ENVS = []

def _worker_entry_from_global(task_q: mp.Queue, result_q: mp.Queue, wid: int, base_seed: int):
    from src.training.parallel.warmup_worker import worker_loop_with_instance
    env = _GLOBAL_ENVS[wid]
    worker_loop_with_instance(task_q, result_q, env, wid, base_seed)

class WarmupManager:
    def __init__(self,
                 env_ctor_path: str = "src.training.parallel.env_factory:make_env",
                 cfg_dict: Dict[str, Any] | None = None,
                 environment_obj: Any = None,
                 num_workers: int = 8,
                 queue_size_factor: int = 4) -> None:
        mp.set_start_method("fork", force=True)
        self.ctx = mp.get_context("fork")

        self.env_ctor_path = env_ctor_path
        self.cfg_dict = dict(cfg_dict or {})
        self.environment_obj = environment_obj
        self.num_workers = int(num_workers)

        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
        os.environ.setdefault("RLPCB_DISABLE_TB", "1")
        os.environ.setdefault("RLPCB_DISABLE_LOG", "1")
        os.environ.setdefault("RLPCB_LIGHT_MODE", "1")

        qsize = max(8, self.num_workers * queue_size_factor)
        self.task_q: mp.Queue = self.ctx.Queue(maxsize=qsize)
        self.result_q: mp.Queue = self.ctx.Queue(maxsize=qsize)

        self._procs: list[mp.Process] = []
        self._closed = False
        self._run_id = uuid.uuid4().hex[:6]

        from src.training.parallel.env_factory import make_env
        cfg = dict(self.cfg_dict)
        base_seed = int(cfg.get("base_seed", 1234))
        cfg.setdefault("light_mode", True)

        _GLOBAL_ENVS.clear()
        for wid in range(self.num_workers):
            if self.environment_obj is not None:
                # 如果有 environment 對象，需要為每個 worker 創建新的副本
                # 因為 environment 對象不能直接複製，我們需要重新創建
                from core.environment.environment import environment
                from core.environment.parameters import parameters
                
                # 創建新的參數對象，使用不同的 seed
                new_params = parameters({
                    "pcb_file": self.environment_obj.parameters.pcb_file,
                    "training_pcb": self.environment_obj.parameters.training_pcb,
                    "evaluation_pcb": self.environment_obj.parameters.evaluation_pcb,
                    "net": self.environment_obj.parameters.net,
                    "use_dataAugmenter": False,  # 在 warmup 階段禁用數據增強，避免除零問題
                    "augment_position": False,
                    "augment_orientation": False,
                    "agent_max_action": self.environment_obj.parameters.agent_max_action,
                    "agent_expl_noise": self.environment_obj.parameters.agent_expl_noise,
                    "debug": self.environment_obj.parameters.debug,
                    "max_steps": self.environment_obj.parameters.max_steps,
                    "w": self.environment_obj.parameters.n,
                    "o": self.environment_obj.parameters.m,
                    "hpwl": self.environment_obj.parameters.p,
                    "seed": base_seed + 10 * wid,
                    "ignore_power": self.environment_obj.parameters.ignore_power,
                    "log_dir": self.environment_obj.parameters.log_dir,
                    "idx": self.environment_obj.parameters.idx,
                    "shuffle_idxs": self.environment_obj.parameters.shuffle_idxs,
                })
                
                env = environment(new_params)
                env.reset()
            else:
                # 否則使用配置字典
                cfg_w = dict(cfg)
                cfg_w["seed"] = base_seed + 10 * wid
                env = make_env(cfg_w)
            _GLOBAL_ENVS.append(env)

        for wid in range(self.num_workers):
            p = self.ctx.Process(
                target=_worker_entry_from_global,
                args=(self.task_q, self.result_q, wid, base_seed),
            )
            p.daemon = True
            p.start()
            self._procs.append(p)

    def collect(self,
                total_steps: int | None,
                chunk_per_worker: int = 1000) -> Generator[Tuple[int, Dict[str, Any]], None, None]:
        if chunk_per_worker <= 0:
            raise ValueError("chunk_per_worker must be > 0")
        sent = 0
        done = 0
        for _ in range(self.num_workers):
            if (total_steps is not None) and (sent >= total_steps):
                break
            self.task_q.put(("rollout", int(chunk_per_worker)))
            sent += chunk_per_worker
        while (total_steps is None) or (done < total_steps):
            wid, batch = self.result_q.get()
            n = len(batch["A"]) if isinstance(batch, dict) else len(batch)
            done += n
            yield wid, batch
            if (total_steps is None) or (sent < total_steps):
                self.task_q.put(("rollout", int(chunk_per_worker)))
                sent += chunk_per_worker

    def close(self) -> None:
        if self._closed:
            return
        for _ in range(self.num_workers):
            try:
                self.task_q.put(("stop", 0))
            except Exception:
                pass
        for p in self._procs:
            try:
                p.join(timeout=5.0)
            except Exception:
                pass
            if p.is_alive():
                try:
                    p.terminate()
                except Exception:
                    pass
        self._closed = True

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
