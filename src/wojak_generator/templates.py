import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from src.utils.file_utils import FileUtils
from src.utils.image_utils import ImageUtils


class TemplateManager:
    """Manages Wojak templates and their metadata"""
    
    def __init__(self, template_directory: str = "assets/templates"):
        self.template_directory = template_directory
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all available templates from the template directory"""
        FileUtils.ensure_directory_exists(self.template_directory)
        
        # Define template metadata
        template_info = {
            'wojak_basic.png': {
                'name': 'Basic Wojak',
                'description': 'Classic Wojak face',
                'face_region': (50, 50, 150, 200),  # x, y, width, height
                'eye_positions': [(80, 100), (120, 100)],  # left_eye, right_eye
                'mouth_position': (100, 160)
            },
            'pointer_wojak.png': {
                'name': 'Pointer Wojak',
                'description': 'Wojak pointing with finger',
                'face_region': (40, 40, 140, 180),
                'eye_positions': [(70, 90), (110, 90)],
                'mouth_position': (90, 140)
            },
            'doomer.png': {
                'name': 'Doomer',
                'description': 'Depressed night-walking Wojak',
                'face_region': (45, 45, 145, 185),
                'eye_positions': [(75, 95), (115, 95)],
                'mouth_position': (95, 150)
            },
            'soyjak.png': {
                'name': 'Soyjak',
                'description': 'Soy-consuming variant',
                'face_region': (35, 35, 130, 170),
                'eye_positions': [(65, 85), (105, 85)],
                'mouth_position': (85, 130)
            },
            'brainlet.png': {
                'name': 'Brainlet',
                'description': 'Low IQ Wojak variant',
                'face_region': (60, 60, 120, 160),
                'eye_positions': [(85, 105), (115, 105)],
                'mouth_position': (100, 140)
            }
        }
        
        # Load existing templates
        template_files = FileUtils.list_template_files(self.template_directory)
        
        for template_path in template_files:
            filename = os.path.basename(template_path)
            template_name = os.path.splitext(filename)[0]
            
            # Load template image
            template_image = ImageUtils.load_image(template_path)
            if template_image is not None:
                # Get metadata if available
                metadata = template_info.get(filename, {
                    'name': template_name.replace('_', ' ').title(),
                    'description': f'{template_name} variant',
                    'face_region': (50, 50, 150, 200),
                    'eye_positions': [(80, 100), (120, 100)],
                    'mouth_position': (100, 160)
                })
                
                self.templates[template_name] = {
                    'image': template_image,
                    'path': template_path,
                    'metadata': metadata
                }
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names"""
        return list(self.templates.keys())
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """
        Get template by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary or None if not found
        """
        return self.templates.get(template_name)
    
    def get_template_image(self, template_name: str) -> Optional[np.ndarray]:
        """
        Get template image by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template image or None if not found
        """
        template = self.get_template(template_name)
        return template['image'] if template else None
    
    def get_template_metadata(self, template_name: str) -> Optional[Dict]:
        """
        Get template metadata by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template metadata or None if not found
        """
        template = self.get_template(template_name)
        return template['metadata'] if template else None
    
    def create_default_templates(self):
        """Create default template images if they don't exist"""
        default_templates = {
            'wojak_basic': self._create_basic_wojak(),
            'pointer_wojak': self._create_pointer_wojak(),
            'doomer': self._create_doomer(),
            'soyjak': self._create_soyjak(),
            'brainlet': self._create_brainlet()
        }
        
        for template_name, template_image in default_templates.items():
            template_path = os.path.join(self.template_directory, f"{template_name}.png")
            
            if not os.path.exists(template_path):
                if ImageUtils.save_image(template_image, template_path):
                    print(f"Created default template: {template_name}")
        
        # Reload templates after creation
        self._load_templates()
    
    def _create_basic_wojak(self) -> np.ndarray:
        """Create a basic Wojak template image"""
        # Create a simple Wojak-like face using OpenCV drawing functions
        image = np.ones((256, 256, 3), dtype=np.uint8) * 240  # Light background
        
        # Draw head outline (circle)
        cv2.circle(image, (128, 128), 100, (220, 220, 220), -1)
        cv2.circle(image, (128, 128), 100, (200, 200, 200), 2)
        
        # Draw eyes
        cv2.circle(image, (108, 108), 8, (0, 0, 0), -1)  # Left eye
        cv2.circle(image, (148, 108), 8, (0, 0, 0), -1)  # Right eye
        
        # Draw mouth
        cv2.ellipse(image, (128, 160), (15, 8), 0, 0, 180, (0, 0, 0), 2)
        
        # Draw nose
        cv2.circle(image, (128, 135), 3, (180, 180, 180), -1)
        
        return image
    
    def _create_pointer_wojak(self) -> np.ndarray:
        """Create a pointer Wojak template"""
        image = self._create_basic_wojak().copy()
        
        # Add pointing finger
        # Simple line representing the pointing finger
        cv2.line(image, (200, 140), (230, 120), (220, 180, 150), 8)
        cv2.circle(image, (230, 120), 6, (220, 180, 150), -1)
        
        return image
    
    def _create_doomer(self) -> np.ndarray:
        """Create a doomer template"""
        image = self._create_basic_wojak().copy()
        
        # Make it darker/more depressed looking
        image = cv2.convertScaleAbs(image, alpha=0.8, beta=-20)
        
        # Add dark circles under eyes
        cv2.ellipse(image, (108, 118), (12, 6), 0, 0, 180, (100, 100, 100), -1)
        cv2.ellipse(image, (148, 118), (12, 6), 0, 0, 180, (100, 100, 100), -1)
        
        # Change mouth to frown
        cv2.ellipse(image, (128, 170), (15, 8), 0, 180, 360, (0, 0, 0), 2)
        
        return image
    
    def _create_soyjak(self) -> np.ndarray:
        """Create a soyjak template"""
        image = self._create_basic_wojak().copy()
        
        # Make mouth more open/excited
        cv2.ellipse(image, (128, 165), (20, 15), 0, 0, 180, (0, 0, 0), -1)
        cv2.ellipse(image, (128, 165), (15, 10), 0, 0, 180, (255, 255, 255), -1)
        
        # Make eyes wider
        cv2.circle(image, (108, 108), 10, (255, 255, 255), -1)
        cv2.circle(image, (148, 108), 10, (255, 255, 255), -1)
        cv2.circle(image, (108, 108), 6, (0, 0, 0), -1)
        cv2.circle(image, (148, 108), 6, (0, 0, 0), -1)
        
        return image
    
    def _create_brainlet(self) -> np.ndarray:
        """Create a brainlet template"""
        image = self._create_basic_wojak().copy()
        
        # Make head smaller/more compressed
        # Draw smaller head
        cv2.circle(image, (128, 128), 80, (240, 240, 240), -1)
        cv2.circle(image, (128, 138), 70, (220, 220, 220), -1)
        cv2.circle(image, (128, 138), 70, (200, 200, 200), 2)
        
        # Draw eyes closer together
        cv2.circle(image, (118, 128), 6, (0, 0, 0), -1)
        cv2.circle(image, (138, 128), 6, (0, 0, 0), -1)
        
        # Draw mouth
        cv2.ellipse(image, (128, 160), (10, 5), 0, 0, 180, (0, 0, 0), 2)
        
        return image
    
    def get_template_thumbnail(self, template_name: str, size: int = 150) -> Optional[np.ndarray]:
        """
        Get template thumbnail
        
        Args:
            template_name: Name of the template
            size: Thumbnail size
            
        Returns:
            Thumbnail image or None if not found
        """
        template_image = self.get_template_image(template_name)
        if template_image is None:
            return None
        
        return ImageUtils.create_thumbnail(template_image, size)
    
    def get_all_templates_info(self) -> List[Dict]:
        """
        Get information about all templates
        
        Returns:
            List of template information dictionaries
        """
        templates_info = []
        
        for template_name, template_data in self.templates.items():
            metadata = template_data['metadata']
            
            info = {
                'name': template_name,
                'display_name': metadata.get('name', template_name),
                'description': metadata.get('description', ''),
                'thumbnail': ImageUtils.image_to_base64(
                    self.get_template_thumbnail(template_name), 'PNG'
                )
            }
            templates_info.append(info)
        
        return templates_info
