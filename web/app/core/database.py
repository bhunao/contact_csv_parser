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
        result: dict[str, Any] = await persons.find_one({"_id": ObjectId(_id)})
        valid_record = Person(**result)
        valid_record.id = result['_id']
        return valid_record

    @classmethod
    async def edit_person(cls, _id: str, new_data: dict[str, Any]) -> Person:
        new_rec = Person(**new_data)
        result = await persons.find_one({"_id": ObjectId(_id)})

        # TODO: add audit log
        print("====================================")
        print(new_data)
        print(result)

        old = new_rec.model_dump()
        old = result.copy()
        del old["_id"]
        old_items = list(old.items())
        new_items = list(new_data.items())

        changed = dict()
        for k, v in old_items:
            _old = old.get(k)
            _new = new_data.get(k)
            if old.get(k) != new_data.get(k):
                changed[k] = _old, _new
                print(_old, _new)

        print(old_items)
        print(new_items)
        print("----------")
        print(changed)

        print("====================================")
        updated_values = new_rec.model_dump(
            exclude={"data_criacao"})
        updated = await persons.update_one(
            filter={"_id": ObjectId(_id)},
            update={"$set": updated_values}
        )
        result = await persons.find_one({"_id": ObjectId(_id)})
        valid_rec = Person(**result)
        valid_rec.id = _id
        return valid_rec

    @ classmethod
    async def create_one_person(cls, new_data: dict[str, Any]) -> Person:
        valid_rec = Person(**new_data)
        result = await persons.insert_one(valid_rec.model_dump())
        db_rec = await persons.find_one({"_id": ObjectId(result.inserted_id)})
        valid_rec = Person(**db_rec)
        valid_rec.id = result.inserted_id
        return valid_rec

    @ classmethod
    async def get_all_persons(cls, n: int | None = None) -> list[Person]:
        persons_cursor = persons.find()
        persons_list = await persons_cursor.to_list(n)
        valid_rec_list = []
        for vals in persons_list:
            valid_rec = Person(**vals)
            valid_rec.id = str(vals["_id"])
            valid_rec_list.append(valid_rec)

        return valid_rec_list
