import pandas as pd
from datetime import datetime
from io import BytesIO
import logging
from typing import Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import InsertOne
from pymongo.results import InsertManyResult

from app.core.config import settings
from app.models import Person, PersonsChangeLog


logger = logging.getLogger(__name__)
mongo_uri = "mongodb://{user}:{password}@mongodb:27017".format
MONGO_URI: str = mongo_uri(
    user=settings.MONGO_INITDB_ROOT_USERNAME,
    password=settings.MONGO_INITDB_ROOT_PASSWORD
)
client = AsyncIOMotorClient(MONGO_URI)
database = client.get_database("zoox")

persons = database.get_collection("persons")
persons_changelog = database.get_collection("persons_changelog")

DictAny = dict[str, Any]


class Database:
    @classmethod
    async def create_persons(cls, persons_list: list[DictAny]) -> InsertManyResult | None:
        to_insert = []
        day: str
        month: str
        year: str
        first: str
        last: str
        for record in persons_list:
            date_fields = ("data_nascimento", "data_criacao",
                           "data_atualizacao")
            for d_field in date_fields:
                first, month, last = record[d_field].split("/")
                if len(first) == 4:
                    year = first
                    day = last
                else:
                    year = last
                    day = first

                record[d_field] = datetime.strptime(
                    f"{year}-{month}-{day}", "%Y-%m-%d")

            valid_model = Person(**record)
            dump_rec = valid_model.model_dump()
            _person = await persons.find_one(dump_rec)
            if not _person:
                to_insert.append(dump_rec)
        if to_insert:
            inserted = await persons.insert_many(to_insert)
            return inserted
        return None

    @classmethod
    async def get_person(cls, _id: str) -> Person:
        result: DictAny = await persons.find_one({"_id": ObjectId(_id)})
        valid_record = Person(**result)
        valid_record.id = result['_id']
        return valid_record

    @classmethod
    async def audit_log_changed(cls, _id: str, old: Person, new: Person) -> DictAny:
        old_dict = old.model_dump()
        new_dict = new.model_dump()
        _old: str
        _new: str

        diff: DictAny = dict()
        for key in old_dict:
            if key in ("data_criacao", "data_atualizacao"):
                continue
            _old = old_dict[key]
            _new = new_dict[key]
            if _old != _new:
                diff[key] = _new
                logger.debug(f"{key}: {old} -> {new}.")

                log = PersonsChangeLog(
                    person_id=_id,
                    date_changed=datetime.now(),
                    row_changed=key,
                    old_value=_old,
                    new_value=_new,
                )
                log_dict = log.model_dump()
                insrted: InsertOne = await persons_changelog.insert_one(log_dict)
        return diff

    @classmethod
    async def edit_person(cls, _id: str, new_data: DictAny) -> Person:
        new_record = Person(**new_data)
        result = await persons.find_one({"_id": ObjectId(_id)})

        old_record = Person(**result)
        diff = await cls.audit_log_changed(_id, old_record, new_record)
        if not diff:
            logger.info(f"No changes in the document '{_id}'.")
            old_record.id = _id
            return old_record

        diff["data_atualizacao"] = new_record.model_dump()["data_atualizacao"]
        updated = await persons.update_one(
            filter={"_id": ObjectId(_id)},
            update={"$set": diff}
        )
        result = await persons.find_one({"_id": ObjectId(_id)})
        valid_rec = Person(**result)
        valid_rec.id = _id
        return valid_rec

    @classmethod
    async def create_one_person(cls, new_data: DictAny) -> Person:
        valid_rec = Person(**new_data)
        result = await persons.insert_one(valid_rec.model_dump())
        db_rec = await persons.find_one({"_id": ObjectId(result.inserted_id)})
        valid_rec = Person(**db_rec)
        valid_rec.id = result.inserted_id
        return valid_rec

    @classmethod
    async def get_all_persons(cls, n: int | None = None, filter: DictAny | None = None) -> list[Person]:
        persons_cursor = persons.find(filter)
        persons_list = await persons_cursor.to_list(n)
        valid_rec_list = []
        for vals in persons_list:
            valid_rec = Person(**vals)
            valid_rec.id = str(vals["_id"])
            valid_rec_list.append(valid_rec)

        return valid_rec_list

    @classmethod
    async def get_changelog(cls, _id: str | None = None) -> list[PersonsChangeLog]:
        if _id:
            auditlogs = persons_changelog.find({"person_id": _id})
        else:
            auditlogs = persons_changelog.find()

        logs_list = [PersonsChangeLog(**log) async for log in auditlogs]
        return logs_list

    @classmethod
    async def export_persons_as_csv(cls) -> BytesIO:
        record_list = await Database.get_all_persons()
        dict_record_list = [rec.model_dump(
            exclude={"id"}) for rec in record_list]

        df = pd.DataFrame(dict_record_list)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output
