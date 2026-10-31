from pydantic import BaseModel, Field


class Card(BaseModel):
    id: str
    title: str
    details: str = ""


class Column(BaseModel):
    id: str
    title: str
    cardIds: list[str] = Field(default_factory=list)


class BoardData(BaseModel):
    columns: list[Column]
    cards: dict[str, Card]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    status: str = "ok"

