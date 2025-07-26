#!/usr/bin/env python3
"""
Script to help add new Wojak templates to the application.

Usage:
    python scripts/add_template.py template_image.png template_name "Template Description"

Example:
    python scripts/add_template.py my_wojak.png my_custom "My Custom Wojak"
"""

import sys
import os
import shutil
from pathlib import Path

def add_template(image_path, template_name, description="Custom Wojak template"):
    """
    Add a new template to the application
    
    Args:
        image_path: Path to the template image file
        template_name: Internal name for the template (used in code)
        description: Human-readable description
    """
    
    # Validate input file
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found")
        return False
    
    # Get file extension
    _, ext = os.path.splitext(image_path)
    if ext.lower() not in ['.png', '.jpg', '.jpeg']:
        print(f"Error: Unsupported file format '{ext}'. Use PNG or JPG.")
        return False
    
    # Create target filename
    target_filename = f"{template_name}.png"
    target_path = os.path.join("assets", "templates", target_filename)
    
    # Ensure templates directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Copy the file
    try:
        shutil.copy2(image_path, target_path)
        print(f"✅ Template added: {target_path}")
    except Exception as e:
        print(f"Error copying file: {e}")
        return False
    
    # Add template info to the templates.py file
    template_info = f'''
    '{template_name}.png': {{
        'name': '{description}',
        'description': '{description}',
        'face_region': (50, 50, 150, 200),  # x, y, width, height
        'eye_positions': [(80, 100), (120, 100)],  # left_eye, right_eye
        'mouth_position': (100, 160)
    }},'''
    
    print(f"✅ Template '{template_name}' added successfully!")
    print(f"📝 Add this to src/wojak_generator/templates.py in the template_info dictionary:")
    print(template_info)
    print(f"🔄 Restart the application to see the new template")
    
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/add_template.py <image_path> <template_name> [description]")
        print("Example: python scripts/add_template.py my_wojak.png my_custom 'My Custom Wojak'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    template_name = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else f"{template_name.replace('_', ' ').title()} Wojak"
    
    add_template(image_path, template_name, description)

if __name__ == "__main__":
    main()
