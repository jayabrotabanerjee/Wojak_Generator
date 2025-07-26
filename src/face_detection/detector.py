import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional


class FaceDetector:
    """Face detection using MediaPipe Face Detection"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=confidence_threshold
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image and return bounding boxes
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of bounding boxes as (x, y, width, height)
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = image.shape
                
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def get_largest_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the largest face in the image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Bounding box of the largest face or None if no face found
        """
        faces = self.detect_faces(image)
        if not faces:
            return None
        
        # Return the face with the largest area
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return largest_face
    
    def crop_face(self, image: np.ndarray, padding: float = 0.2) -> Optional[np.ndarray]:
        """
        Crop the largest face from the image with padding
        
        Args:
            image: Input image as numpy array
            padding: Padding factor around the face
            
        Returns:
            Cropped face image or None if no face found
        """
        face_bbox = self.get_largest_face(image)
        if face_bbox is None:
            return None
        
        x, y, w, h = face_bbox
        
        # Add padding
        pad_x = int(w * padding)
        pad_y = int(h * padding)
        
        # Calculate crop coordinates with padding
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(image.shape[1], x + w + pad_x)
        y2 = min(image.shape[0], y + h + pad_y)
        
        return image[y1:y2, x1:x2]
