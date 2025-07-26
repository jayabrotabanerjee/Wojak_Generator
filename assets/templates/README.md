# Wojak Templates

This directory contains the Wojak template images that will be used for face generation.

## How to Add Templates

1. **Image Format**: Add PNG or JPG files
2. **Image Size**: Recommended 256x256 pixels or larger
3. **File Naming**: Use descriptive names (e.g., `wojak_basic.png`, `doomer.png`)
4. **Image Quality**: High quality images work best for face blending

## Expected Template Files:

### Core Templates:
- `wojak_basic.png` - Classic Wojak face
- `pointer_wojak.png` - Wojak pointing with finger
- `doomer.png` - Depressed night-walking Wojak
- `soyjak.png` - Soy-consuming variant
- `brainlet.png` - Low IQ Wojak variant

### Custom Templates:
You can add any additional Wojak variants by placing PNG/JPG files in this directory.

## Template Requirements:

- **Face Position**: The face should be centered in the image
- **Clear Features**: Eyes, nose, and mouth should be clearly visible
- **Consistent Style**: Maintain the Wojak art style
- **Background**: Transparent or solid background works best

## How Templates Are Used:

1. The `TemplateManager` class automatically scans this directory
2. Images are loaded and processed for face generation
3. If templates are missing, the application will generate basic SVG versions
4. Templates appear in the web interface template gallery

## Adding New Templates:

1. Place your PNG/JPG files in this directory
2. Restart the application
3. The new templates will appear in the template selection gallery
4. Update the template metadata in `src/wojak_generator/templates.py` if needed

## File Structure:
```
assets/templates/
├── README.md (this file)
├── wojak_basic.png
├── pointer_wojak.png
├── doomer.png
├── soyjak.png
├── brainlet.png
└── [your-custom-templates].png
```
