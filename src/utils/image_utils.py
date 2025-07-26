import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional


class ImageUtils:
    """Utility functions for image processing and conversion"""
    
    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """
        Load an image from file path
        
        Args:
            file_path: Path to image file
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            image = cv2.imread(file_path)
            if image is None:
                # Try with PIL for better format support
                pil_image = Image.open(file_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return image
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            return None
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Load an image from bytes
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            # Try with OpenCV
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                # Try with PIL
                pil_image = Image.open(io.BytesIO(image_bytes))
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return image
        except Exception as e:
            print(f"Error loading image from bytes: {e}")
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, file_path: str, quality: int = 95) -> bool:
        """
        Save an image to file
        
        Args:
            image: Image as numpy array
            file_path: Output file path
            quality: JPEG quality (for JPEG files)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            elif file_path.lower().endswith('.png'):
                cv2.imwrite(file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 6])
            else:
                cv2.imwrite(file_path, image)
            return True
        except Exception as e:
            print(f"Error saving image {file_path}: {e}")
            return False
    
    @staticmethod
    def image_to_base64(image: np.ndarray, format: str = 'JPEG', quality: int = 95) -> str:
        """
        Convert image to base64 string
        
        Args:
            image: Image as numpy array
            format: Output format ('JPEG' or 'PNG')
            quality: Quality for JPEG
            
        Returns:
            Base64 encoded string
        """
        try:
            # Convert BGR to RGB for PIL
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Save to bytes
            buffer = io.BytesIO()
            if format.upper() == 'JPEG':
                pil_image.save(buffer, format='JPEG', quality=quality)
            else:
                pil_image.save(buffer, format='PNG')
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/{format.lower()};base64,{image_base64}"
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return ""
    
    @staticmethod
    def base64_to_image(base64_string: str) -> Optional[np.ndarray]:
        """
        Convert base64 string to image
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to image
            return ImageUtils.load_image_from_bytes(image_bytes)
        except Exception as e:
            print(f"Error converting base64 to image: {e}")
            return None
    
    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """
        Validate if image is valid
        
        Args:
            image: Image to validate
            
        Returns:
            True if valid, False otherwise
        """
        if image is None:
            return False
        
        if len(image.shape) != 3:
            return False
        
        if image.shape[2] != 3:
            return False
        
        if image.shape[0] < 50 or image.shape[1] < 50:
            return False
        
        return True
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """
        Get image information
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with image information
        """
        if not ImageUtils.validate_image(image):
            return {}
        
        height, width, channels = image.shape
        
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'dtype': str(image.dtype),
            'size_mb': (image.nbytes / 1024 / 1024),
            'aspect_ratio': width / height
        }
    
    @staticmethod
    def create_thumbnail(image: np.ndarray, max_size: int = 200) -> np.ndarray:
        """
        Create a thumbnail of the image
        
        Args:
            image: Input image
            max_size: Maximum dimension size
            
        Returns:
            Thumbnail image
        """
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale = min(max_size / width, max_size / height)
        
        if scale >= 1:
            return image.copy()
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return thumbnail
    
    @staticmethod
    def ensure_rgb_format(image: np.ndarray) -> np.ndarray:
        """
        Ensure image is in RGB format
        
        Args:
            image: Input image (BGR or RGB)
            
        Returns:
            RGB format image
        """
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume it's BGR and convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    @staticmethod
    def ensure_bgr_format(image: np.ndarray) -> np.ndarray:
        """
        Ensure image is in BGR format (OpenCV default)
        
        Args:
            image: Input image (RGB or BGR)
            
        Returns:
            BGR format image
        """
        # This is more complex to determine automatically
        # For now, assume input is already BGR (OpenCV default)
        return image
