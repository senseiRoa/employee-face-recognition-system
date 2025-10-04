from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from models import Tablet
from schemas import TabletCreate, TabletUpdate


def create_tablet(db: Session, tablet: TabletCreate) -> Tablet:
    db_tablet = Tablet(**tablet.dict())
    db.add(db_tablet)
    db.commit()
    db.refresh(db_tablet)
    return db_tablet


def get_tablet(db: Session, tablet_id: int) -> Optional[Tablet]:
    return db.query(Tablet).filter(Tablet.id == tablet_id).first()


def get_tablets(db: Session, warehouse_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Tablet]:
    query = db.query(Tablet)
    if warehouse_id:
        query = query.filter(Tablet.warehouse_id == warehouse_id)
    return query.offset(skip).limit(limit).all()


def update_tablet(db: Session, tablet_id: int, tablet_update: TabletUpdate) -> Optional[Tablet]:
    db_tablet = get_tablet(db, tablet_id)
    if not db_tablet:
        return None
    
    update_data = tablet_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tablet, key, value)
    
    db.commit()
    db.refresh(db_tablet)
    return db_tablet


def update_tablet_sync(db: Session, tablet_id: int) -> Optional[Tablet]:
    db_tablet = get_tablet(db, tablet_id)
    if not db_tablet:
        return None
    
    db_tablet.last_sync = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_tablet)
    return db_tablet


def delete_tablet(db: Session, tablet_id: int) -> bool:
    db_tablet = get_tablet(db, tablet_id)
    if not db_tablet:
        return False
    
    db.delete(db_tablet)
    db.commit()
    return True
