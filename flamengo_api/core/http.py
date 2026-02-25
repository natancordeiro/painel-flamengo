from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from flask import jsonify


def _json_default(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def ok(data: Any = None, *, status: int = 200):
    payload: Dict[str, Any] = {"success": True}
    if data is not None:
        payload["data"] = data
    return jsonify(payload, default=_json_default), status


def err(message: str, *, status: int = 400, code: str = "bad_request", details: Optional[dict] = None):
    payload: Dict[str, Any] = {
        "success": False,
        "error": {"code": code, "message": message},
    }
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status
