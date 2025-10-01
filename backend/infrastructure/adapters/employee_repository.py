from sqlalchemy.orm import joinedload
from typing import List
import base64
import os
from app.ports.services import EmployeeService
from domain.employee import Employee
from infrastructure.adapters.database import SessionLocal
from infrastructure.adapters.orm.employee import Employee as EmployeeORM, FaceEncoding
from infrastructure.adapters.face_recognition_adapter import FaceRecognitionAdapter

class EmployeeRepository(EmployeeService):
    def register_employee(self, employee_id: str, name: str, image_base64: str) -> Employee:
        db = SessionLocal()
        face_recognition_adapter = FaceRecognitionAdapter()

        # Get the face embedding
        embedding = face_recognition_adapter.represent(image_base64)
        embedding_str = str(embedding)

        # Save the image to the data/employees directory
        img_path = f"/app/data/employees/{employee_id}.jpg"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # Create the employee and face encoding objects
        employee_orm = EmployeeORM(id=employee_id, name=name)
        face_encoding = FaceEncoding(encoding=embedding_str, employee=employee_orm)

        db.add(employee_orm)
        db.add(face_encoding)
        db.commit()
        db.refresh(employee_orm)
        db.close()

        return Employee(id=employee_orm.id, name=employee_orm.name, encodings=[embedding_str])

    def get_employees(self) -> List[Employee]:
        db = SessionLocal()
        employees_orm = db.query(EmployeeORM).options(joinedload(EmployeeORM.encodings)).all()
        
        employees = []
        for emp_orm in employees_orm:
            encodings_str = [enc.encoding for enc in emp_orm.encodings]
            employees.append(Employee(id=emp_orm.id, name=emp_orm.name, encodings=encodings_str))
            
        db.close()
        return employees