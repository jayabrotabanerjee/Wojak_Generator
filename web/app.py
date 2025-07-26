import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wojak_generator.generator import WojakGenerator
from utils.image_utils import ImageUtils
from utils.file_utils import FileUtils

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'wojak-generator-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Wojak generator
generator = WojakGenerator()

# Ensure upload directories exist
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
FileUtils.ensure_directory_exists(UPLOAD_FOLDER)
FileUtils.ensure_directory_exists(OUTPUT_FOLDER)


@app.route('/')
def index():
    """Main page"""
    templates = generator.get_all_templates_info()
    return render_template('index.html', templates=templates)


@app.route('/api/templates')
def get_templates():
    """API endpoint to get available templates"""
    try:
        templates = generator.get_all_templates_info()
        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to upload and validate face image"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not FileUtils.is_valid_image_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload an image file.'
            }), 400
        
        # Read file data
        file_data = file.read()
        
        # Check file size
        if len(file_data) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({
                'success': False,
                'error': 'File too large. Maximum size is 16MB.'
            }), 400
        
        # Load image
        image = ImageUtils.load_image_from_bytes(file_data)
        
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Could not process image. Please try a different file.'
            }), 400
        
        # Validate face image
        validation = generator.validate_face_image(image)
        
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Face validation failed',
                'details': validation['issues']
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        safe_filename = FileUtils.generate_unique_filename(
            FileUtils.get_file_extension(filename)
        )
        
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Create thumbnail for preview
        thumbnail = ImageUtils.create_thumbnail(image, 200)
        thumbnail_base64 = ImageUtils.image_to_base64(thumbnail, 'JPEG', 80)
        
        return jsonify({
            'success': True,
            'file_id': safe_filename,
            'validation': validation,
            'thumbnail': thumbnail_base64,
            'message': 'Image uploaded and validated successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/generate', methods=['POST'])
def generate_wojak():
    """API endpoint to generate Wojak meme"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        file_id = data.get('file_id')
        template_name = data.get('template', 'wojak_basic')
        
        if not file_id:
            return jsonify({
                'success': False,
                'error': 'No file ID provided'
            }), 400
        
        # Load uploaded image
        file_path = os.path.join(UPLOAD_FOLDER, file_id)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Uploaded file not found. Please upload again.'
            }), 400
        
        face_image = ImageUtils.load_image(file_path)
        
        if face_image is None:
            return jsonify({
                'success': False,
                'error': 'Could not load uploaded image'
            }), 400
        
        # Get generation parameters from request
        params = data.get('params', {})
        
        # Generate Wojak
        result = generator.generate_wojak(face_image, template_name, params)
        
        if result is None:
            return jsonify({
                'success': False,
                'error': 'Failed to generate Wojak. Please try a different image or template.'
            }), 500
        
        # Save result
        output_filename = FileUtils.generate_unique_filename('.png')
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        success = ImageUtils.save_image(result, output_path)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to save generated image'
            }), 500
        
        # Convert to base64 for immediate display
        result_base64 = ImageUtils.image_to_base64(result, 'PNG')
        
        # Clean up uploaded file
        FileUtils.safe_delete_file(file_path)
        
        return jsonify({
            'success': True,
            'result_image': result_base64,
            'download_id': output_filename,
            'message': 'Wojak generated successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/download/<download_id>')
def download_result(download_id):
    """API endpoint to download generated image"""
    try:
        # Validate download ID
        safe_filename = secure_filename(download_id)
        file_path = os.path.join(OUTPUT_FOLDER, safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'wojak_{safe_filename}',
            mimetype='image/png'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download error: {str(e)}'
        }), 500


@app.route('/api/template/<template_name>')
def get_template_preview(template_name):
    """API endpoint to get template preview"""
    try:
        preview = generator.preview_template(template_name, 200)
        
        if preview is None:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'preview': preview
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/result')
def result_page():
    """Result page for displaying generated Wojak"""
    return render_template('result.html')


@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# Clean up old files on startup
def cleanup_old_files():
    """Clean up old uploaded and output files"""
    try:
        FileUtils.cleanup_temp_files()
        
        # Clean up uploads older than 1 hour
        import time
        current_time = time.time()
        
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 3600:  # 1 hour
                            FileUtils.safe_delete_file(file_path)
    except Exception as e:
        print(f"Error during cleanup: {e}")


# Run cleanup on startup
cleanup_old_files()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
