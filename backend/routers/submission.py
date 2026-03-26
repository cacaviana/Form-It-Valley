import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from dtos.submission.create_submission.request import CreateSubmissionRequest
from dtos.submission.create_submission.response import CreateSubmissionResponse
from services.submission_service import SubmissionService

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

_service = SubmissionService()

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


@router.get("")
async def list_submissions():
    """Lista todas as submissions."""
    return await _service.list_all()


@router.get("/flow/{flow_id}")
async def list_by_flow(flow_id: str):
    """Lista submissions de um flow especifico."""
    return await _service.list_by_flow(flow_id)


@router.get("/{submission_id}")
async def get_submission(submission_id: str):
    """Busca submission por ID."""
    result = await _service.get_by_id(submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Submission nao encontrada")
    return result


@router.post("", status_code=201, response_model=CreateSubmissionResponse)
async def create_submission(request: CreateSubmissionRequest):
    """Cria submission e gera orcamento se aplicavel."""
    try:
        result = await _service.create(request.model_dump())
        return CreateSubmissionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{submission_id}/export", response_class=PlainTextResponse)
async def export_submission(submission_id: str):
    """Exporta devis como texto e salva localmente."""
    result = await _service.get_by_id(submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Submission nao encontrada")

    # Salvar arquivo local
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = result.get("flow_slug", "unknown")
    client = result.get("client_name", "unknown").replace(" ", "_")
    filename = f"devis_{slug}_{client}_{timestamp}.txt"
    filepath = os.path.join(EXPORTS_DIR, filename)

    content = f"DEVIS - {result.get('flow_slug', '')}\n"
    content += f"Date: {result.get('created_at', '')}\n"
    content += f"Client: {result.get('client_name', '')}\n"
    content += f"Email: {result.get('client_email', '')}\n"
    content += f"Tel: {result.get('client_phone', 'N/A')}\n"
    content += f"Adresse: {result.get('client_address', 'N/A')}\n\n"
    content += "--- REPONSES ---\n"
    for a in result.get("answers", []):
        content += f"- {a.get('question', '')}: {a.get('value', '')}\n"
    content += "\n--- DEVIS ---\n"
    content += result.get("quote_text", "Aucun devis genere") + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Salvar JSON tambem
    json_path = filepath.replace(".txt", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Saved-Path": filepath,
        }
    )


@router.delete("/{submission_id}", status_code=204)
async def delete_submission(submission_id: str):
    """Remove submission."""
    deleted = await _service.delete(submission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Submission nao encontrada")
