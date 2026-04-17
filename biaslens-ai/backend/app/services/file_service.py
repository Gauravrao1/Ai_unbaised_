import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import UploadFile

from app.core.config import get_settings


settings = get_settings()
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = Path(settings.uploads_dir)
if not UPLOAD_DIR.is_absolute():
    UPLOAD_DIR = BASE_DIR.parent / UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

METADATA_SUFFIX = ".json"


def make_analysis_id() -> str:
    return uuid.uuid4().hex[:12]


async def save_upload_file(upload_file: UploadFile, analysis_id: str, suffix: str) -> str:
    destination = UPLOAD_DIR / f"{analysis_id}{suffix}"
    contents = await upload_file.read()
    destination.write_bytes(contents)
    return str(destination)


def load_dataframe(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def read_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(_to_json_safe(payload), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def metadata_path(analysis_id: str) -> Path:
    return UPLOAD_DIR / f"{analysis_id}{METADATA_SUFFIX}"


def save_analysis_metadata(analysis_id: str, payload: Dict[str, Any]) -> None:
    metadata = {
        **payload,
        "analysis_id": analysis_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json_file(metadata_path(analysis_id), metadata)


def load_analysis_metadata(analysis_id: str) -> Dict[str, Any]:
    return read_json_file(metadata_path(analysis_id))


def preview_dataframe(df: pd.DataFrame, limit: int = 8) -> list[dict[str, Any]]:
    preview = df.head(limit).copy()
    # Cast to object first so None values are preserved instead of becoming NaN again.
    preview = preview.astype(object).where(pd.notnull(preview), None)
    return _to_json_safe(preview.to_dict(orient="records"))


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_to_json_safe(item) for item in value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value

