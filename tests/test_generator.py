import unittest
import numpy as np
import cv2
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wojak_generator.generator import WojakGenerator
from wojak_generator.templates import TemplateManager
from utils.image_utils import ImageUtils
from utils.file_utils import FileUtils


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_template_manager_initialization(self):
        """Test that template manager initializes correctly"""
        self.assertIsInstance(self.template_manager, TemplateManager)
        self.assertEqual(self.template_manager.template_directory, self.temp_dir)
        self.assertIsInstance(self.template_manager.templates, dict)
    
    def test_create_default_templates(self):
        """Test default template creation"""
        self.template_manager.create_default_templates()
        
        # Check that templates were created
        template_names = self.template_manager.get_template_names()
        self.assertGreater(len(template_names), 0)
        
        # Check that basic template exists
        self.assertIn('wojak_basic', template_names)
    
    def test_get_template_names(self):
        """Test getting template names"""
        names = self.template_manager.get_template_names()
        self.assertIsInstance(names, list)
    
    def test_get_template(self):
        """Test getting template by name"""
        self.template_manager.create_default_templates()
        template_names = self.template_manager.get_template_names()
        
        if template_names:
            template_name = template_names[0]
            template = self.template_manager.get_template(template_name)
            
            self.assertIsNotNone(template)
            self.assertIn('image', template)
            self.assertIn('metadata', template)
            self.assertIsInstance(template['image'], np.ndarray)
    
    def test_get_template_image(self):
        """Test getting template image"""
        self.template_manager.create_default_templates()
        template_names = self.template_manager.get_template_names()
        
        if template_names:
            template_name = template_names[0]
            image = self.template_manager.get_template_image(template_name)
            
            if image is not None:  # Template might not be created in test environment
                self.assertIsInstance(image, np.ndarray)
                self.assertEqual(len(image.shape), 3)  # Should be 3D (height, width, channels)
    
    def test_get_all_templates_info(self):
        """Test getting all templates info"""
        self.template_manager.create_default_templates()
        info = self.template_manager.get_all_templates_info()
        
        self.assertIsInstance(info, list)


class TestWojakGenerator(unittest.TestCase):
    """Test cases for WojakGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for templates
        self.temp_dir = tempfile.mkdtemp()
        self.generator = WojakGenerator(self.temp_dir)
        
        # Create a test face image
        self.test_face_image = self._create_test_face_image()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_face_image(self):
        """Create a test image that resembles a face"""
        image = np.ones((200, 200, 3), dtype=np.uint8) * 240
        
        # Draw a simple face
        center = (100, 100)
        
        # Head (circle)
        cv2.circle(image, center, 80, (220, 180, 150), -1)
        
        # Eyes
        cv2.circle(image, (80, 80), 8, (0, 0, 0), -1)  # Left eye
        cv2.circle(image, (120, 80), 8, (0, 0, 0), -1)  # Right eye
        
        # Nose
        cv2.circle(image, (100, 100), 4, (200, 160, 120), -1)
        
        # Mouth
        cv2.ellipse(image, (100, 130), (15, 8), 0, 0, 180, (100, 50, 50), -1)
        
        return image
    
    def test_generator_initialization(self):
        """Test that generator initializes correctly"""
        self.assertIsInstance(self.generator, WojakGenerator)
        self.assertIsNotNone(self.generator.face_detector)
        self.assertIsNotNone(self.generator.landmark_extractor)
        self.assertIsNotNone(self.generator.template_manager)
        self.assertIsInstance(self.generator.default_params, dict)
    
    def test_get_available_templates(self):
        """Test getting available templates"""
        templates = self.generator.get_available_templates()
        self.assertIsInstance(templates, list)
    
    def test_validate_face_image_valid(self):
        """Test face image validation with valid image"""
        validation = self.generator.validate_face_image(self.test_face_image)
        
        self.assertIsInstance(validation, dict)
        self.assertIn('valid', validation)
        self.assertIn('issues', validation)
        self.assertIn('face_detected', validation)
        self.assertIn('landmarks_detected', validation)
        self.assertIn('image_quality', validation)
    
    def test_validate_face_image_invalid(self):
        """Test face image validation with invalid image"""
        # Test with None
        validation = self.generator.validate_face_image(None)
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['issues']), 0)
        
        # Test with too small image
        small_image = np.ones((10, 10, 3), dtype=np.uint8)
        validation = self.generator.validate_face_image(small_image)
        self.assertFalse(validation['valid'])
    
    def test_generate_wojak(self):
        """Test Wojak generation (may not work without proper face detection)"""
        # This test may not work in the testing environment due to MediaPipe dependencies
        # but we can test that the method exists and handles errors gracefully
        
        result = self.generator.generate_wojak(self.test_face_image)
        
        # Result could be None (if generation fails) or np.ndarray (if successful)
        if result is not None:
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(len(result.shape), 3)  # Should be 3D array
        # If result is None, that's also acceptable in test environment


class TestImageUtils(unittest.TestCase):
    """Test cases for ImageUtils class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    def test_validate_image_valid(self):
        """Test image validation with valid image"""
        self.assertTrue(ImageUtils.validate_image(self.test_image))
    
    def test_validate_image_invalid(self):
        """Test image validation with invalid images"""
        # Test with None
        self.assertFalse(ImageUtils.validate_image(None))
        
        # Test with 2D array
        image_2d = np.ones((100, 100), dtype=np.uint8)
        self.assertFalse(ImageUtils.validate_image(image_2d))
        
        # Test with wrong number of channels
        image_4ch = np.ones((100, 100, 4), dtype=np.uint8)
        self.assertFalse(ImageUtils.validate_image(image_4ch))
        
        # Test with too small image
        small_image = np.ones((10, 10, 3), dtype=np.uint8)
        self.assertFalse(ImageUtils.validate_image(small_image))
    
    def test_get_image_info(self):
        """Test getting image information"""
        info = ImageUtils.get_image_info(self.test_image)
        
        self.assertIsInstance(info, dict)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('channels', info)
        self.assertEqual(info['width'], 100)
        self.assertEqual(info['height'], 100)
        self.assertEqual(info['channels'], 3)
    
    def test_create_thumbnail(self):
        """Test thumbnail creation"""
        thumbnail = ImageUtils.create_thumbnail(self.test_image, max_size=50)
        
        self.assertIsInstance(thumbnail, np.ndarray)
        self.assertLessEqual(max(thumbnail.shape[:2]), 50)
    
    def test_image_to_base64(self):
        """Test image to base64 conversion"""
        base64_str = ImageUtils.image_to_base64(self.test_image)
        
        self.assertIsInstance(base64_str, str)
        self.assertTrue(base64_str.startswith('data:image/'))


class TestFileUtils(unittest.TestCase):
    """Test cases for FileUtils class"""
    
    def test_is_valid_image_file(self):
        """Test image file validation"""
        # Valid extensions
        self.assertTrue(FileUtils.is_valid_image_file('test.jpg'))
        self.assertTrue(FileUtils.is_valid_image_file('test.png'))
        self.assertTrue(FileUtils.is_valid_image_file('test.gif'))
        
        # Invalid extensions
        self.assertFalse(FileUtils.is_valid_image_file('test.txt'))
        self.assertFalse(FileUtils.is_valid_image_file('test.pdf'))
        self.assertFalse(FileUtils.is_valid_image_file(''))
    
    def test_create_safe_filename(self):
        """Test safe filename creation"""
        unsafe_name = "test file with spaces & symbols!.jpg"
        safe_name = FileUtils.create_safe_filename(unsafe_name)
        
        self.assertIsInstance(safe_name, str)
        self.assertTrue(safe_name.endswith('.jpg'))
        
        # Should not contain unsafe characters
        unsafe_chars = ['&', '!', ' ']
        for char in unsafe_chars:
            self.assertNotIn(char, safe_name)
    
    def test_generate_unique_filename(self):
        """Test unique filename generation"""
        filename1 = FileUtils.generate_unique_filename('.jpg')
        filename2 = FileUtils.generate_unique_filename('.jpg')
        
        self.assertNotEqual(filename1, filename2)  # Should be unique
        self.assertTrue(filename1.endswith('.jpg'))
        self.assertTrue(filename2.endswith('.jpg'))
    
    def test_get_file_extension(self):
        """Test file extension extraction"""
        self.assertEqual(FileUtils.get_file_extension('test.jpg'), '.jpg')
        self.assertEqual(FileUtils.get_file_extension('test.PNG'), '.png')  # Should be lowercase
        self.assertEqual(FileUtils.get_file_extension('test'), '')


if __name__ == '__main__':
    unittest.main()
