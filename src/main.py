#!/usr/bin/env python3
"""
Wojak Generator - Main Entry Point

This module provides the main entry point for the Wojak Generator application.
It can be used to run the web application or as a command-line tool.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wojak_generator.generator import WojakGenerator
from utils.image_utils import ImageUtils
from utils.file_utils import FileUtils


def generate_wojak_cli(input_path: str, output_path: str, template_name: str = 'wojak_basic'):
    """
    Generate Wojak meme from command line
    
    Args:
        input_path: Path to input face image
        output_path: Path to save generated Wojak
        template_name: Name of template to use
    """
    # Initialize generator
    generator = WojakGenerator()
    
    # Load input image
    print(f"Loading image from: {input_path}")
    face_image = ImageUtils.load_image(input_path)
    
    if face_image is None:
        print(f"Error: Could not load image from {input_path}")
        return False
    
    # Validate face image
    print("Validating face image...")
    validation = generator.validate_face_image(face_image)
    
    if not validation['valid']:
        print("Error: Face image validation failed:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        return False
    
    print("Face image validation passed!")
    
    # Check template
    available_templates = generator.get_available_templates()
    if template_name not in available_templates:
        print(f"Error: Template '{template_name}' not found.")
        print(f"Available templates: {', '.join(available_templates)}")
        return False
    
    # Generate Wojak
    print(f"Generating Wojak using template: {template_name}")
    result = generator.generate_wojak(face_image, template_name)
    
    if result is None:
        print("Error: Failed to generate Wojak")
        return False
    
    # Save result
    print(f"Saving result to: {output_path}")
    success = ImageUtils.save_image(result, output_path)
    
    if success:
        print("Wojak generated successfully!")
        return True
    else:
        print("Error: Failed to save generated image")
        return False


def list_templates():
    """List all available templates"""
    generator = WojakGenerator()
    templates_info = generator.get_all_templates_info()
    
    print("Available Wojak Templates:")
    print("=" * 40)
    
    for template in templates_info:
        print(f"Name: {template['name']}")
        print(f"Display Name: {template['display_name']}")
        print(f"Description: {template['description']}")
        print("-" * 30)


def run_web_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the web application
    
    Args:
        host: Host address
        port: Port number
        debug: Enable debug mode
    """
    try:
        # Import Flask app
        from web.app import app
        
        print(f"Starting Wojak Generator web server...")
        print(f"Server will be available at http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        app.run(host=host, port=port, debug=debug)
        
    except ImportError:
        print("Error: Web application not available. Please install Flask.")
        return False
    except Exception as e:
        print(f"Error starting web server: {e}")
        return False


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Wojak Generator - Transform your face into a Wojak meme",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py web                                    # Start web server
  python main.py web --port 8080                       # Start web server on port 8080
  python main.py generate face.jpg wojak.png           # Generate with default template
  python main.py generate face.jpg wojak.png --template doomer  # Use specific template
  python main.py list-templates                        # List available templates
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web server command
    web_parser = subparsers.add_parser('web', help='Start web application')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host address (default: 0.0.0.0)')
    web_parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate Wojak from image')
    gen_parser.add_argument('input', help='Input face image path')
    gen_parser.add_argument('output', help='Output Wojak image path')
    gen_parser.add_argument('--template', default='wojak_basic', help='Template name (default: wojak_basic)')
    
    # List templates command
    subparsers.add_parser('list-templates', help='List available templates')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'web':
        success = run_web_server(args.host, args.port, args.debug)
        sys.exit(0 if success else 1)
    
    elif args.command == 'generate':
        # Validate paths
        if not os.path.exists(args.input):
            print(f"Error: Input file does not exist: {args.input}")
            sys.exit(1)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            FileUtils.ensure_directory_exists(output_dir)
        
        success = generate_wojak_cli(args.input, args.output, args.template)
        sys.exit(0 if success else 1)
    
    elif args.command == 'list-templates':
        list_templates()
        sys.exit(0)
    
    else:
        # Default to web server if no command specified
        print("No command specified. Starting web server...")
        success = run_web_server()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
