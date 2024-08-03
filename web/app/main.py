import logging
from fastapi import FastAPI

from app.routers import persons


log_format = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
)
logging.basicConfig(format=log_format, level=logging.INFO)

app = FastAPI()

app.include_router(persons.router, prefix="/persons", tags=["persons"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}
