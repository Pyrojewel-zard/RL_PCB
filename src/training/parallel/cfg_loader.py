# src/training/parallel/cfg_loader.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import os
from typing import Dict, Any

_DEFAULT_JSON = os.path.join(os.path.dirname(__file__), "warmup_config.json")

def load_parallel_warmup_cfg(path: str | None = None) -> Dict[str, Any]:
    """Load warmup config from JSON; return sensible defaults if missing."""
    p = path or _DEFAULT_JSON
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    # Defaults (safe for Linux fork warmup)
    return {
        "base_seed": 1234,
        "light_mode": True,
        # You can override these in JSON or in code:
        # "pcb_file": "dataset/base/training.pcb",
        # "env_ctor": "core.environment.environment:environment",
        # "n": 1, "m": 1, "p": 1,
        # "max_steps": 600,
    }
