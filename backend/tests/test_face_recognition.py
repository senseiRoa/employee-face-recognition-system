import unittest
import face_recognition
import cv2

class TestFaceRecognition(unittest.TestCase):

    def test_find_face_in_image(self):
        # Load the image from file
        print("Loading image from test_img/foto1.png...")
        image = cv2.imread("test_img/foto1.png")
        
        # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
        print("Converting image from BGR to RGB...")
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face locations in the image
        print("Detecting face locations...")
        face_locations = face_recognition.face_locations(rgb_image)
        print(f"Number of faces found: {len(face_locations)}")
        
        # Assert that at least one face was found
        self.assertGreater(len(face_locations), 0)

if __name__ == '__main__':
    unittest.main()