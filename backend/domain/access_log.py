from pydantic import BaseModel
import datetime

class AccessLog(BaseModel):
    id: int
    employee_id: str
    event: str
    ts: datetime.datetime
