from fastapi import APIRouter, Depends, Body
from app.use_cases.recognize_face import RecognizeFaceUseCase
from infrastructure.adapters.face_recognition_adapter import FaceRecognitionAdapter
from infrastructure.adapters.employee_repository import EmployeeRepository
from app.ports.services import FaceRecognitionService, EmployeeService
from infrastructure.api.auth import get_current_user
from pydantic import BaseModel

class RecognitionRequest(BaseModel):
    image_base64: str

router = APIRouter()

def get_face_recognition_service() -> FaceRecognitionService:
    return FaceRecognitionAdapter()

def get_employee_service() -> EmployeeService:
    return EmployeeRepository()

@router.post("/check_in_out")
def recognize_face(
    request: RecognitionRequest,
    face_recognition_service: FaceRecognitionService = Depends(get_face_recognition_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user) # Add authentication
):
    use_case = RecognizeFaceUseCase(face_recognition_service, employee_service)
    return use_case.execute(request.image_base64)
