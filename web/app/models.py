
from datetime import datetime
from pydantic import BaseModel


class Person(BaseModel):
    nome: str
    data_nascimento: datetime
    genero: str
    nacionalidade: str
    data_criacao: datetime
    data_atualizacao: datetime
    id: str | None = None


class PersonsChangeLog(BaseModel):
    """Implementação de um histórico de alterações da tabela,
    registrando as modificações feitas."""
    person_id: str
    date_changed: datetime
    row_changed: str
    old_value: str
    new_value: str
