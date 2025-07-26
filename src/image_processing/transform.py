import cv2
import numpy as np
from typing import Tuple, Optional


class ImageTransformer:
    """Image transformation utilities for face alignment and scaling"""
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float, center: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Rotate an image by a given angle
        
        Args:
            image: Input image
            angle: Rotation angle in degrees
            center: Center of rotation (default: image center)
            
        Returns:
            Rotated image
        """
        if center is None:
            center = (image.shape[1] // 2, image.shape[0] // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
        return rotated
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int], maintain_aspect: bool = True) -> np.ndarray:
        """
        Resize an image to target size
        
        Args:
            image: Input image
            target_size: Target (width, height)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        if maintain_aspect:
            h, w = image.shape[:2]
            target_w, target_h = target_size
            
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize image
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Create canvas and center the image
            canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            x_offset = (target_w - new_w) // 2
            y_offset = (target_h - new_h) // 2
            canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
            
            return canvas
        else:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
    
    @staticmethod
    def align_face(image: np.ndarray, landmarks: dict, target_size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """
        Align face based on eye positions
        
        Args:
            image: Input image with detected face
            landmarks: Facial landmarks dictionary
            target_size: Target output size
            
        Returns:
            Aligned face image
        """
        if 'left_eye' not in landmarks or 'right_eye' not in landmarks:
            return ImageTransformer.resize_image(image, target_size)
        
        # Get eye centers
        left_eye_points = landmarks['left_eye']
        right_eye_points = landmarks['right_eye']
        
        if not left_eye_points or not right_eye_points:
            return ImageTransformer.resize_image(image, target_size)
        
        left_eye_center = (
            sum(p[0] for p in left_eye_points) // len(left_eye_points),
            sum(p[1] for p in left_eye_points) // len(left_eye_points)
        )
        
        right_eye_center = (
            sum(p[0] for p in right_eye_points) // len(right_eye_points),
            sum(p[1] for p in right_eye_points) // len(right_eye_points)
        )
        
        # Calculate angle for horizontal alignment
        dx = right_eye_center[0] - left_eye_center[0]
        dy = right_eye_center[1] - left_eye_center[1]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Rotate to align eyes horizontally
        center = ((left_eye_center[0] + right_eye_center[0]) // 2,
                 (left_eye_center[1] + right_eye_center[1]) // 2)
        
        aligned = ImageTransformer.rotate_image(image, -angle, center)
        
        # Resize to target size
        return ImageTransformer.resize_image(aligned, target_size)
    
    @staticmethod
    def create_mask(image: np.ndarray, landmarks: dict, feature: str = 'face_oval') -> np.ndarray:
        """
        Create a mask for a specific facial feature
        
        Args:
            image: Input image
            landmarks: Facial landmarks dictionary
            feature: Feature to create mask for
            
        Returns:
            Binary mask
        """
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        if feature in landmarks and landmarks[feature]:
            points = np.array(landmarks[feature], dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
        
        return mask
    
    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 15, sigma: float = 5.0) -> np.ndarray:
        """
        Apply Gaussian blur to an image
        
        Args:
            image: Input image
            kernel_size: Size of the Gaussian kernel
            sigma: Standard deviation for Gaussian kernel
            
        Returns:
            Blurred image
        """
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    
    @staticmethod
    def adjust_brightness_contrast(image: np.ndarray, brightness: float = 0, contrast: float = 1.0) -> np.ndarray:
        """
        Adjust brightness and contrast of an image
        
        Args:
            image: Input image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast multiplier (0.5 to 3.0)
            
        Returns:
            Adjusted image
        """
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        return adjusted
    
    @staticmethod
    def match_color_distribution(source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        Match color distribution of source image to target image
        
        Args:
            source: Source image to adjust
            target: Target image to match
            
        Returns:
            Color-matched source image
        """
        # Convert to LAB color space for better color matching
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB)
        
        # Calculate means and standard deviations for each channel
        source_mean, source_std = cv2.meanStdDev(source_lab)
        target_mean, target_std = cv2.meanStdDev(target_lab)
        
        # Normalize source to match target distribution
        matched_lab = source_lab.astype(np.float32)
        
        for i in range(3):
            matched_lab[:, :, i] = (matched_lab[:, :, i] - source_mean[i]) * (target_std[i] / source_std[i]) + target_mean[i]
        
        # Clip values and convert back to BGR
        matched_lab = np.clip(matched_lab, 0, 255).astype(np.uint8)
        matched_bgr = cv2.cvtColor(matched_lab, cv2.COLOR_LAB2BGR)
        
        return matched_bgr
