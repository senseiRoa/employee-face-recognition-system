from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import Tablet, TabletCreate, TabletUpdate
from services import tablet_service
from dependencies import get_current_user
from models import Company

router = APIRouter()


@router.post("/", response_model=Tablet, status_code=status.HTTP_201_CREATED)
def create_tablet(
    tablet: TabletCreate,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return tablet_service.create_tablet(db, tablet)


@router.get("/", response_model=List[Tablet])
def list_tablets(
    warehouse_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return tablet_service.get_tablets(db, warehouse_id=warehouse_id, skip=skip, limit=limit)


@router.get("/{tablet_id}", response_model=Tablet)
def get_tablet(
    tablet_id: int,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    tablet = tablet_service.get_tablet(db, tablet_id)
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet not found"
        )
    return tablet


@router.put("/{tablet_id}", response_model=Tablet)
def update_tablet(
    tablet_id: int,
    tablet_update: TabletUpdate,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    tablet = tablet_service.update_tablet(db, tablet_id, tablet_update)
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet not found"
        )
    return tablet


@router.post("/{tablet_id}/sync", response_model=Tablet)
def sync_tablet(
    tablet_id: int,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    tablet = tablet_service.update_tablet_sync(db, tablet_id)
    if not tablet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet not found"
        )
    return tablet


@router.delete("/{tablet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tablet(
    tablet_id: int,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    success = tablet_service.delete_tablet(db, tablet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablet not found"
        )
