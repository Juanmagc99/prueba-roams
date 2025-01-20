from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from app.core.database import SessionDep
from app.models import Client, ClientCreate, Mortgage, MortgageCreate
from sqlmodel import select

clients_router = APIRouter()

@clients_router.get("/clients/{client_id}")
def read_client(client_id: int, session: SessionDep):
    client = session.exec(select(Client).where(Client.id == client_id)).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    mortgages = session.exec(select(Mortgage).where(Mortgage.client_id == client_id)).all()
    
    return {"client": client, "mortgages": mortgages}

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

@clients_router.post("/clients/{client_id}/simulate-mortgage")
def simulate_mortgage(client_id: int, mortgage_data: MortgageCreate, session: SessionDep):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    capital = client.requested_capital
    tae = mortgage_data.tae
    installments = mortgage_data.installments

    i = tae / 100 / 12
    n = installments * 12

    
    if i == 0:
        payment = capital / n
    else:
        payment = capital * i / (1 - pow(1 + i, -n))

    total = payment * n

    mortgage = Mortgage(
        tae=tae,
        installments=installments,
        monthly_payment= round(payment, 2),
        total=round(total,2),
        client_id=client.id,
    )

    session.add(mortgage)
    session.commit()
    session.refresh(mortgage)

    return mortgage