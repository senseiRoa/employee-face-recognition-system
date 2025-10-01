from fastapi import APIRouter, Depends
from typing import List
from app.use_cases.list_employees import ListEmployeesUseCase
from app.use_cases.register_employee import RegisterEmployeeUseCase
from domain.employee import Employee
from infrastructure.adapters.employee_repository import EmployeeRepository
from app.ports.services import EmployeeService
from infrastructure.api.auth import get_current_user
from pydantic import BaseModel

class EmployeeRegistrationRequest(BaseModel):
    employee_id: str
    name: str
    image_base64: str

router = APIRouter()

def get_employee_service() -> EmployeeService:
    return EmployeeRepository()

@router.post("/employees", response_model=Employee)
def register_employee(
    request: EmployeeRegistrationRequest,
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    use_case = RegisterEmployeeUseCase(employee_service)
    return use_case.execute(request.employee_id, request.name, request.image_base64)

@router.get("/employees", response_model=List[Employee])
def list_employees(
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    use_case = ListEmployeesUseCase(employee_service)
    return use_case.execute()
