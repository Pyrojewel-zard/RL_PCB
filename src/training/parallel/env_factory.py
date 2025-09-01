# /home/yxl/RL_PCB/src/training/parallel/env_factory.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, Union
import importlib
import inspect

DEFAULT_CTOR = "core.environment.environment:environment"

def _import_from_string(path: str):
    if ":" not in path:
        raise ValueError(f"Invalid import path: {path!r}, expected 'package.module:callable'")
    mod, name = path.split(":", 1)
    m = importlib.import_module(mod)
    return getattr(m, name)

def _maybe_call(obj, name: str, *args, **kwargs):
    if hasattr(obj, name):
        fn = getattr(obj, name)
        if callable(fn):
            try:
                return fn(*args, **kwargs)
            except Exception:
                pass
    return None

def make_env(cfg_or_params: Union[Dict[str, Any], Any]):
    """
    构造环境实例（Linux/fork 预建用）：
      - 如果传入的是 parameters 对象：直接使用 ctor(params)
      - 如果传入的是配置字典：
          先试 parameters(cfg)；若 ctor 不接受再试 ctor(cfg)
    构造后若 cfg.light_mode=True，会尽量关闭渲染/日志/重校验（若环境实现了对应方法）。
    """
    # 检查是否已经传入了 environment 对象
    if hasattr(cfg_or_params, 'agents') and hasattr(cfg_or_params, 'parameters'):
        # 这看起来像是一个 environment 对象，直接返回
        env = cfg_or_params
        cfg = {"light_mode": True}  # 默认配置
    # 检查是否已经传入了 agent_parameters 对象
    elif hasattr(cfg_or_params, 'board') and hasattr(cfg_or_params, 'graph'):
        # 这看起来像是一个 agent_parameters 对象，需要创建 environment
        from core.environment.environment import environment
        # 我们需要从 agent_parameters 创建 environment，但这比较复杂
        # 所以最好直接传入 environment 对象
        raise RuntimeError("Please pass an environment object instead of agent_parameters")
    else:
        # 这是配置字典，需要构建 parameters
        cfg = cfg_or_params
        ctor_path = cfg.get("env_ctor", DEFAULT_CTOR)
        
        # 统一先尝试 parameters(cfg)
        try:
            from core.environment.parameters import parameters as env_parameters
            params = env_parameters(cfg)              # 不筛字段，直接交给工程的 parameters 处理
        except Exception as e_params:
            # 默认构造器：不能回退到 dict（environment 需要 parameters 对象）
            if ctor_path == DEFAULT_CTOR:
                raise RuntimeError(
                    "env_factory: Failed to construct environment with parameters(cfg). "
                    "Since you're using the default ctor "
                    "'core.environment.environment:environment', it requires a "
                    "`parameters` object. Please check your cfg for missing/invalid fields."
                ) from e_params

            # 非默认构造器：某些自定义 ctor 可能直接吃 dict —— 尝试一次兜底
            try:
                env = _import_from_string(ctor_path)(cfg)
                return env
            except Exception as e_dict:
                raise RuntimeError(
                    f"env_factory: Both ctor(parameters(cfg)) and ctor(cfg) failed for env_ctor={ctor_path}."
                ) from e_dict

    # 如果已经传入了 environment 对象，直接返回
    if 'env' in locals():
        # 轻量/静默（若实现了这些方法）
        if cfg.get("light_mode", True):
            for fn_name in ("set_light_mode", "disable_logging", "disable_render", "set_fast_checks"):
                _maybe_call(env, fn_name, True)
        return env
    
    # 使用 parameters 对象构造环境
    ctor = _import_from_string(ctor_path)
    env = ctor(params)

    # 轻量/静默（若实现了这些方法）
    if cfg.get("light_mode", True):
        for fn_name in ("set_light_mode", "disable_logging", "disable_render", "set_fast_checks"):
            _maybe_call(env, fn_name, True)

    return env
