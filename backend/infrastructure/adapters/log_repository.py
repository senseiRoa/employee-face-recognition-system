from typing import List
from app.ports.services import LogService
from infrastructure.adapters.database import SessionLocal
from infrastructure.adapters.orm.access_log import AccessLog as AccessLogORM

class LogRepository(LogService):
    def get_logs(self) -> List[dict]:
        db = SessionLocal()
        logs_orm = db.query(AccessLogORM).all()
        db.close()
        return [{"id": log.id, "employee_id": log.employee_id, "event": log.event, "ts": log.ts} for log in logs_orm]
