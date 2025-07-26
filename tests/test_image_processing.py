import unittest
import numpy as np
import cv2
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_processing.transform import ImageTransformer
from image_processing.blend import ImageBlender


class TestImageTransformer(unittest.TestCase):
    """Test cases for ImageTransformer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a simple test image
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # Add some pattern to make transformations visible
        cv2.rectangle(self.test_image, (20, 20), (80, 80), (255, 0, 0), -1)
        cv2.circle(self.test_image, (50, 50), 15, (0, 255, 0), -1)
    
    def test_rotate_image(self):
        """Test image rotation"""
        rotated = ImageTransformer.rotate_image(self.test_image, 45)
        
        self.assertIsInstance(rotated, np.ndarray)
        self.assertEqual(rotated.shape, self.test_image.shape)
        self.assertEqual(rotated.dtype, self.test_image.dtype)
    
    def test_resize_image_maintain_aspect(self):
        """Test image resizing with aspect ratio maintained"""
        target_size = (200, 200)
        resized = ImageTransformer.resize_image(self.test_image, target_size, maintain_aspect=True)
        
        self.assertIsInstance(resized, np.ndarray)
        self.assertEqual(resized.shape[:2], target_size)
        self.assertEqual(resized.shape[2], 3)
    
    def test_resize_image_no_aspect(self):
        """Test image resizing without maintaining aspect ratio"""
        target_size = (150, 200)
        resized = ImageTransformer.resize_image(self.test_image, target_size, maintain_aspect=False)
        
        self.assertIsInstance(resized, np.ndarray)
        self.assertEqual(resized.shape[:2], target_size)
        self.assertEqual(resized.shape[2], 3)
    
    def test_align_face(self):
        """Test face alignment"""
        # Create mock landmarks
        landmarks = {
            'left_eye': [(30, 40), (32, 40), (28, 40)],
            'right_eye': [(70, 40), (72, 40), (68, 40)]
        }
        
        aligned = ImageTransformer.align_face(self.test_image, landmarks, (128, 128))
        
        self.assertIsInstance(aligned, np.ndarray)
        self.assertEqual(aligned.shape[:2], (128, 128))
    
    def test_create_mask(self):
        """Test mask creation"""
        landmarks = {
            'left_eye': [(30, 40), (35, 38), (35, 42), (30, 44), (25, 42), (25, 38)]
        }
        
        mask = ImageTransformer.create_mask(self.test_image, landmarks, 'left_eye')
        
        self.assertIsInstance(mask, np.ndarray)
        self.assertEqual(mask.shape, self.test_image.shape[:2])
        self.assertEqual(mask.dtype, np.uint8)
        
        # Check that mask has some non-zero values
        self.assertGreater(np.sum(mask), 0)
    
    def test_apply_gaussian_blur(self):
        """Test Gaussian blur application"""
        blurred = ImageTransformer.apply_gaussian_blur(self.test_image, kernel_size=15, sigma=5.0)
        
        self.assertIsInstance(blurred, np.ndarray)
        self.assertEqual(blurred.shape, self.test_image.shape)
        self.assertEqual(blurred.dtype, self.test_image.dtype)
    
    def test_adjust_brightness_contrast(self):
        """Test brightness and contrast adjustment"""
        adjusted = ImageTransformer.adjust_brightness_contrast(self.test_image, brightness=10, contrast=1.2)
        
        self.assertIsInstance(adjusted, np.ndarray)
        self.assertEqual(adjusted.shape, self.test_image.shape)
        self.assertEqual(adjusted.dtype, self.test_image.dtype)
    
    def test_match_color_distribution(self):
        """Test color distribution matching"""
        # Create target image with different color distribution
        target_image = np.ones((100, 100, 3), dtype=np.uint8) * 200
        
        matched = ImageTransformer.match_color_distribution(self.test_image, target_image)
        
        self.assertIsInstance(matched, np.ndarray)
        self.assertEqual(matched.shape, self.test_image.shape)
        self.assertEqual(matched.dtype, self.test_image.dtype)


class TestImageBlender(unittest.TestCase):
    """Test cases for ImageBlender class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test images
        self.foreground = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White
        self.background = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Gray
        
        # Create a simple mask
        self.mask = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(self.mask, (50, 50), 30, 255, -1)
    
    def test_alpha_blend(self):
        """Test alpha blending"""
        blended = ImageBlender.alpha_blend(self.foreground, self.background, self.mask, alpha=0.5)
        
        self.assertIsInstance(blended, np.ndarray)
        self.assertEqual(blended.shape, self.background.shape)
        self.assertEqual(blended.dtype, np.uint8)
        
        # Check that blended image is different from both inputs
        self.assertFalse(np.array_equal(blended, self.foreground))
        self.assertFalse(np.array_equal(blended, self.background))
    
    def test_feather_mask(self):
        """Test mask feathering"""
        feathered = ImageBlender.feather_mask(self.mask, feather_amount=10)
        
        self.assertIsInstance(feathered, np.ndarray)
        self.assertEqual(feathered.shape, self.mask.shape)
        self.assertEqual(feathered.dtype, self.mask.dtype)
        
        # Feathered mask should have gradual transitions
        # Check that there are intermediate values between 0 and 255
        unique_values = np.unique(feathered)
        self.assertGreater(len(unique_values), 2)  # More than just 0 and 255
    
    def test_create_gradient_mask(self):
        """Test gradient mask creation"""
        gradient = ImageBlender.create_gradient_mask((100, 100), (50, 50), 40)
        
        self.assertIsInstance(gradient, np.ndarray)
        self.assertEqual(gradient.shape, (100, 100))
        self.assertEqual(gradient.dtype, np.uint8)
        
        # Check that center is brighter than edges
        center_value = gradient[50, 50]
        edge_value = gradient[0, 0]
        self.assertGreater(center_value, edge_value)
    
    def test_blend_facial_features(self):
        """Test facial feature blending"""
        # Create mock landmarks
        landmarks = {
            'left_eye': [(30, 40), (35, 38), (35, 42), (30, 44), (25, 42), (25, 38)],
            'right_eye': [(65, 40), (70, 38), (70, 42), (65, 44), (60, 42), (60, 38)],
            'mouth': [(40, 70), (50, 68), (60, 70), (60, 75), (50, 77), (40, 75)]
        }
        
        # Create face and template images
        face_image = np.ones((100, 100, 3), dtype=np.uint8) * 180
        template_image = np.ones((100, 100, 3), dtype=np.uint8) * 220
        
        blended = ImageBlender.blend_facial_features(face_image, template_image, landmarks)
        
        self.assertIsInstance(blended, np.ndarray)
        self.assertEqual(blended.shape, template_image.shape)
        self.assertEqual(blended.dtype, template_image.dtype)
    
    def test_enhance_contrast_selective(self):
        """Test selective contrast enhancement"""
        enhanced = ImageBlender.enhance_contrast_selective(self.background, self.mask, factor=1.5)
        
        self.assertIsInstance(enhanced, np.ndarray)
        self.assertEqual(enhanced.shape, self.background.shape)
        self.assertEqual(enhanced.dtype, self.background.dtype)


if __name__ == '__main__':
    unittest.main()
