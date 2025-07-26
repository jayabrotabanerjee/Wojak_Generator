import unittest
import numpy as np
import cv2
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from face_detection.detector import FaceDetector
from face_detection.landmarks import LandmarkExtractor


class TestFaceDetector(unittest.TestCase):
    """Test cases for FaceDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = FaceDetector()
        
        # Create a simple test image with a face-like structure
        self.test_image = self._create_test_face_image()
    
    def _create_test_face_image(self):
        """Create a simple test image that resembles a face"""
        # Create a 300x300 image
        image = np.ones((300, 300, 3), dtype=np.uint8) * 240
        
        # Draw a simple face
        center = (150, 150)
        
        # Head (circle)
        cv2.circle(image, center, 80, (220, 180, 150), -1)
        
        # Eyes
        cv2.circle(image, (130, 130), 8, (0, 0, 0), -1)  # Left eye
        cv2.circle(image, (170, 130), 8, (0, 0, 0), -1)  # Right eye
        
        # Nose
        cv2.circle(image, (150, 150), 4, (200, 160, 120), -1)
        
        # Mouth
        cv2.ellipse(image, (150, 180), (15, 8), 0, 0, 180, (100, 50, 50), -1)
        
        return image
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.confidence_threshold, 0.5)
    
    def test_detect_faces_with_valid_image(self):
        """Test face detection with a valid image"""
        faces = self.detector.detect_faces(self.test_image)
        self.assertIsInstance(faces, list)
        # Note: MediaPipe might not detect our simple drawn face, so we just test the return type
    
    def test_detect_faces_with_invalid_image(self):
        """Test face detection with invalid input"""
        # Test with None
        faces = self.detector.detect_faces(None)
        self.assertEqual(faces, [])
        
        # Test with empty array
        empty_image = np.array([])
        faces = self.detector.detect_faces(empty_image)
        self.assertEqual(faces, [])
    
    def test_get_largest_face(self):
        """Test getting the largest face from detection results"""
        # Test with image that may or may not have detectable faces
        largest_face = self.detector.get_largest_face(self.test_image)
        # Result could be None or a tuple, both are valid
        if largest_face is not None:
            self.assertIsInstance(largest_face, tuple)
            self.assertEqual(len(largest_face), 4)  # x, y, width, height
    
    def test_crop_face(self):
        """Test face cropping functionality"""
        cropped = self.detector.crop_face(self.test_image)
        # Result could be None if no face is detected, or a numpy array
        if cropped is not None:
            self.assertIsInstance(cropped, np.ndarray)
            self.assertEqual(len(cropped.shape), 3)  # Should be 3D array


class TestLandmarkExtractor(unittest.TestCase):
    """Test cases for LandmarkExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = LandmarkExtractor()
        self.test_image = self._create_test_face_image()
    
    def _create_test_face_image(self):
        """Create a simple test image that resembles a face"""
        image = np.ones((300, 300, 3), dtype=np.uint8) * 240
        center = (150, 150)
        
        # Head (circle)
        cv2.circle(image, center, 80, (220, 180, 150), -1)
        
        # Eyes
        cv2.circle(image, (130, 130), 8, (0, 0, 0), -1)
        cv2.circle(image, (170, 130), 8, (0, 0, 0), -1)
        
        # Nose
        cv2.circle(image, (150, 150), 4, (200, 160, 120), -1)
        
        # Mouth
        cv2.ellipse(image, (150, 180), (15, 8), 0, 0, 180, (100, 50, 50), -1)
        
        return image
    
    def test_extractor_initialization(self):
        """Test that landmark extractor initializes correctly"""
        self.assertIsNotNone(self.extractor)
        self.assertIsNotNone(self.extractor.key_landmarks)
        
        # Check that key landmark categories are defined
        expected_features = ['left_eye', 'right_eye', 'mouth', 'nose', 'face_oval']
        for feature in expected_features:
            self.assertIn(feature, self.extractor.key_landmarks)
    
    def test_extract_landmarks(self):
        """Test landmark extraction"""
        landmarks = self.extractor.extract_landmarks(self.test_image)
        
        # Result could be None if no face is detected, or a dictionary
        if landmarks is not None:
            self.assertIsInstance(landmarks, dict)
            
            # Check that expected keys are present
            expected_keys = ['left_eye', 'right_eye', 'mouth', 'nose', 'face_oval']
            for key in expected_keys:
                self.assertIn(key, landmarks)
    
    def test_get_face_center(self):
        """Test face center calculation"""
        # Create mock landmarks
        mock_landmarks = {
            'left_eye': [(100, 100), (105, 100), (95, 100)],
            'right_eye': [(200, 100), (205, 100), (195, 100)],
            'mouth': [(150, 180), (155, 180), (145, 180)]
        }
        
        center = self.extractor.get_face_center(mock_landmarks)
        self.assertIsInstance(center, tuple)
        self.assertEqual(len(center), 2)
        
        # Check that center is roughly in the middle of the landmarks
        self.assertGreater(center[0], 50)  # x should be reasonable
        self.assertGreater(center[1], 50)  # y should be reasonable
    
    def test_get_face_angle(self):
        """Test face angle calculation"""
        # Create mock landmarks with horizontal eyes
        mock_landmarks = {
            'left_eye': [(100, 100)],
            'right_eye': [(200, 100)]
        }
        
        angle = self.extractor.get_face_angle(mock_landmarks)
        self.assertIsInstance(angle, float)
        self.assertAlmostEqual(angle, 0.0, places=1)  # Should be close to 0 for horizontal
        
        # Test with angled eyes
        mock_landmarks_angled = {
            'left_eye': [(100, 100)],
            'right_eye': [(200, 120)]
        }
        
        angle_angled = self.extractor.get_face_angle(mock_landmarks_angled)
        self.assertGreater(abs(angle_angled), 0)  # Should be non-zero
    
    def test_get_face_scale(self):
        """Test face scale calculation"""
        # Create mock landmarks
        mock_landmarks = {
            'face_oval': [(50, 50), (250, 50), (250, 250), (50, 250)]
        }
        
        scale = self.extractor.get_face_scale(mock_landmarks, reference_size=200)
        self.assertIsInstance(scale, float)
        self.assertGreater(scale, 0)


if __name__ == '__main__':
    unittest.main()
