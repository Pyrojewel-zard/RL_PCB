# -*- coding: utf-8 -*-
"""
运行 warmup 阶段的脚本。
会启动 WarmupManager，生成探索数据填充经验回放池。
"""
from __future__ import annotations
import argparse
import os
from src.training.parallel.warmup_manager import WarmupManager
from src.training.parallel.cfg_loader import load_parallel_warmup_cfg
from src.training.parallel.env_factory import make_env


def main():
    parser = argparse.ArgumentParser(description="Run warmup sampling with multiple workers.")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to warmup_config.json (optional)")
    parser.add_argument("--steps", type=int, default=1000,
                        help="Number of steps per worker rollout")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel worker processes")
    args = parser.parse_args()

    # 加载配置
    cfg = load_parallel_warmup_cfg(args.config)
    print(f"[Warmup] Loaded config: {cfg}")

    # 构建环境工厂
    def ctor():
        return make_env(cfg)

    # 启动 WarmupManager
    manager = WarmupManager(
        env_ctor=ctor,
        num_workers=args.workers,
        base_seed=cfg.get("base_seed", 1234),
    )

    manager.start()

    print(f"[Warmup] Collecting {args.steps} steps per worker...")
    results = manager.run_rollouts(args.steps)

    # 简单统计
    total_samples = sum(len(batch["R"]) for _, batch in results)
    print(f"[Warmup] Finished. Collected {total_samples} transitions from {args.workers} workers.")

    manager.close()


if __name__ == "__main__":
    main()
