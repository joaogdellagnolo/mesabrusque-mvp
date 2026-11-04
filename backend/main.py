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
    version="0.2.0"
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
# REGRAS DE HORÁRIOS E CUPONS OCIOSOS
# ==========================================
HORARIO_LIMITE_OCIOSO = time(19, 30)

HORARIOS_PADRAO = [
    {"hora": time(18, 30), "label": "18:30", "ocioso": True, "bonus": "Horário VIP (+Desconto Garantido)"},
    {"hora": time(19, 0),  "label": "19:00", "ocioso": True, "bonus": "Horário VIP (+Desconto Garantido)"},
    {"hora": time(19, 30), "label": "19:30", "ocioso": True, "bonus": "Último horário com cupom máximo"},
    {"hora": time(20, 0),  "label": "20:00", "ocioso": False, "bonus": "Alta procura (Sem cupom ocioso)"},
    {"hora": time(20, 30), "label": "20:30", "ocioso": False, "bonus": "Alta procura (Sem cupom ocioso)"},
    {"hora": time(21, 0),  "label": "21:00", "ocioso": False, "bonus": "Horário normal"},
]


# ==========================================
# SCHEMAS (Pydantic)
# ==========================================

class MesaOut(BaseModel):
    id: int
    identificador: str
    capacidade: int
    ativa: bool

    class Config:
        from_attributes = True


class MesaCreate(BaseModel):
    identificador: str = Field(..., min_length=2, max_length=20)
    capacidade: int = Field(..., gt=0, le=20)


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


class CupomUpdate(BaseModel):
    cupom_destaque: Optional[str] = Field(None, max_length=100)
    desconto_percentual: int = Field(0, ge=0, le=80)


class SlotDisponibilidadeOut(BaseModel):
    hora: str
    ocioso: bool
    bonus: str
    disponivel: bool
    mesas_livres: int
    desconto_aplicavel: int
    cupom_aplicavel: Optional[str]


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
    restaurante_id: int
    restaurante_nome: str
    restaurante_endereco: str
    restaurante_bairro: str
    mesa_identificador: str
    data_reserva: date
    horario_reserva: time
    qtd_pessoas: int
    cupom_aplicado: Optional[str]
    status: StatusReserva
    nome_usuario: str
    email_usuario: str
    telefone_usuario: str


def montar_reserva_out(reserva: Reserva) -> ReservaOut:
    return ReservaOut(
        id=reserva.id,
        codigo_confirmacao=reserva.codigo_confirmacao,
        restaurante_id=reserva.restaurante.id,
        restaurante_nome=reserva.restaurante.nome,
        restaurante_endereco=reserva.restaurante.endereco,
        restaurante_bairro=reserva.restaurante.bairro,
        mesa_identificador=reserva.mesa.identificador,
        data_reserva=reserva.data_reserva,
        horario_reserva=reserva.horario_reserva,
        qtd_pessoas=reserva.qtd_pessoas,
        cupom_aplicado=reserva.cupom_aplicado,
        status=reserva.status,
        nome_usuario=reserva.usuario.nome,
        email_usuario=reserva.usuario.email,
        telefone_usuario=reserva.usuario.telefone,
    )


# ==========================================
# ROTAS DA API — CLIENTE & DESCOBERTA
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


@app.get("/restaurantes/{restaurante_id}/disponibilidade", response_model=List[SlotDisponibilidadeOut])
def consultar_disponibilidade(
    restaurante_id: int,
    data_reserva: date = Query(..., description="Data desejada para a reserva"),
    qtd_pessoas: int = Query(2, gt=0, le=20, description="Quantidade de pessoas"),
    db: Session = Depends(get_db)
):
    restaurante = db.get(Restaurante, restaurante_id)
    if not restaurante or not restaurante.ativo:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado ou inativo.")

    mesas_compativeis = db.scalars(
        select(Mesa).where(
            and_(
                Mesa.restaurante_id == restaurante_id,
                Mesa.ativa == True,
                Mesa.capacidade >= qtd_pessoas
            )
        )
    ).all()
    ids_mesas_compativeis = {m.id for m in mesas_compativeis}

    reservas_ativas_dia = db.scalars(
        select(Reserva).where(
            and_(
                Reserva.restaurante_id == restaurante_id,
                Reserva.data_reserva == data_reserva,
                Reserva.status.in_([StatusReserva.PENDENTE, StatusReserva.CONFIRMADA])
            )
        )
    ).all()

    slots = []
    for slot in HORARIOS_PADRAO:
        ocupadas_no_horario = {
            r.mesa_id for r in reservas_ativas_dia if r.horario_reserva == slot["hora"]
        }
        livres = len(ids_mesas_compativeis - ocupadas_no_horario)
        tem_cupom = slot["ocioso"] and restaurante.desconto_percentual > 0 and bool(restaurante.cupom_destaque)
        slots.append(
            SlotDisponibilidadeOut(
                hora=slot["label"],
                ocioso=slot["ocioso"],
                bonus=slot["bonus"],
                disponivel=livres > 0,
                mesas_livres=livres,
                desconto_aplicavel=restaurante.desconto_percentual if tem_cupom else 0,
                cupom_aplicavel=restaurante.cupom_destaque if tem_cupom else None,
            )
        )

    return slots


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
    else:
        usuario.nome = payload.nome_usuario
        usuario.telefone = payload.telefone_usuario
        db.flush()

    codigo = f"BRQ-{uuid.uuid4().hex[:6].upper()}"

    # Regra do MVP: Cupom só é aplicado se o horário reservado for ocioso (<= 19:30) e o restaurante tiver desconto ativo
    horario_eh_ocioso = payload.horario_reserva <= HORARIO_LIMITE_OCIOSO
    cupom_aplicado = (
        restaurante.cupom_destaque
        if (horario_eh_ocioso and restaurante.desconto_percentual > 0)
        else None
    )

    nova_reserva = Reserva(
        usuario_id=usuario.id,
        restaurante_id=restaurante.id,
        mesa_id=mesa_disponivel.id,
        data_reserva=payload.data_reserva,
        horario_reserva=payload.horario_reserva,
        qtd_pessoas=payload.qtd_pessoas,
        cupom_aplicado=cupom_aplicado,
        codigo_confirmacao=codigo,
        status=StatusReserva.CONFIRMADA
    )

    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)

    return montar_reserva_out(nova_reserva)


@app.get("/reservas", response_model=List[ReservaOut])
def consultar_reservas_cliente(
    email: Optional[str] = Query(None, description="Filtrar reservas pelo e-mail do cliente"),
    codigo: Optional[str] = Query(None, description="Filtrar pelo código do voucher BRQ-XXXXXX"),
    db: Session = Depends(get_db)
):
    query = select(Reserva).join(Usuario)
    if codigo:
        query = query.where(Reserva.codigo_confirmacao == codigo.strip().upper())
    elif email:
        query = query.where(Usuario.email.ilike(email.strip()))
    else:
        raise HTTPException(status_code=400, detail="Informe o e-mail ou o código do voucher para consultar.")

    reservas = db.scalars(query.order_by(Reserva.data_reserva.desc(), Reserva.horario_reserva.desc())).all()
    return [montar_reserva_out(r) for r in reservas]


@app.get("/reservas/{codigo}", response_model=ReservaOut)
def buscar_reserva_por_codigo(codigo: str, db: Session = Depends(get_db)):
    reserva = db.scalars(
        select(Reserva).where(Reserva.codigo_confirmacao == codigo.strip().upper())
    ).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Voucher não encontrado.")
    return montar_reserva_out(reserva)


@app.patch("/reservas/{codigo}/cancelar", response_model=ReservaOut)
def cancelar_reserva(codigo: str, db: Session = Depends(get_db)):
    reserva = db.scalars(
        select(Reserva).where(Reserva.codigo_confirmacao == codigo.strip().upper())
    ).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    if reserva.status == StatusReserva.CONCLUIDA:
        raise HTTPException(status_code=400, detail="Esta reserva já foi concluída (check-in realizado).")
    if reserva.status == StatusReserva.CANCELADA:
        raise HTTPException(status_code=400, detail="Esta reserva já está cancelada.")

    reserva.status = StatusReserva.CANCELADA
    db.commit()
    db.refresh(reserva)
    return montar_reserva_out(reserva)


# ==========================================
# ROTAS DA API — PAINEL DO RESTAURANTE
# ==========================================

@app.get("/restaurantes/{restaurante_id}/reservas", response_model=List[ReservaOut])
def listar_reservas_restaurante(
    restaurante_id: int,
    data_reserva: Optional[date] = Query(None, description="Data para filtrar a fila do dia"),
    db: Session = Depends(get_db)
):
    restaurante = db.get(Restaurante, restaurante_id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado.")

    query = select(Reserva).where(Reserva.restaurante_id == restaurante_id)
    if data_reserva:
        query = query.where(Reserva.data_reserva == data_reserva)

    reservas = db.scalars(query.order_by(Reserva.data_reserva.asc(), Reserva.horario_reserva.asc())).all()
    return [montar_reserva_out(r) for r in reservas]


@app.patch("/reservas/{codigo}/checkin", response_model=ReservaOut)
def realizar_checkin_voucher(codigo: str, db: Session = Depends(get_db)):
    reserva = db.scalars(
        select(Reserva).where(Reserva.codigo_confirmacao == codigo.strip().upper())
    ).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Código de voucher inválido ou não encontrado.")
    if reserva.status == StatusReserva.CANCELADA:
        raise HTTPException(status_code=400, detail="Este voucher foi cancelado e não pode ser utilizado.")
    if reserva.status == StatusReserva.CONCLUIDA:
        raise HTTPException(status_code=400, detail="Check-in já foi realizado anteriormente para este voucher.")

    reserva.status = StatusReserva.CONCLUIDA
    db.commit()
    db.refresh(reserva)
    return montar_reserva_out(reserva)


@app.patch("/restaurantes/{restaurante_id}/cupom", response_model=RestauranteOut)
def atualizar_cupom_restaurante(
    restaurante_id: int,
    payload: CupomUpdate,
    db: Session = Depends(get_db)
):
    restaurante = db.get(Restaurante, restaurante_id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado.")

    restaurante.desconto_percentual = payload.desconto_percentual
    restaurante.cupom_destaque = (
        payload.cupom_destaque.strip()
        if (payload.cupom_destaque and payload.desconto_percentual > 0)
        else None
    )
    db.commit()
    db.refresh(restaurante)

    rest_dict = RestauranteOut.model_validate(restaurante)
    rest_dict.total_mesas = len([m for m in restaurante.mesas if m.ativa])
    return rest_dict


@app.get("/restaurantes/{restaurante_id}/mesas", response_model=List[MesaOut])
def listar_mesas_restaurante(restaurante_id: int, db: Session = Depends(get_db)):
    restaurante = db.get(Restaurante, restaurante_id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado.")
    return restaurante.mesas


@app.post("/restaurantes/{restaurante_id}/mesas", response_model=MesaOut, status_code=status.HTTP_201_CREATED)
def adicionar_mesa_restaurante(
    restaurante_id: int,
    payload: MesaCreate,
    db: Session = Depends(get_db)
):
    restaurante = db.get(Restaurante, restaurante_id)
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado.")

    nova_mesa = Mesa(
        restaurante_id=restaurante_id,
        identificador=payload.identificador.strip(),
        capacidade=payload.capacidade,
        ativa=True
    )
    db.add(nova_mesa)
    try:
        db.commit()
        db.refresh(nova_mesa)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma mesa com esse identificador neste restaurante.")
    return nova_mesa


@app.patch("/mesas/{mesa_id}/toggle", response_model=MesaOut)
def alternar_status_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.get(Mesa, mesa_id)
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    mesa.ativa = not mesa.ativa
    db.commit()
    db.refresh(mesa)
    return mesa
