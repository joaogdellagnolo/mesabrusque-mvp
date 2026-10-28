import uuid
from datetime import date, time
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from database import engine, get_db, SessionLocal
from models import Base, Restaurante, Mesa, Usuario, Reserva, StatusReserva

# Cria as tabelas automaticamente e popula dados iniciais de Brusque caso o banco esteja vazio
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MesaBrusque API",
    description="API de descoberta de restaurantes, cupons de horários ociosos e reservas em Brusque/SC",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# SEED INICIAL (Restaurantes de Brusque/SC)
# ==========================================
def seed_initial_data():
    db = SessionLocal()
    try:
        if db.scalars(select(Restaurante)).first() is not None:
            return

        restaurantes_seed = [
            Restaurante(
                nome="Haus Bier & Gastronomia Alemã",
                categoria="Alemão",
                endereco="Av. Cônsul Carlos Renaux, 412",
                bairro="Centro I",
                latitude=-27.0978,
                longitude=-48.9168,
                cupom_destaque="20% OFF no jantar até 19h30",
                desconto_percentual=20,
                avaliacao=4.9,
                imagem_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
                mesas=[
                    Mesa(identificador="Mesa 01 (Salão)", capacidade=2),
                    Mesa(identificador="Mesa 02 (Salão)", capacidade=4),
                    Mesa(identificador="Mesa 03 (Biergarten)", capacidade=6),
                    Mesa(identificador="Mesa 04 (Biergarten)", capacidade=8),
                ]
            ),
            Restaurante(
                nome="Trattoria Nonna Fenarreco",
                categoria="Italiano",
                endereco="Rua Hercílio Luz, 210",
                bairro="São Luiz",
                latitude=-27.1025,
                longitude=-48.9210,
                cupom_destaque="15% OFF + Sobremesa Grátis",
                desconto_percentual=15,
                avaliacao=4.8,
                imagem_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
                mesas=[
                    Mesa(identificador="Mesa 01 (Romântica)", capacidade=2),
                    Mesa(identificador="Mesa 02 (Família)", capacidade=4),
                    Mesa(identificador="Mesa 03 (Varanda)", capacidade=6),
                ]
            ),
            Restaurante(
                nome="Brusque Burger & Craft Beer",
                categoria="Hamburgueria",
                endereco="Av. Beira Rio, 890",
                bairro="Santa Rita",
                latitude=-27.0942,
                longitude=-48.9125,
                cupom_destaque="25% OFF terças e quartas",
                desconto_percentual=25,
                avaliacao=4.7,
                imagem_url="https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
                mesas=[
                    Mesa(identificador="Booth 01", capacidade=2),
                    Mesa(identificador="Booth 02", capacidade=4),
                    Mesa(identificador="Deck Beira Rio", capacidade=6),
                ]
            ),
            Restaurante(
                nome="Kori Sushi Lounge",
                categoria="Japonês",
                endereco="Rua Moritz Germano Hoffmann, 105",
                bairro="Centro II",
                latitude=-27.0995,
                longitude=-48.9102,
                cupom_destaque="10% OFF no Rodízio Premium",
                desconto_percentual=10,
                avaliacao=4.9,
                imagem_url="https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
                mesas=[
                    Mesa(identificador="Tatame 01", capacidade=2),
                    Mesa(identificador="Tatame 02", capacidade=4),
                    Mesa(identificador="Lounge 03", capacidade=6),
                ]
            ),
        ]

        db.add_all(restaurantes_seed)
        db.commit()
    finally:
        db.close()


seed_initial_data()


# ==========================================
# SCHEMAS (Pydantic)
# ==========================================

class RestauranteOut(BaseModel):
    id: int
    nome: str
    categoria: str
    endereco: str
    bairro: str
    latitude: float
    longitude: float
    cupom_destaque: Optional[str]
    desconto_percentual: int
    avaliacao: float
    imagem_url: Optional[str]
    total_mesas: int = 0

    class Config:
        from_attributes = True


class ReservaCreate(BaseModel):
    restaurante_id: int
    data_reserva: date
    horario_reserva: time
    qtd_pessoas: int = Field(..., gt=0, le=20, description="Quantidade de pessoas na mesa")
    nome_usuario: str = Field(..., min_length=2)
    email_usuario: EmailStr
    telefone_usuario: str


class ReservaOut(BaseModel):
    id: int
    codigo_confirmacao: str
    restaurante_nome: str
    mesa_identificador: str
    data_reserva: date
    horario_reserva: time
    qtd_pessoas: int
    cupom_aplicado: Optional[str]
    status: StatusReserva


# ==========================================
# ROTAS DA API
# ==========================================

@app.get("/restaurantes", response_model=List[RestauranteOut])
def listar_restaurantes(
    categoria: Optional[str] = Query(None, description="Filtrar por culinária"),
    apenas_com_cupom: bool = Query(False, description="Filtrar apenas restaurantes com desconto ativo"),
    db: Session = Depends(get_db)
):
    query = select(Restaurante).where(Restaurante.ativo == True)

    if categoria and categoria != "Todos":
        query = query.where(Restaurante.categoria.ilike(f"%{categoria}%"))
    if apenas_com_cupom:
        query = query.where(Restaurante.desconto_percentual > 0)

    restaurantes = db.scalars(query).all()

    resultado = []
    for r in restaurantes:
        rest_dict = RestauranteOut.model_validate(r)
        rest_dict.total_mesas = len([m for m in r.mesas if m.ativa])
        resultado.append(rest_dict)

    return resultado


@app.post("/reservas", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def criar_reserva(payload: ReservaCreate, db: Session = Depends(get_db)):
    restaurante = db.get(Restaurante, payload.restaurante_id)
    if not restaurante or not restaurante.ativo:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado ou inativo.")

    mesas_ocupadas_subq = (
        select(Reserva.mesa_id)
        .where(
            and_(
                Reserva.restaurante_id == payload.restaurante_id,
                Reserva.data_reserva == payload.data_reserva,
                Reserva.horario_reserva == payload.horario_reserva,
                Reserva.status.in_([StatusReserva.PENDENTE, StatusReserva.CONFIRMADA])
            )
        )
    )

    mesa_disponivel = db.scalars(
        select(Mesa)
        .where(
            and_(
                Mesa.restaurante_id == payload.restaurante_id,
                Mesa.ativa == True,
                Mesa.capacidade >= payload.qtd_pessoas,
                Mesa.id.not_in(mesas_ocupadas_subq)
            )
        )
        .order_by(Mesa.capacidade.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    ).first()

    if not mesa_disponivel:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não há mesas disponíveis para essa quantidade de pessoas neste horário."
        )

    usuario = db.scalars(select(Usuario).where(Usuario.email == payload.email_usuario)).first()
    if not usuario:
        usuario = Usuario(
            nome=payload.nome_usuario,
            email=payload.email_usuario,
            telefone=payload.telefone_usuario
        )
        db.add(usuario)
        db.flush()

    codigo = f"BRQ-{uuid.uuid4().hex[:6].upper()}"

    nova_reserva = Reserva(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        mesa_id=mesa_disponivel.id,
        data_reserva=payload.data_reserva,
        horario_reserva=payload.horario_reserva,
        qtd_pessoas=payload.qtd_pessoas,
        cupom_aplicado=restaurante.cupom_destaque,
        codigo_confirmacao=codigo,
        status=StatusReserva.CONFIRMADA
    )

    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)

    return ReservaOut(
        id=nova_reserva.id,
        codigo_confirmacao=nova_reserva.codigo_confirmacao,
        restaurante_nome=restaurante.nome,
        mesa_identificador=mesa_disponivel.identificador,
        data_reserva=nova_reserva.data_reserva,
        horario_reserva=nova_reserva.horario_reserva,
        qtd_pessoas=nova_reserva.qtd_pessoas,
        cupom_aplicado=nova_reserva.cupom_aplicado,
        status=nova_reserva.status
    )

