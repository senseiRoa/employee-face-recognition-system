from abc import ABC, abstractmethod
from typing import List

from domain.employee import Employee

class EmployeeService(ABC):
    @abstractmethod
    def register_employee(self, employee_id: str, name: str, image_base64: str) -> Employee:
        pass

    @abstractmethod
    def get_employees(self) -> List[Employee]:
        pass

class FaceRecognitionService(ABC):
    @abstractmethod
    def recognize_face(self, image_base64: str, employees: List[Employee]) -> dict:
        pass

class LogService(ABC):
    @abstractmethod
    def get_logs(self) -> List[dict]:
        pass
