from app.ports.services import EmployeeService
from domain.employee import Employee

class RegisterEmployeeUseCase:
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service

    def execute(self, employee_id: str, name: str, image_base64: str) -> Employee:
        return self.employee_service.register_employee(employee_id, name, image_base64)
