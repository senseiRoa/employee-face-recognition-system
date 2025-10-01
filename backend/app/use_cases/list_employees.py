from typing import List
from app.ports.services import EmployeeService
from domain.employee import Employee

class ListEmployeesUseCase:
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service

    def execute(self) -> List[Employee]:
        return self.employee_service.get_employees()
