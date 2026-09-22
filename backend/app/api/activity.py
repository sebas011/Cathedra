from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.db import get_db
from app.models import ActivityEvent, LocalUser

router = APIRouter(prefix="/activity", tags=["Activity History"])


@router.get("")
def list_activity(db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> list[dict[str, object]]:
    events = db.scalars(select(ActivityEvent).order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc()).limit(200)).all()
    return [{"id": event.id, "username": event.username, "action": event.action, "area": event.area, "created_at": event.created_at} for event in events]
