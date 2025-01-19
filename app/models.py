import re
from pydantic import BaseModel, field_validator
from sqlmodel import Field, Relationship, SQLModel


class ClientCreate(BaseModel):
    name: str = Field(max_length=100, nullable=False)
    dni: str = Field(max_length=9, min_length=9, nullable=False)
    requested_capital: int = Field(gt=0, nullable=False)

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, value):
        value = value.strip().upper()

        if not re.fullmatch(r"\d{8}[A-Z]", value):
            raise ValueError("DNI must include 8 digits followed by 1 uppercase letter")
        
        dgts = int(value[:-1])
        letter = value[-1]

        dni_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        if letter != dni_letters[dgts % 23]:
            raise ValueError("DNI letter is incorrect")
        
        return value

class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    dni: str = Field(max_length=9, min_length=9, nullable=False, unique=True)
    requested_capital: int = Field(gt=0, nullable=False)
    mortages: list["Mortgage"] = Relationship(back_populates="client", cascade_delete=True)

class MortgageCreate(BaseModel):
    tae: float = Field(gt=0, nullable=False)
    installments: int = Field(gt=0, nullable=False)

class Mortgage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tae: float = Field(gt=0, nullable=False)
    installments: int = Field(gt=0, nullable=False)
    monthly_payment: float = Field(gt=0, nullable=False)
    total: float = Field(gt=0, nullable=False)
    client_id: int = Field(foreign_key="client.id", nullable=False, ondelete="CASCADE")
    client: Client = Relationship(back_populates="mortgages")