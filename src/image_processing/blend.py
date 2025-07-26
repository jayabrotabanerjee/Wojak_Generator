import cv2
import numpy as np
from typing import Tuple, Optional


class ImageBlender:
    """Image blending utilities for seamless integration of face features"""
    
    @staticmethod
    def alpha_blend(foreground: np.ndarray, background: np.ndarray, mask: np.ndarray, alpha: float = 1.0) -> np.ndarray:
        """
        Blend foreground into background using alpha mask
        
        Args:
            foreground: Foreground image
            background: Background image
            mask: Alpha mask (0-255)
            alpha: Global alpha multiplier
            
        Returns:
            Blended image
        """
        # Normalize mask to 0-1 range
        normalized_mask = (mask.astype(np.float32) / 255.0) * alpha
        
        # Ensure mask has 3 channels
        if len(normalized_mask.shape) == 2:
            normalized_mask = np.stack([normalized_mask] * 3, axis=2)
        
        # Resize images to match if necessary
        h, w = background.shape[:2]
        if foreground.shape[:2] != (h, w):
            foreground = cv2.resize(foreground, (w, h))
        if normalized_mask.shape[:2] != (h, w):
            normalized_mask = cv2.resize(normalized_mask, (w, h))
            if len(normalized_mask.shape) == 2:
                normalized_mask = np.stack([normalized_mask] * 3, axis=2)
        
        # Blend images
        foreground_f = foreground.astype(np.float32)
        background_f = background.astype(np.float32)
        
        blended = foreground_f * normalized_mask + background_f * (1 - normalized_mask)
        
        return blended.astype(np.uint8)
    
    @staticmethod
    def poisson_blend(source: np.ndarray, target: np.ndarray, mask: np.ndarray, center: Tuple[int, int]) -> np.ndarray:
        """
        Perform Poisson blending for seamless integration
        
        Args:
            source: Source image
            target: Target image
            mask: Binary mask
            center: Center point for blending
            
        Returns:
            Blended image
        """
        try:
            # Ensure mask is binary
            mask_binary = np.where(mask > 127, 255, 0).astype(np.uint8)
            
            # Perform seamless cloning
            result = cv2.seamlessClone(source, target, mask_binary, center, cv2.NORMAL_CLONE)
            return result
        except cv2.error:
            # Fallback to alpha blending if Poisson blending fails
            return ImageBlender.alpha_blend(source, target, mask)
    
    @staticmethod
    def feather_mask(mask: np.ndarray, feather_amount: int = 10) -> np.ndarray:
        """
        Apply feathering to a mask for softer edges
        
        Args:
            mask: Input binary mask
            feather_amount: Amount of feathering in pixels
            
        Returns:
            Feathered mask
        """
        # Apply Gaussian blur for feathering
        feathered = cv2.GaussianBlur(mask, (feather_amount * 2 + 1, feather_amount * 2 + 1), feather_amount / 3)
        return feathered
    
    @staticmethod
    def create_gradient_mask(shape: Tuple[int, int], center: Tuple[int, int], radius: int) -> np.ndarray:
        """
        Create a radial gradient mask
        
        Args:
            shape: Mask shape (height, width)
            center: Center of the gradient
            radius: Radius of the gradient
            
        Returns:
            Gradient mask
        """
        h, w = shape
        y, x = np.ogrid[:h, :w]
        center_y, center_x = center
        
        # Calculate distance from center
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Create gradient
        mask = np.clip(255 - (distance / radius * 255), 0, 255).astype(np.uint8)
        
        return mask
    
    @staticmethod
    def blend_facial_features(face_image: np.ndarray, wojak_template: np.ndarray, landmarks: dict, 
                            feature_weights: dict = None) -> np.ndarray:
        """
        Blend specific facial features from face image onto Wojak template
        
        Args:
            face_image: Source face image
            wojak_template: Target Wojak template
            landmarks: Facial landmarks
            feature_weights: Weights for different features
            
        Returns:
            Blended image
        """
        if feature_weights is None:
            feature_weights = {
                'eyes': 0.7,
                'mouth': 0.6,
                'nose': 0.4
            }
        
        result = wojak_template.copy()
        
        # Blend eyes
        if 'left_eye' in landmarks and 'right_eye' in landmarks:
            eye_mask = ImageBlender._create_eye_mask(face_image.shape[:2], landmarks)
            if eye_mask is not None:
                feathered_mask = ImageBlender.feather_mask(eye_mask, 5)
                result = ImageBlender.alpha_blend(face_image, result, feathered_mask, feature_weights.get('eyes', 0.7))
        
        # Blend mouth
        if 'mouth' in landmarks:
            mouth_mask = ImageBlender._create_mouth_mask(face_image.shape[:2], landmarks)
            if mouth_mask is not None:
                feathered_mask = ImageBlender.feather_mask(mouth_mask, 3)
                result = ImageBlender.alpha_blend(face_image, result, feathered_mask, feature_weights.get('mouth', 0.6))
        
        # Blend nose (optional, with lower weight)
        if 'nose' in landmarks and feature_weights.get('nose', 0) > 0:
            nose_mask = ImageBlender._create_nose_mask(face_image.shape[:2], landmarks)
            if nose_mask is not None:
                feathered_mask = ImageBlender.feather_mask(nose_mask, 2)
                result = ImageBlender.alpha_blend(face_image, result, feathered_mask, feature_weights.get('nose', 0.4))
        
        return result
    
    @staticmethod
    def _create_eye_mask(shape: Tuple[int, int], landmarks: dict) -> Optional[np.ndarray]:
        """Create mask for eye regions"""
        mask = np.zeros(shape, dtype=np.uint8)
        
        for eye in ['left_eye', 'right_eye']:
            if eye in landmarks and landmarks[eye]:
                points = np.array(landmarks[eye], dtype=np.int32)
                cv2.fillPoly(mask, [points], 255)
        
        return mask if np.any(mask) else None
    
    @staticmethod
    def _create_mouth_mask(shape: Tuple[int, int], landmarks: dict) -> Optional[np.ndarray]:
        """Create mask for mouth region"""
        mask = np.zeros(shape, dtype=np.uint8)
        
        if 'mouth' in landmarks and landmarks['mouth']:
            points = np.array(landmarks['mouth'], dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
        
        return mask if np.any(mask) else None
    
    @staticmethod
    def _create_nose_mask(shape: Tuple[int, int], landmarks: dict) -> Optional[np.ndarray]:
        """Create mask for nose region"""
        mask = np.zeros(shape, dtype=np.uint8)
        
        if 'nose' in landmarks and landmarks['nose']:
            points = np.array(landmarks['nose'], dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
        
        return mask if np.any(mask) else None
    
    @staticmethod
    def enhance_contrast_selective(image: np.ndarray, mask: np.ndarray, factor: float = 1.2) -> np.ndarray:
        """
        Enhance contrast selectively in masked regions
        
        Args:
            image: Input image
            mask: Mask defining regions to enhance
            factor: Contrast enhancement factor
            
        Returns:
            Enhanced image
        """
        enhanced = image.copy().astype(np.float32)
        
        # Normalize mask
        mask_norm = mask.astype(np.float32) / 255.0
        if len(mask_norm.shape) == 2:
            mask_norm = np.stack([mask_norm] * 3, axis=2)
        
        # Calculate mean for contrast adjustment
        mean = np.mean(enhanced, axis=(0, 1), keepdims=True)
        
        # Apply contrast enhancement
        enhanced = (enhanced - mean) * factor + mean
        
        # Blend enhanced version with original based on mask
        result = enhanced * mask_norm + image.astype(np.float32) * (1 - mask_norm)
        
        return np.clip(result, 0, 255).astype(np.uint8)
