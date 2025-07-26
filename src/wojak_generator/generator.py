import cv2
import numpy as np
from typing import Optional, Dict, Tuple
from src.face_detection.detector import FaceDetector
from src.face_detection.landmarks import LandmarkExtractor
from src.image_processing.transform import ImageTransformer
from src.image_processing.blend import ImageBlender
from src.wojak_generator.templates import TemplateManager
from src.utils.image_utils import ImageUtils


class WojakGenerator:
    """Main class for generating Wojak memes from face images"""
    
    def __init__(self, template_directory: str = "assets/templates"):
        self.face_detector = FaceDetector(confidence_threshold=0.5)
        self.landmark_extractor = LandmarkExtractor()
        self.template_manager = TemplateManager(template_directory)
        
        # Ensure default templates exist
        self.template_manager.create_default_templates()
        
        # Generation parameters
        self.default_params = {
            'face_blend_strength': 0.6,
            'eye_blend_strength': 0.8,
            'mouth_blend_strength': 0.7,
            'nose_blend_strength': 0.3,
            'color_match_strength': 0.4,
            'contrast_enhancement': 1.1,
            'template_size': (256, 256)
        }
    
    def generate_wojak(self, 
                      face_image: np.ndarray, 
                      template_name: str = 'wojak_basic',
                      params: Optional[Dict] = None) -> Optional[np.ndarray]:
        """
        Generate a Wojak meme from a face image
        
        Args:
            face_image: Input face image
            template_name: Name of the Wojak template to use
            params: Generation parameters
            
        Returns:
            Generated Wojak image or None if generation failed
        """
        if params is None:
            params = self.default_params.copy()
        else:
            # Merge with defaults
            merged_params = self.default_params.copy()
            merged_params.update(params)
            params = merged_params
        
        # Validate input image
        if not ImageUtils.validate_image(face_image):
            print("Invalid input image")
            return None
        
        # Get template
        template_image = self.template_manager.get_template_image(template_name)
        if template_image is None:
            print(f"Template '{template_name}' not found")
            return None
        
        # Resize template to target size
        template_size = params['template_size']
        template_resized = ImageTransformer.resize_image(template_image, template_size, maintain_aspect=False)
        
        try:
            # Step 1: Detect and crop face
            cropped_face = self.face_detector.crop_face(face_image, padding=0.3)
            if cropped_face is None:
                print("No face detected in input image")
                return None
            
            # Step 2: Extract facial landmarks
            landmarks = self.landmark_extractor.extract_landmarks(cropped_face)
            if landmarks is None:
                print("Could not extract facial landmarks")
                return None
            
            # Step 3: Align and resize face to match template
            aligned_face = ImageTransformer.align_face(cropped_face, landmarks, template_size)
            
            # Step 4: Apply color matching
            color_matched_face = ImageTransformer.match_color_distribution(aligned_face, template_resized)
            color_match_strength = params['color_match_strength']
            aligned_face = ImageBlender.alpha_blend(
                color_matched_face, aligned_face, 
                np.ones(aligned_face.shape[:2], dtype=np.uint8) * 255, 
                color_match_strength
            )
            
            # Step 5: Extract landmarks from aligned face
            aligned_landmarks = self.landmark_extractor.extract_landmarks(aligned_face)
            if aligned_landmarks is None:
                aligned_landmarks = landmarks  # Fallback to original landmarks
            
            # Step 6: Blend facial features
            result = self._blend_facial_features(aligned_face, template_resized, aligned_landmarks, params)
            
            # Step 7: Apply final enhancements
            result = self._apply_final_enhancements(result, params)
            
            return result
            
        except Exception as e:
            print(f"Error generating Wojak: {e}")
            return None
    
    def _blend_facial_features(self, 
                              face_image: np.ndarray, 
                              template_image: np.ndarray, 
                              landmarks: Dict, 
                              params: Dict) -> np.ndarray:
        """
        Blend facial features from face image onto template
        
        Args:
            face_image: Aligned face image
            template_image: Wojak template
            landmarks: Facial landmarks
            params: Generation parameters
            
        Returns:
            Blended image
        """
        result = template_image.copy()
        
        # Define feature weights from parameters
        feature_weights = {
            'eyes': params.get('eye_blend_strength', 0.8),
            'mouth': params.get('mouth_blend_strength', 0.7),
            'nose': params.get('nose_blend_strength', 0.3)
        }
        
        # Blend eyes
        if 'left_eye' in landmarks and 'right_eye' in landmarks:
            eye_mask = self._create_feature_mask(face_image.shape[:2], landmarks, ['left_eye', 'right_eye'])
            if eye_mask is not None:
                # Enhance eye contrast before blending
                enhanced_face = ImageBlender.enhance_contrast_selective(face_image, eye_mask, 1.2)
                feathered_mask = ImageBlender.feather_mask(eye_mask, 5)
                result = ImageBlender.alpha_blend(enhanced_face, result, feathered_mask, feature_weights['eyes'])
        
        # Blend mouth
        if 'mouth' in landmarks:
            mouth_mask = self._create_feature_mask(face_image.shape[:2], landmarks, ['mouth'])
            if mouth_mask is not None:
                feathered_mask = ImageBlender.feather_mask(mouth_mask, 3)
                result = ImageBlender.alpha_blend(face_image, result, feathered_mask, feature_weights['mouth'])
        
        # Blend nose (optional, usually subtle)
        if feature_weights['nose'] > 0 and 'nose' in landmarks:
            nose_mask = self._create_feature_mask(face_image.shape[:2], landmarks, ['nose'])
            if nose_mask is not None:
                feathered_mask = ImageBlender.feather_mask(nose_mask, 2)
                result = ImageBlender.alpha_blend(face_image, result, feathered_mask, feature_weights['nose'])
        
        return result
    
    def _create_feature_mask(self, shape: Tuple[int, int], landmarks: Dict, features: list) -> Optional[np.ndarray]:
        """
        Create mask for specified facial features
        
        Args:
            shape: Image shape (height, width)
            landmarks: Facial landmarks
            features: List of features to include in mask
            
        Returns:
            Feature mask or None
        """
        mask = np.zeros(shape, dtype=np.uint8)
        
        for feature in features:
            if feature in landmarks and landmarks[feature]:
                points = np.array(landmarks[feature], dtype=np.int32)
                if len(points) > 2:
                    cv2.fillPoly(mask, [points], 255)
        
        return mask if np.any(mask) else None
    
    def _apply_final_enhancements(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """
        Apply final enhancements to the generated image
        
        Args:
            image: Generated image
            params: Generation parameters
            
        Returns:
            Enhanced image
        """
        result = image.copy()
        
        # Apply contrast enhancement
        contrast_factor = params.get('contrast_enhancement', 1.1)
        if contrast_factor != 1.0:
            result = ImageTransformer.adjust_brightness_contrast(result, 0, contrast_factor)
        
        # Apply subtle sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(result, -1, kernel * 0.1)
        result = cv2.addWeighted(result, 0.9, sharpened, 0.1, 0)
        
        return result
    
    def get_available_templates(self) -> list:
        """
        Get list of available template names
        
        Returns:
            List of template names
        """
        return self.template_manager.get_template_names()
    
    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        Get information about a specific template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template information dictionary
        """
        return self.template_manager.get_template_metadata(template_name)
    
    def get_all_templates_info(self) -> list:
        """
        Get information about all available templates
        
        Returns:
            List of template information dictionaries
        """
        return self.template_manager.get_all_templates_info()
    
    def preview_template(self, template_name: str, size: int = 150) -> Optional[str]:
        """
        Get template preview as base64 string
        
        Args:
            template_name: Name of the template
            size: Preview size
            
        Returns:
            Base64 encoded preview image
        """
        thumbnail = self.template_manager.get_template_thumbnail(template_name, size)
        if thumbnail is None:
            return None
        
        return ImageUtils.image_to_base64(thumbnail, 'PNG')
    
    def batch_generate(self, 
                      face_images: list, 
                      template_name: str = 'wojak_basic',
                      params: Optional[Dict] = None) -> list:
        """
        Generate Wojak memes for multiple face images
        
        Args:
            face_images: List of face images
            template_name: Template to use for all images
            params: Generation parameters
            
        Returns:
            List of generated images (some may be None if generation failed)
        """
        results = []
        
        for face_image in face_images:
            result = self.generate_wojak(face_image, template_name, params)
            results.append(result)
        
        return results
    
    def validate_face_image(self, face_image: np.ndarray) -> Dict:
        """
        Validate if face image is suitable for Wojak generation
        
        Args:
            face_image: Input face image
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': False,
            'issues': [],
            'face_detected': False,
            'landmarks_detected': False,
            'image_quality': 'unknown'
        }
        
        # Check basic image validity
        if not ImageUtils.validate_image(face_image):
            result['issues'].append('Invalid image format or size too small')
            return result
        
        # Check if face is detected
        faces = self.face_detector.detect_faces(face_image)
        if not faces:
            result['issues'].append('No face detected in image')
            return result
        
        result['face_detected'] = True
        
        # Check if landmarks can be extracted
        cropped_face = self.face_detector.crop_face(face_image)
        if cropped_face is not None:
            landmarks = self.landmark_extractor.extract_landmarks(cropped_face)
            if landmarks is not None:
                result['landmarks_detected'] = True
            else:
                result['issues'].append('Could not extract facial landmarks')
        
        # Assess image quality
        image_info = ImageUtils.get_image_info(face_image)
        if image_info:
            if image_info['width'] < 200 or image_info['height'] < 200:
                result['issues'].append('Image resolution too low (minimum 200x200)')
                result['image_quality'] = 'low'
            elif image_info['width'] < 400 or image_info['height'] < 400:
                result['image_quality'] = 'medium'
            else:
                result['image_quality'] = 'high'
        
        # Check if valid for generation
        result['valid'] = result['face_detected'] and result['landmarks_detected'] and not any(
            'Invalid' in issue for issue in result['issues']
        )
        
        return result
