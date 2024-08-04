from datetime import date
import logging
from io import BytesIO, StringIO
from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import pandas as pd

from fastapi import APIRouter, Form, Request, UploadFile

from app.core.database import Database, persons, persons_changelog
from app.core.config import settings
from app.models import Person, PersonsChangeLog


TEMPLATES = settings.TEMPLATES.TemplateResponse
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return TEMPLATES(
        "index.html",
        context={"request": request}
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
        logger.error(e)
        context["msg"] = f"Erro ao ler arquivo '{file.filename}'."
        context["alert_type"] = "danger"
        status_code = 400

    return TEMPLATES(
        "alert.html",
        status_code=status_code,
        context=context
    )


@router.get("/data/{_id}")
async def get_person(request: Request, _id: str):
    """Edição dos dados da tabela no banco."""
    context: dict[str, Any] = {"request": request}
    status_code: int
    try:
        record = await Database.get_person(_id)
        context["person"] = record
        status_code = 200
    except InvalidId as e:
        logger.debug(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code
    )


@router.get("/data/{_id}/edit")
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
        logger.debug(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code
    )


@router.put("/data/{_id}")
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
        logger.error(e)
        context["error"] = "Person id not found."
        status_code = 404

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code,
        block_name="content",
    )


@router.get("/create")
async def create_new_person_get(request: Request):
    context: dict[str, Any] = {"request": request}
    return TEMPLATES(
        "create_person.html",
        context=context,
    )


@router.post("/create")
async def create_new_person_post(
    request: Request,
    nome: str = Form(""),
    data_nascimento: str = Form(""),
    genero: str = Form(""),
    nacionalidade: str = Form(""),
    data_criacao: str = Form(""),
    data_atualizacao: str = Form(""),
):
    context: dict[str, Any] = {"request": request}
    try:
        rec_values = {
            "nome": nome,
            "data_nascimento": data_nascimento,
            "genero": genero,
            "nacionalidade": nacionalidade,
            "data_criacao": data_criacao,
            "data_atualizacao": data_atualizacao
        }
        record = await Database.create_one_person(rec_values)
        context["person"] = record
        status_code = 200
    except Exception as e:
        status_code = 400
        logger.error(e)

    return TEMPLATES(
        "person_data.html",
        context=context,
        status_code=status_code,
        block_name="content",
    )


@router.get("/all")
async def get__all_persons(request: Request):
    valid_rec_list = await Database.get_all_persons()
    context: dict[str, Any] = {"request": request}
    context["persons_list"] = valid_rec_list
    status_code = 200
    return TEMPLATES(
        "persons_table.html",
        context=context,
        status_code=status_code,
    )


@router.get("/changelog")
async def get_persons_changelong(request: Request, _id: str | None = None):
    # TODO: move this to database class
    context: dict[str, Any] = {"request": request}
    try:
        if _id:
            auditlogs = persons_changelog.find({"person_id": _id})
        else:
            auditlogs = persons_changelog.find()
        logs_list = [PersonsChangeLog(**log) async for log in auditlogs]
        status_code = 200
        context["person_id"] = _id
        context["auditlog_list"] = logs_list
    except Exception as e:
        logger.error(e)
        status_code = 404
        context["person_id"] = f"'{_id}' NOT FOUND"
        context["auditlog_list"] = []

    # logs_list = await auditlogs.to_list(None)
    # auditlog_list = [PersonsChangeLog(**log) for log in logs_list]

    return TEMPLATES(
        "changes_table.html",
        context=context,
        status_code=status_code,
    )


@router.get("/export_csv")
async def export_download_as_csv():
    """Exporta a tabela atualizada/filtrada em formato CSV."""
    # TODO: adicionar filtros
    result = persons.find()
    result = await result.to_list(None)
    for rec in result:
        del rec["_id"]

    df = pd.DataFrame(result)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=perssoas.csv"}
    )
