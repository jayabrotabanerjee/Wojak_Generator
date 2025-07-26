# Adding Wojak Templates

This guide explains how to add new Wojak template images to the application.

## Quick Start

1. **Prepare your image**:
   - Format: PNG or JPG
   - Size: 256x256 pixels (recommended)
   - Content: Clear Wojak face with visible features

2. **Add to templates directory**:
   ```bash
   cp your_wojak_image.png assets/templates/your_template_name.png
   ```

3. **Update template configuration** (optional):
   - Edit `src/wojak_generator/templates.py`
   - Add metadata for your template

4. **Restart the application** to see your new template

## Detailed Instructions

### Step 1: Prepare Your Template Image

Your template image should:
- Be a clear Wojak face drawing
- Have the face centered in the image
- Show clear eyes, nose, and mouth features
- Be at least 256x256 pixels for best quality
- Have a transparent or solid background

### Step 2: Add to Templates Directory

Place your image file in the `assets/templates/` directory:

```
assets/templates/
├── README.md
├── wojak_basic.png          ← Core template
├── pointer_wojak.png        ← Core template  
├── doomer.png              ← Core template
├── soyjak.png              ← Core template
├── brainlet.png            ← Core template
└── your_new_template.png   ← Your new template
```

### Step 3: Update Template Metadata (Optional)

For better integration, add your template info to `src/wojak_generator/templates.py`:

```python
template_info = {
    # ... existing templates ...
    'your_new_template.png': {
        'name': 'Your Template Name',
        'description': 'Description of your template',
        'face_region': (50, 50, 150, 200),  # x, y, width, height
        'eye_positions': [(80, 100), (120, 100)],  # left_eye, right_eye
        'mouth_position': (100, 160)
    },
}
```

### Step 4: Test Your Template

1. Start the application:
   ```bash
   python src/main.py web
   ```

2. Open http://localhost:5000

3. Your new template should appear in the template gallery

## Template Guidelines

### Image Requirements
- **Format**: PNG (preferred) or JPG
- **Size**: 256x256 pixels minimum, 512x512 recommended
- **Style**: Consistent with Wojak art style
- **Background**: Transparent PNG or solid color

### Face Requirements
- **Position**: Face should be centered
- **Features**: Clear eyes, nose, mouth
- **Expression**: Distinct Wojak expression
- **Quality**: High contrast, clean lines

### Naming Convention
- Use descriptive names: `angry_wojak.png`, `happy_wojak.png`
- Use underscores instead of spaces
- Keep names short and memorable

## Using the Helper Script

Use the provided script to add templates easily:

```bash
python scripts/add_template.py path/to/your/image.png template_name "Template Description"
```

Example:
```bash
python scripts/add_template.py ~/my_wojak.png angry_wojak "Angry Wojak"
```

## Troubleshooting

### Template Not Appearing
- Check file format (PNG/JPG only)
- Verify file is in `assets/templates/` directory
- Restart the application
- Check console for error messages

### Poor Generation Quality
- Use higher resolution images (512x512+)
- Ensure clear facial features
- Try PNG format for better quality
- Adjust face_region coordinates in metadata

### Template Loading Errors
- Check file permissions
- Verify image is not corrupted
- Ensure filename has no special characters

## Example Templates

The application includes these core templates:

1. **wojak_basic.png** - Classic neutral Wojak
2. **pointer_wojak.png** - Wojak pointing gesture  
3. **doomer.png** - Depressed/tired Wojak
4. **soyjak.png** - Excited/surprised Wojak
5. **brainlet.png** - Simple/confused Wojak

Use these as reference for style and quality when creating new templates.

## Advanced Configuration

For advanced users, you can customize:

- Face detection regions
- Eye and mouth positions
- Blending parameters
- Custom preprocessing

See `src/wojak_generator/templates.py` for advanced configuration options.
