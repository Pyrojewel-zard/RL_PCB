# -*- coding: utf-8 -*-
"""
修复版环境工厂：从 cfg 创建"轻量/静默"的 Env。
- 使用正确的导入路径
- 支持 cfg["env_ctor"] 指定 "pkg.mod:callable" 自定义构造器；
- 否则尝试默认的 environment(settings) 风格；
- 构造后尽可能关闭重校验/渲染/日志。
"""
from __future__ import annotations
import importlib
from typing import Any, Dict

def _import_from_string(path: str):
    mod, func = path.split(":", 1)
    m = importlib.import_module(mod)
    return getattr(m, func)

def _maybe_call(obj, name: str, *args, **kw):
    if hasattr(obj, name):
        fn = getattr(obj, name)
        try:
            return fn(*args, **kw) if callable(fn) else None
        except Exception:
            return None
    return None

def make_env(cfg: Dict[str, Any]):
    # 1) 允许外部直接指定构造器
    if "env_ctor" in cfg:
        ctor = _import_from_string(cfg["env_ctor"])
        env = ctor(cfg)
    else:
        # 2) 尝试默认工程接口（修复了导入路径）
        try:
            from src.training.core.environment.environment import environment as _environment
            env = _environment(cfg)
        except Exception as e:
            raise RuntimeError(
                "env_factory: 无法构造环境。请在 cfg['env_ctor'] 提供 'pkg.mod:callable'，"
                "或者确保 src.training.core.environment.environment 可用。"
            ) from e

    # 轻量/静默模式（两侧都做：worker 的 env var + 这里的实例方法）
    if cfg.get("light_mode", True):
        for fn_name in ("set_light_mode", "disable_logging", "disable_render", "set_fast_checks"):
            _maybe_call(env, fn_name, True)

    return env
