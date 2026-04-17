from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import UploadResponse
from app.services.bias_engine import describe_sensitive_columns, detect_target_column, detect_sensitive_columns
from app.services.file_service import (
    load_dataframe,
    make_analysis_id,
    preview_dataframe,
    save_analysis_metadata,
    save_upload_file,
)

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    model_file: UploadFile | None = File(None),
    target_column: str | None = Form(None),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV uploads are supported for the dataset.")

    analysis_id = make_analysis_id()
    csv_path = await save_upload_file(file, analysis_id, ".csv")
    model_path = None
    model_filename = None

    if model_file is not None and model_file.filename:
        model_extension = ".joblib"
        if model_file.filename.lower().endswith(".pkl"):
            model_extension = ".pkl"
        model_path = await save_upload_file(model_file, analysis_id, model_extension)
        model_filename = model_file.filename

    frame = load_dataframe(csv_path)
    detected_sensitive = detect_sensitive_columns(frame)
    detected_target = target_column or detect_target_column(frame)

    save_analysis_metadata(
        analysis_id,
        {
            "csv_path": csv_path,
            "model_path": model_path,
            "filename": file.filename,
            "model_filename": model_filename,
            "rows": int(len(frame)),
            "columns": list(frame.columns),
            "detected_sensitive_columns": detected_sensitive,
            "detected_target_column": detected_target,
            "preview": preview_dataframe(frame),
        },
    )

    return UploadResponse(
        analysis_id=analysis_id,
        filename=file.filename,
        model_filename=model_filename,
        rows=int(len(frame)),
        columns=list(frame.columns),
        detected_sensitive_columns=detected_sensitive,
        detected_target_column=detected_target,
        preview=preview_dataframe(frame),
    )

