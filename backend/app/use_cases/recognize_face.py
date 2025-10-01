from app.ports.services import FaceRecognitionService, EmployeeService
from domain.employee import Employee
from typing import List

class RecognizeFaceUseCase:
    def __init__(self, face_recognition_service: FaceRecognitionService, employee_service: EmployeeService):
        self.face_recognition_service = face_recognition_service
        self.employee_service = employee_service

    def execute(self, image_base64: str) -> dict:
        employees: List[Employee] = self.employee_service.get_employees()
        return self.face_recognition_service.recognize_face(image_base64, employees)
