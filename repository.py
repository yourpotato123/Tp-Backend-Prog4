from typing import Optional, List
from sqlmodel import Session, select
from models import Auto, AutoCreate, AutoUpdate, Venta, VentaCreate, VentaUpdate
from sqlalchemy.exc import IntegrityError




# ---------- AutoRepository ----------
class AutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, auto_in: AutoCreate) -> Auto:
        auto = Auto.from_orm(auto_in)
        self.session.add(auto)
        try:
            self.session.commit()
            self.session.refresh(auto)
            return auto
        except IntegrityError as e:
            self.session.rollback()
            raise

    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        return self.session.get(Auto, auto_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Auto]:
        q = select(Auto).offset(skip).limit(limit)
        return self.session.exec(q).all()

    def update(self, auto_id: int, auto_update: AutoUpdate) -> Optional[Auto]:
        auto = self.get_by_id(auto_id)
        if not auto:
            return None
        update_data = auto_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(auto, k, v)
        try:
            self.session.add(auto)
            self.session.commit()
            self.session.refresh(auto)
            return auto
        except IntegrityError:
            self.session.rollback()
            raise

    def delete(self, auto_id: int) -> bool:
        auto = self.get_by_id(auto_id)
        if not auto:
            return False
        self.session.delete(auto)
        self.session.commit()
        return True

    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        q = select(Auto).where(Auto.numero_chasis == numero_chasis)
        return self.session.exec(q).first()

    def search(self, marca: Optional[str] = None, modelo: Optional[str] = None, skip: int = 0, limit: int = 100):
        q = select(Auto)
        if marca:
            q = q.where(Auto.marca.ilike(f"%{marca}%"))
        if modelo:
            q = q.where(Auto.modelo.ilike(f"%{modelo}%"))
        q = q.offset(skip).limit(limit)
        return self.session.exec(q).all()

# ---------- VentaRepository ----------
class VentaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, venta_in: VentaCreate) -> Venta:
        venta = Venta.from_orm(venta_in)
        self.session.add(venta)
        self.session.commit()
        self.session.refresh(venta)
        return venta

    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        return self.session.get(Venta, venta_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Venta]:
        q = select(Venta).offset(skip).limit(limit)
        return self.session.exec(q).all()

    def update(self, venta_id: int, venta_update: VentaUpdate) -> Optional[Venta]:
        venta = self.get_by_id(venta_id)
        if not venta:
            return None
        update_data = venta_update.dict(exclude_unset=True)
        for k, v in update_data.items():
            setattr(venta, k, v)
        self.session.add(venta)
        self.session.commit()
        self.session.refresh(venta)
        return venta

    def delete(self, venta_id: int) -> bool:
        venta = self.get_by_id(venta_id)
        if not venta:
            return False
        self.session.delete(venta)
        self.session.commit()
        return True

    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        q = select(Venta).where(Venta.auto_id == auto_id)
        return self.session.exec(q).all()

    def get_by_comprador(self, nombre: str) -> List[Venta]:
        q = select(Venta).where(Venta.nombre_comprador.ilike(f"%{nombre}%"))
        return self.session.exec(q).all()

    def filter_by_date_range(self, start_date=None, end_date=None, skip=0, limit=100):
        q = select(Venta)
        if start_date:
            q = q.where(Venta.fecha_venta >= start_date)
        if end_date:
            q = q.where(Venta.fecha_venta <= end_date)
        q = q.offset(skip).limit(limit)
        return self.session.exec(q).all()

    def filter_by_price_range(self, min_price=None, max_price=None, skip=0, limit=100):
        q = select(Venta)
        if min_price is not None:
            q = q.where(Venta.precio >= min_price)
        if max_price is not None:
            q = q.where(Venta.precio <= max_price)
        q = q.offset(skip).limit(limit)
        return self.session.exec(q).all()