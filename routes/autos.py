from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlmodel import Session
from database import get_session
from repository import AutoRepository
from models import AutoCreate, AutoResponse, AutoResponseWithVentas, AutoUpdate, Auto

router = APIRouter(prefix="/autos", tags=["autos"])


# ----------------- CREATE -----------------
@router.post("/", response_model=AutoResponse, status_code=status.HTTP_201_CREATED)
def create_auto(auto_in: AutoCreate, session: Session = Depends(get_session)):
    repo = AutoRepository(session)

    # verificar unicidad del chasis
    if repo.get_by_chasis(auto_in.numero_chasis):
        raise HTTPException(status_code=400, detail="numero_chasis ya existe")

    try:
        auto = repo.create(auto_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return auto


# ----------------- LIST -----------------
@router.get("/", response_model=List[AutoResponse])
def list_autos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    marca: Optional[str] = None,
    modelo: Optional[str] = None,
    session: Session = Depends(get_session),
):
    repo = AutoRepository(session)

    if marca or modelo:
        return repo.search(marca=marca, modelo=modelo, skip=skip, limit=limit)

    return repo.get_all(skip=skip, limit=limit)


# ----------------- GET BY CHASIS (colocar ANTES que {id}) -----------------
@router.get("/chasis/{numero_chasis}", response_model=AutoResponse)
def get_by_chasis(numero_chasis: str, session: Session = Depends(get_session)):
    repo = AutoRepository(session)
    auto = repo.get_by_chasis(numero_chasis)
    if not auto:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    return auto


# ----------------- GET BY ID -----------------
@router.get("/{auto_id}", response_model=AutoResponse)
def get_auto(auto_id: int, session: Session = Depends(get_session)):
    repo = AutoRepository(session)
    auto = repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    return auto


# ----------------- UPDATE -----------------
@router.put("/{auto_id}", response_model=AutoResponse)
def update_auto(auto_id: int, auto_up: AutoUpdate, session: Session = Depends(get_session)):
    repo = AutoRepository(session)

    # si intenta cambiar chasis, chequear unicidad
    if auto_up.numero_chasis:
        existing = repo.get_by_chasis(auto_up.numero_chasis)
        if existing and existing.id != auto_id:
            raise HTTPException(status_code=400, detail="numero_chasis ya existe")

    try:
        auto = repo.update(auto_id, auto_up)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not auto:
        raise HTTPException(status_code=404, detail="Auto no encontrado")

    return auto


# ----------------- DELETE -----------------
@router.delete("/{auto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auto(auto_id: int, session: Session = Depends(get_session)):
    repo = AutoRepository(session)

    auto = repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=404, detail="Auto no encontrado")

    # prevenir borrar autos con ventas
    if auto.ventas:
        raise HTTPException(status_code=400, detail="No se puede borrar un auto con ventas registradas")

    repo.delete(auto_id)
    return


# ----------------- GET AUTO WITH VENTAS -----------------
@router.get("/{auto_id}/with-ventas", response_model=AutoResponseWithVentas)
def get_auto_with_ventas(auto_id: int, session: Session = Depends(get_session)):
    repo = AutoRepository(session)
    auto = repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=404, detail="Auto no encontrado")

    # forzar carga de ventas (lazy load)
    _ = auto.ventas

    return auto
