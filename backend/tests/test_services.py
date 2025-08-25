import unittest
import base64
import numpy as np
from PIL import Image
import io
import face_recognition
import numpy as np

from services import b64_to_rgb_np, compute_encoding, serialize_encoding, deserialize_encoding

class TestServices(unittest.TestCase):

    def test_b64_to_rgb_np(self):
        print("Running test_b64_to_rgb_np...")
        # Read an image file and encode it as a base64 string
        with open("test_img/foto1.png", "rb") as f:
            b64_string = base64.b64encode(f.read()).decode("utf-8")
        print("Base64 string length:", len(b64_string))
        
        # Convert base64 string back to RGB numpy array
        img_np = b64_to_rgb_np(b64_string)
        print("Image numpy shape:", img_np.shape)
        # Check that the result is a numpy array
        self.assertIsInstance(img_np, np.ndarray)

    def test_compute_encoding(self):
        print("Running test_compute_encoding...")
        # Open an image and convert it to RGB
        image = Image.open("test_img/foto3.png").convert("RGB")
        # Convert image to numpy array
        image_np = np.array(image)
        print("Image numpy shape:", image_np.shape)
        # Compute face encoding using face_recognition
        encoding = face_recognition.face_encodings(image_np)[0]
        print("Encoding shape:", encoding.shape)
        # Check that encoding is a numpy array of length 128
        self.assertIsInstance(encoding, np.ndarray)
        self.assertEqual(len(encoding), 128)

    def test_serialize_deserialize_encoding(self):
        print("Running test_serialize_deserialize_encoding...")
        # Read an image file and encode it as a base64 string
        with open("test_img/foto1.png", "rb") as f:
            b64_string = base64.b64encode(f.read()).decode("utf-8")
        print("Base64 string length:", len(b64_string))
        
        # Compute face encoding from base64 string
        encoding = compute_encoding(b64_string)
        print("Original encoding (first 5 values):", encoding[:5])
        # Serialize the encoding to a string or bytes
        serialized_encoding = serialize_encoding(encoding)
        print("Serialized encoding type:", type(serialized_encoding))
        # Deserialize back to numpy array
        deserialized_encoding = deserialize_encoding(serialized_encoding)
        print("Deserialized encoding (first 5 values):", deserialized_encoding[:5])
        
        # Check that the original and deserialized encodings are close
        self.assertTrue(np.allclose(encoding, deserialized_encoding))

if __name__ == '__main__':
    unittest.main()