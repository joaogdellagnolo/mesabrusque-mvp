from datetime import datetime, date, time
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import (
    Integer, String, Float, Boolean, Date, Time, DateTime,
    ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class StatusReserva(str, PyEnum):
    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    CONCLUIDA = "CONCLUIDA"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reservas: Mapped[List["Reserva"]] = relationship(back_populates="usuario")


class Restaurante(Base):
    __tablename__ = "restaurantes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False)
    endereco: Mapped[str] = mapped_column(String(200), nullable=False)
    bairro: Mapped[str] = mapped_column(String(80), nullable=False)
    cidade: Mapped[str] = mapped_column(String(80), default="Brusque")
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    cupom_destaque: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    desconto_percentual: Mapped[int] = mapped_column(Integer, default=0)
    avaliacao: Mapped[float] = mapped_column(Float, default=5.0)
    imagem_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    mesas: Mapped[List["Mesa"]] = relationship(back_populates="restaurante", cascade="all, delete-orphan")
    reservas: Mapped[List["Reserva"]] = relationship(back_populates="restaurante")


class Mesa(Base):
    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.id", ondelete="CASCADE"), nullable=False)
    identificador: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    restaurante: Mapped["Restaurante"] = relationship(back_populates="mesas")
    reservas: Mapped[List["Reserva"]] = relationship(back_populates="mesa")

    __table_args__ = (
        UniqueConstraint("restaurante_id", "identificador", name="uq_mesa_por_restaurante"),
    )


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.id"), nullable=False)
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), nullable=False)

    data_reserva: Mapped[date] = mapped_column(Date, nullable=False)
    horario_reserva: Mapped[time] = mapped_column(Time, nullable=False)
    qtd_pessoas: Mapped[int] = mapped_column(Integer, nullable=False)

    cupom_aplicado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    codigo_confirmacao: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False)
    status: Mapped[StatusReserva] = mapped_column(
        Enum(StatusReserva), default=StatusReserva.CONFIRMADA, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario: Mapped["Usuario"] = relationship(back_populates="reservas")
    restaurante: Mapped["Restaurante"] = relationship(back_populates="reservas")
    mesa: Mapped["Mesa"] = relationship(back_populates="reservas")

    __table_args__ = (
        Index("idx_reserva_disponibilidade", "restaurante_id", "data_reserva", "horario_reserva", "status"),
    )

