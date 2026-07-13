"""Modelos SQLAlchemy compatibles con Python 3.14 y SQL Server."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MovementType(str, Enum):
    ENTRADA = "ENTRADA"
    VENTA = "VENTA"
    AJUSTE = "AJUSTE"


class Product(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), unique=True, nullable=False)
    categoria = Column(String(60), nullable=False)
    descripcion = Column(Text, nullable=True)
    stock_minimo = Column(Integer, default=2, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    variantes = relationship("Variant", back_populates="producto", cascade="all, delete-orphan")


class Variant(Base):
    __tablename__ = "variantes"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    talla = Column(String(20), nullable=False)
    color = Column(String(40), nullable=False)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    producto = relationship("Product", back_populates="variantes")
    movimientos = relationship("InventoryMovement", back_populates="variante", cascade="all, delete-orphan")


class InventoryMovement(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True)
    variante_id = Column(Integer, ForeignKey("variantes.id"), nullable=False, index=True)
    tipo = Column(SqlEnum(MovementType), nullable=False)
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(180), nullable=False)
    referencia = Column(String(80), nullable=True)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    variante = relationship("Variant", back_populates="movimientos")
