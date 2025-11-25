from __future__ import annotations

import json
import logging
from typing import Any, Dict


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure application-wide logging once."""

    logger = logging.getLogger("medassist")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def safe_json_loads(payload: str) -> Dict[str, Any]:
    """Attempt to parse JSON even if surrounded by prose."""

    payload = payload.strip()
    if not payload:
        return {}

    if payload[0] != "{":
        first_brace = payload.find("{")
        last_brace = payload.rfind("}")
        if first_brace != -1 and last_brace != -1:
            payload = payload[first_brace : last_brace + 1]

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}

