from app.ports.services import FaceRecognitionService
from deepface import DeepFace
import numpy as np
import base64
import cv2
import ast
from typing import List
from domain.employee import Employee

class FaceRecognitionAdapter(FaceRecognitionService):
    def recognize_face(self, image_base64: str, employees: List[Employee]) -> dict:
        # Decode the base64 image
        img_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Generate embedding for the new face
        try:
            new_embedding = DeepFace.represent(img_path=img, model_name="VGG-Face", enforce_detection=False)
        except ValueError as e:
            # This can happen if no face is detected in the image
            return {"recognized": False, "error": str(e)}

        # Prepare the list of known representations
        representations = []
        for employee in employees:
            for encoding_str in employee.encodings:
                try:
                    # Safely evaluate the string representation of the list
                    embedding_list = ast.literal_eval(encoding_str)
                    # DeepFace may return a dict with the embedding, get the vector
                    if isinstance(embedding_list, list) and len(embedding_list) > 0 and isinstance(embedding_list[0], dict):
                        embedding_vector = embedding_list[0]["embedding"]
                        representations.append([embedding_vector, employee.id])
                except (ValueError, SyntaxError):
                    # Handle cases where the string is not a valid list
                    continue
        
        if not representations:
            return {"recognized": False, "error": "No known faces to compare against."}

        # Find the closest face in the database using in-memory representations
        dfs = DeepFace.find(img_path=new_embedding[0]["embedding"], db_path="", representations=representations, model_name="VGG-Face", distance_metric="cosine", enforce_detection=False)

        # Return the identity of the recognized face
        if len(dfs) > 0 and len(dfs[0]) > 0:
            # The identity is the employee_id we passed in the representations list
            employee_id = dfs[0].iloc[0].identity
            return {"recognized": True, "employee_id": employee_id}
        else:
            return {"recognized": False}

    def represent(self, image_base64: str) -> list:
        # Decode the base64 image
        img_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Generate the face embedding
        embedding = DeepFace.represent(img_path=img, model_name="VGG-Face")

        return embedding