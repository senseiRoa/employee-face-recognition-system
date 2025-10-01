from typing import List
from app.ports.services import LogService

class ListLogsUseCase:
    def __init__(self, log_service: LogService):
        self.log_service = log_service

    def execute(self) -> List[dict]:
        return self.log_service.get_logs()
