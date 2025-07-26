import os
import shutil
import tempfile
import uuid
from typing import List, Optional
from pathlib import Path


class FileUtils:
    """Utility functions for file operations"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def is_valid_image_file(filename: str) -> bool:
        """
        Check if filename has valid image extension
        
        Args:
            filename: Name of the file
            
        Returns:
            True if valid image file, False otherwise
        """
        if not filename:
            return False
        
        extension = Path(filename).suffix.lower()
        return extension in FileUtils.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_path: str) -> bool:
        """
        Validate file size
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file size is acceptable, False otherwise
        """
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= FileUtils.MAX_FILE_SIZE
        except OSError:
            return False
    
    @staticmethod
    def create_safe_filename(filename: str) -> str:
        """
        Create a safe filename by removing/replacing unsafe characters
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Get file extension
        path = Path(filename)
        name = path.stem
        ext = path.suffix
        
        # Remove unsafe characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        safe_name = ''.join(c for c in name if c in safe_chars)
        
        # Ensure name is not empty
        if not safe_name:
            safe_name = "image"
        
        # Limit length
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        return safe_name + ext
    
    @staticmethod
    def generate_unique_filename(extension: str = '.jpg') -> str:
        """
        Generate a unique filename
        
        Args:
            extension: File extension
            
        Returns:
            Unique filename
        """
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{extension}"
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """
        Ensure directory exists, create if it doesn't
        
        Args:
            directory: Directory path
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    
    @staticmethod
    def get_temp_directory() -> str:
        """
        Get temporary directory for the application
        
        Returns:
            Path to temporary directory
        """
        temp_dir = os.path.join(tempfile.gettempdir(), 'wojak_generator')
        FileUtils.ensure_directory_exists(temp_dir)
        return temp_dir
    
    @staticmethod
    def create_temp_file(extension: str = '.jpg') -> str:
        """
        Create a temporary file
        
        Args:
            extension: File extension
            
        Returns:
            Path to temporary file
        """
        temp_dir = FileUtils.get_temp_directory()
        filename = FileUtils.generate_unique_filename(extension)
        return os.path.join(temp_dir, filename)
    
    @staticmethod
    def cleanup_temp_files(max_age_hours: int = 24):
        """
        Clean up old temporary files
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        import time
        
        temp_dir = FileUtils.get_temp_directory()
        if not os.path.exists(temp_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
        except OSError as e:
            print(f"Error cleaning up temp files: {e}")
    
    @staticmethod
    def safe_delete_file(file_path: str) -> bool:
        """
        Safely delete a file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """
        Copy a file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if copied successfully, False otherwise
        """
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                FileUtils.ensure_directory_exists(dest_dir)
            
            shutil.copy2(source, destination)
            return True
        except (OSError, shutil.Error) as e:
            print(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension from filename
        
        Args:
            filename: Name of the file
            
        Returns:
            File extension (including dot)
        """
        return Path(filename).suffix.lower()
    
    @staticmethod
    def list_template_files(template_dir: str) -> List[str]:
        """
        List all template files in a directory
        
        Args:
            template_dir: Directory containing templates
            
        Returns:
            List of template file paths
        """
        templates = []
        
        if not os.path.exists(template_dir):
            return templates
        
        try:
            for filename in os.listdir(template_dir):
                if FileUtils.is_valid_image_file(filename):
                    file_path = os.path.join(template_dir, filename)
                    templates.append(file_path)
        except OSError as e:
            print(f"Error listing template files: {e}")
        
        return sorted(templates)
    
    @staticmethod
    def get_upload_directory() -> str:
        """
        Get upload directory for user files
        
        Returns:
            Path to upload directory
        """
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        FileUtils.ensure_directory_exists(upload_dir)
        return upload_dir
    
    @staticmethod
    def get_output_directory() -> str:
        """
        Get output directory for generated images
        
        Returns:
            Path to output directory
        """
        output_dir = os.path.join(os.getcwd(), 'output')
        FileUtils.ensure_directory_exists(output_dir)
        return output_dir
