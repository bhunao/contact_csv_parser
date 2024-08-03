from datetime import date
import logging
from io import StringIO
from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import HTMLResponse, RedirectResponse
import pandas as pd

from fastapi import APIRouter, Form, Request, UploadFile

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
    context: dict[str, Any] = {"request": request}
    try:
        records = await csv_file_to_dict(file)
        new_recs = await Database.create_persons(records)
        n = len(new_recs.inserted_ids) if new_recs else 0
        context["msg"] = f"{n} new records created from file.",
        context["alert_type"] = "success"
        status_code = 200
    except Exception as e:
        _logger.error(e)
        context["msg"] = f"Erro ao ler arquivo '{file.filename}'."
        context["alert_type"] = "danger"
        status_code = 400

    return TEMPLATES(
        "alert.html",
        status_code=status_code,
        context=context
    )


@router.get("/{_id}")
async def get_person(request: Request, _id: str):
    """Edição dos dados da tabela no banco."""
    context: dict[str, Any] = {"request": request}
    status_code: int
    try:
        record = await Database.get_person(_id)
        context["person"] = record
        status_code = 200
    except InvalidId as e:
        _logger.debug(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code
    )


@router.get("/{_id}/edit")
async def edit_person(request: Request, _id: str):
    """Edição dos dados da tabela no banco."""
    context: dict[str, Any] = {"request": request}
    status_code: int
    try:
        record = await Database.get_person(_id)
        context["edit"] = True
        context["person"] = record
        status_code = 200
    except InvalidId as e:
        _logger.debug(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code
    )


@router.put("/{_id}")
async def edit_person_put(request: Request, _id: str,
                          nome: str = Form(""),
                          data_nascimento: str = Form(""),
                          genero: str = Form(""),
                          nacionalidade: str = Form(""),
                          ):
    """Edição dos dados da tabela no banco."""
    context: dict[str, Any] = {"request": request}
    status_code: int

    try:
        rec_values = {
            "nome": nome,
            "data_nascimento": data_nascimento,
            "genero": genero,
            "nacionalidade": nacionalidade,
            "data_criacao": date.today(),
            "data_atualizacao": date.today()
        }
        updated = await Database.edit_person(_id, rec_values)
        context["person"] = updated
        status_code = 200
    except Exception as e:
        _logger.error(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code,
        block_name="content",
    )
