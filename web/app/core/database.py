from datetime import datetime
from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import InsertManyResult

from app.core.config import settings
from app.models import Person


mongo_uri = "mongodb://{user}:{password}@mongodb:27017".format
MONGO_URI: str = mongo_uri(
    user=settings.MONGO_INITDB_ROOT_USERNAME,
    password=settings.MONGO_INITDB_ROOT_PASSWORD
)
client = AsyncIOMotorClient(MONGO_URI)
database = client.get_database("zoox")
persons = database.get_collection("persons")


class Database:
    @classmethod
    async def create_persons(cls, persons_list: list[dict[str, Any]]) -> InsertManyResult | None:
        to_insert = []
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
                # _ = await persons.insert_one(dump_rec)
        if to_insert:
            inserted = await persons.insert_many(to_insert)
            return inserted
        return None

    @classmethod
    async def get_person(cls, _id: str) -> Person:
        try:
            result: dict[str, Any] = await persons.find_one({"_id": ObjectId(_id)})
            valid_record = Person(**result)
            valid_record.id = result['_id']
            return valid_record
        except InvalidId as e:
            return None
