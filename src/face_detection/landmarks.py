import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Optional, Tuple


class LandmarkExtractor:
    """Extract facial landmarks using MediaPipe Face Mesh"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Important landmark indices for Wojak generation
        self.key_landmarks = {
            'left_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
            'right_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
            'mouth': [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 78],
            'nose': [1, 2, 5, 6, 19, 20, 131, 134, 102, 48, 115, 116, 117, 118, 119, 120, 121, 126, 142, 36],
            'face_oval': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        }
    
    def extract_landmarks(self, image: np.ndarray) -> Optional[Dict[str, List[Tuple[int, int]]]]:
        """
        Extract facial landmarks from an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary containing landmark coordinates for different facial features
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return None
        
        face_landmarks = results.multi_face_landmarks[0]
        h, w, _ = image.shape
        
        landmarks = {}
        
        for feature_name, indices in self.key_landmarks.items():
            feature_points = []
            for idx in indices:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    feature_points.append((x, y))
            landmarks[feature_name] = feature_points
        
        return landmarks
    
    def get_face_center(self, landmarks: Dict[str, List[Tuple[int, int]]]) -> Tuple[int, int]:
        """
        Calculate the center point of the face
        
        Args:
            landmarks: Dictionary of facial landmarks
            
        Returns:
            Center coordinates (x, y)
        """
        all_points = []
        for feature_points in landmarks.values():
            all_points.extend(feature_points)
        
        if not all_points:
            return (0, 0)
        
        center_x = sum(point[0] for point in all_points) // len(all_points)
        center_y = sum(point[1] for point in all_points) // len(all_points)
        
        return (center_x, center_y)
    
    def get_face_angle(self, landmarks: Dict[str, List[Tuple[int, int]]]) -> float:
        """
        Calculate the rotation angle of the face
        
        Args:
            landmarks: Dictionary of facial landmarks
            
        Returns:
            Angle in degrees
        """
        if 'left_eye' not in landmarks or 'right_eye' not in landmarks:
            return 0.0
        
        # Get eye centers
        left_eye_points = landmarks['left_eye']
        right_eye_points = landmarks['right_eye']
        
        if not left_eye_points or not right_eye_points:
            return 0.0
        
        left_eye_center = (
            sum(p[0] for p in left_eye_points) // len(left_eye_points),
            sum(p[1] for p in left_eye_points) // len(left_eye_points)
        )
        
        right_eye_center = (
            sum(p[0] for p in right_eye_points) // len(right_eye_points),
            sum(p[1] for p in right_eye_points) // len(right_eye_points)
        )
        
        # Calculate angle
        dx = right_eye_center[0] - left_eye_center[0]
        dy = right_eye_center[1] - left_eye_center[1]
        
        angle = np.degrees(np.arctan2(dy, dx))
        return angle
    
    def get_face_scale(self, landmarks: Dict[str, List[Tuple[int, int]]], reference_size: int = 200) -> float:
        """
        Calculate the scale factor for the face relative to a reference size
        
        Args:
            landmarks: Dictionary of facial landmarks
            reference_size: Reference face size in pixels
            
        Returns:
            Scale factor
        """
        if 'face_oval' not in landmarks:
            return 1.0
        
        face_points = landmarks['face_oval']
        if not face_points:
            return 1.0
        
        # Calculate face width and height
        x_coords = [p[0] for p in face_points]
        y_coords = [p[1] for p in face_points]
        
        face_width = max(x_coords) - min(x_coords)
        face_height = max(y_coords) - min(y_coords)
        
        # Use the larger dimension for scaling
        face_size = max(face_width, face_height)
        
        if face_size == 0:
            return 1.0
        
        scale = reference_size / face_size
        return scale
