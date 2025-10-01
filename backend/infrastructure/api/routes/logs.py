from fastapi import APIRouter, Depends
from typing import List
from app.use_cases.list_logs import ListLogsUseCase
from infrastructure.adapters.log_repository import LogRepository

router = APIRouter()

def get_log_service():
    return LogRepository()

@router.get("/logs", response_model=List[dict])
def list_logs(log_service: LogRepository = Depends(get_log_service)):
    use_case = ListLogsUseCase(log_service)
    return use_case.execute()
