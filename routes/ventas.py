from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlmodel import Session
from datetime import datetime

from database import get_session
from repository import VentaRepository, AutoRepository
from models import (
    VentaCreate,
    VentaResponse,
    VentaUpdate,
    VentaResponseWithAuto
)




router = APIRouter(prefix="/ventas", tags=["ventas"])


# ----------------- CREATE -----------------
@router.post("/", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
def create_venta(venta_in: VentaCreate, session: Session = Depends(get_session)):
    auto_repo = AutoRepository(session)

    # validar existencia del auto
    if not auto_repo.get_by_id(venta_in.auto_id):
        raise HTTPException(400, "El auto indicado no existe")

    repo = VentaRepository(session)

    try:
        return repo.create(venta_in)
    except Exception as e:
        raise HTTPException(400, detail=str(e))


# ----------------- LIST -----------------
@router.get("/", response_model=List[VentaResponse])
def list_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session)
):
    repo = VentaRepository(session)

    if min_price is not None or max_price is not None:
        return repo.filter_by_price_range(min_price, max_price, skip=skip, limit=limit)

    if start_date or end_date:
        return repo.filter_by_date_range(start_date, end_date, skip=skip, limit=limit)

    return repo.get_all(skip=skip, limit=limit)


# ----------------- ENDPOINTS ESPECÍFICOS (antes de {id}) -----------------

@router.get("/auto/{auto_id}", response_model=List[VentaResponse])
def ventas_por_auto(auto_id: int, session: Session = Depends(get_session)):
    repo = VentaRepository(session)
    return repo.get_by_auto_id(auto_id)


@router.get("/comprador/{nombre}", response_model=List[VentaResponse])
def ventas_por_comprador(nombre: str, session: Session = Depends(get_session)):
    repo = VentaRepository(session)
    return repo.get_by_comprador(nombre)


# ----------------- GET BY ID -----------------
@router.get("/{venta_id}", response_model=VentaResponse)
def get_venta(venta_id: int, session: Session = Depends(get_session)):
    repo = VentaRepository(session)
    venta = repo.get_by_id(venta_id)
    if not venta:
        raise HTTPException(404, "Venta no encontrada")
    return venta


# ----------------- UPDATE -----------------
@router.put("/{venta_id}", response_model=VentaResponse)
def update_venta(venta_id: int, venta_up: VentaUpdate, session: Session = Depends(get_session)):
    repo = VentaRepository(session)

    # si se cambia auto_id → validar existencia
    if venta_up.auto_id:
        auto_repo = AutoRepository(session)
        if not auto_repo.get_by_id(venta_up.auto_id):
            raise HTTPException(400, "El auto indicado no existe")

    venta = repo.update(venta_id, venta_up)

    if not venta:
        raise HTTPException(404, "Venta no encontrada")

    return venta


# ----------------- DELETE -----------------
@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(venta_id: int, session: Session = Depends(get_session)):
    repo = VentaRepository(session)
    ok = repo.delete(venta_id)

    if not ok:
        raise HTTPException(404, "Venta no encontrada")

    return


# ----------------- GET WITH AUTO -----------------
@router.get("/{venta_id}/with-auto", response_model=VentaResponseWithAuto)
def venta_with_auto(venta_id: int, session: Session = Depends(get_session)):
    repo = VentaRepository(session)
    venta = repo.get_by_id(venta_id)

    if not venta:
        raise HTTPException(404, "Venta no encontrada")

    # Lazy load del auto (SQLModel)
    _ = venta.auto

    return venta
