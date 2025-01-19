from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from core.database import SessionDep
from models import Client, ClientCreate, Mortage, MortageCreate
from sqlmodel import select

clients_router = APIRouter()

@clients_router.get("/clients/{client_id}")
def read_client(client_id: int, session: SessionDep):
    client = session.exec(select(Client).where(Client.id == client_id)).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client

@clients_router.post("/clients")
def create_client(client_data: ClientCreate, session: SessionDep):
    client = Client(name=client_data.name, dni=client_data.dni, requested_capital=client_data.requested_capital)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@clients_router.put("/clients/{client_id}")
def update_client(client_id: int, client_data: ClientCreate, session: SessionDep):
    client = session.exec(select(Client).where(Client.id == client_id)).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.name = client_data.name
    client.dni = client_data.dni
    client.requested_capital = client_data.requested_capital

    session.commit()
    session.refresh(client)

    return client

@clients_router.delete("/clients/{client_id}")
def delete_client(client_id: int, session: SessionDep):
    client = session.exec(select(Client).where(Client.id == client_id)).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    session.delete(client)
    session.commit()

    return {"message": "Client deleted successfully"}

@clients_router.get("/clients/")
def read_clients(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Client]:
    clients = session.exec(select(Client).offset(offset).limit(limit)).all()

    if not clients:
        return Response(status_code=204)
    
    return clients

@clients_router.post("/{client_id}/simulate-mortgage")
def simulate_mortgage(client_id: int, mortage_data: MortageCreate, session: SessionDep):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    capital = client.requested_capital
    tae = mortage_data.tae
    installments = mortage_data.installments

    i = tae / 100 / 12
    n = installments * 12

    
    if i == 0:
        payment = capital / n
    else:
        payment = capital * i / (1 - pow(1 + i, -n))

    total = payment * n

    mortage = Mortage(
        tae=tae,
        installments=n,
        monthly_payment= round(payment, 2),
        total=round(total,2),
        client_id=client.id,
    )

    session.add(mortage)
    session.commit()
    session.refresh(mortage)

    return mortage