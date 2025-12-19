# -*- coding: utf-8 -*-
"""Config schema validation and migrations.

Config files are user-editable. This module:
- migrates old versions forward
- validates known keys/types
- returns a sanitized dict + warnings (strings)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


LATEST_CONFIG_VERSION = 2


def _as_bool(val: Any) -> bool | None:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("1", "true", "yes", "y", "on"):
            return True
        if v in ("0", "false", "no", "n", "off"):
            return False
    if isinstance(val, int):
        return bool(val)
    return None


def migrate_config(cfg: Any) -> Tuple[Dict[str, Any], List[str]]:
    warnings: List[str] = []
    if not isinstance(cfg, dict):
        return {}, ["config is not an object; ignoring"]

    cfg = dict(cfg)
    try:
        ver = int(cfg.get("configVersion", 0) or 0)
    except Exception:
        ver = 0
        warnings.append("invalid configVersion; treating as 0")

    # v0 -> v1: introduce ui.lang + configVersion
    if ver < 1:
        ui = cfg.get("ui")
        if not isinstance(ui, dict):
            ui = {}
        ui.setdefault("lang", "auto")
        cfg["ui"] = ui
        cfg["configVersion"] = 1
        ver = 1

    # v1 -> v2: normalize ui.lang values + bump version
    if ver < 2:
        ui = cfg.get("ui")
        if not isinstance(ui, dict):
            ui = {}
        lang = ui.get("lang", "auto")
        if lang not in ("auto", "zh", "en"):
            ui["lang"] = "auto"
            warnings.append("ui.lang invalid; reset to auto")
        cfg["ui"] = ui
        cfg["configVersion"] = 2
        ver = 2

    if ver > LATEST_CONFIG_VERSION:
        warnings.append(f"configVersion {ver} is newer than supported {LATEST_CONFIG_VERSION}")

    return cfg, warnings


def validate_and_sanitize_config(cfg: Dict[str, Any], defaults: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    warnings: List[str] = []
    out: Dict[str, Any] = {}

    # Always keep configVersion if present.
    try:
        out["configVersion"] = int(cfg.get("configVersion", defaults.get("configVersion", LATEST_CONFIG_VERSION)))
    except Exception:
        out["configVersion"] = defaults.get("configVersion", LATEST_CONFIG_VERSION)
        warnings.append("configVersion not an int; using default")

    def _copy_str(key: str):
        val = cfg.get(key)
        if val is None:
            return
        if isinstance(val, str) and val.strip():
            out[key] = val
        else:
            warnings.append(f"{key} invalid type; ignored")

    _copy_str("mainBranch")
    _copy_str("worktreeDir")
    _copy_str("gitTool")

    # ui
    ui = cfg.get("ui")
    if ui is not None:
        if isinstance(ui, dict):
            ui_out: Dict[str, Any] = {}
            lang = ui.get("lang")
            if isinstance(lang, str) and lang in ("auto", "zh", "en"):
                ui_out["lang"] = lang
            elif lang is not None:
                warnings.append("ui.lang invalid; ignored")
            if ui_out:
                out["ui"] = ui_out
        else:
            warnings.append("ui invalid type; ignored")

    # review
    review = cfg.get("review")
    if review is not None:
        if isinstance(review, dict):
            r_out: Dict[str, Any] = {}
            default_tool = review.get("defaultTool")
            if isinstance(default_tool, str) and default_tool:
                r_out["defaultTool"] = default_tool
            models = review.get("models")
            if isinstance(models, dict):
                m_out: Dict[str, str] = {}
                for k, v in models.items():
                    if isinstance(k, str) and isinstance(v, str) and k and v:
                        m_out[k] = v
                r_out["models"] = m_out
            use_wsl = review.get("useWsl")
            if use_wsl is not None:
                b = _as_bool(use_wsl)
                if b is None:
                    warnings.append("review.useWsl invalid; ignored")
                else:
                    r_out["useWsl"] = b
            if r_out:
                out["review"] = r_out
        else:
            warnings.append("review invalid type; ignored")

    # merge
    merge = cfg.get("merge")
    if merge is not None:
        if isinstance(merge, dict):
            m_out: Dict[str, Any] = {}
            tool = merge.get("tool")
            if isinstance(tool, str) and tool:
                m_out["tool"] = tool
            tp = merge.get("toolPriority")
            if isinstance(tp, list):
                m_out["toolPriority"] = [x for x in tp if isinstance(x, str) and x]
            if m_out:
                out["merge"] = m_out
        else:
            warnings.append("merge invalid type; ignored")

    # submodules
    submodules = cfg.get("submodules")
    if submodules is not None:
        if isinstance(submodules, list):
            s_out = []
            for sm in submodules:
                if not isinstance(sm, dict):
                    continue
                path = sm.get("path")
                main = sm.get("mainBranch")
                if isinstance(path, str) and path and isinstance(main, str) and main:
                    s_out.append({"path": path, "mainBranch": main})
            out["submodules"] = s_out
        else:
            warnings.append("submodules invalid type; ignored")

    # availableTools (usually auto-detected; keep only if sane)
    at = cfg.get("availableTools")
    if at is not None:
        if isinstance(at, dict):
            out["availableTools"] = at
        else:
            warnings.append("availableTools invalid type; ignored")

    return out, warnings

