import logging
from io import StringIO
from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import HTMLResponse
import pandas as pd

from fastapi import APIRouter, Request, UploadFile

from app.core.database import Database, persons
from app.core.config import settings
from app.models import Person


TEMPLATES = settings.TEMPLATES.TemplateResponse
_logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return TEMPLATES(
        request,
        "index.html"
    )


async def csv_file_to_dict(file: UploadFile) -> list[dict[str, Any]]:
    content = await file.read()
    content = str(content, "utf-8")
    content = StringIO(content)
    csv = pd.read_csv(content)
    records = csv.to_dict("records")
    return records


@router.post("/upload_csv", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile):
    """Recebe o arquivo CSV enviado pelo usuário."""
    # await client.server_info()
    try:
        records = await csv_file_to_dict(file)
        new_recs = await Database.create_persons(records)
        n = len(new_recs.inserted_ids) if new_recs else 0
        context = {
            "msg": f"{n} new records created from file.",
            "alert_type": "success"
        }
        status_code = 200
    except Exception as e:
        _logger.error(e)
        context = {
            "msg": f"Erro ao ler arquivo '{file.filename}'.",
            "alert_type": "danger"
        }
        status_code = 400

    return TEMPLATES(
        request,
        "alert.html",
        status_code=status_code,
        context=context
    )


@router.get("/{_id}")
async def get_person(request: Request, _id: str):
    """Edição dos dados da tabela no banco."""
    context: dict[str, Any]
    status_code: int
    try:
        record = await Database.get_person(_id)
        context = {
            "person": record
        }
        status_code = 200
    except InvalidId as e:
        _logger.debug(e)
        context = {
            "error": "Person id not found."
        }
        status_code = 404

    return TEMPLATES(
        request,
        "person_data.html",
        context=context,
        status_code=status_code
    )
