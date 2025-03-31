# Wojak Generator

An AI-based tool that transforms your images into custom Wojak memes.

## Project Description

This application allows users to upload an image containing a face, select a Wojak template (e.g., Pointer Wojak, Doomer, etc.), and generate a customized Wojak that incorporates facial features from the uploaded image. The system uses computer vision and image processing techniques to detect facial features and apply them to the selected Wojak template.

## Directory Structure

```
wojak-generator/
├── .github/
│   └── workflows/
│       └── ci.yml
├── assets/
│   └── templates/
│       ├── pointer_wojak.png
│       ├── doomer.png
│       ├── soyjak.png
│       ├── brainlet.png
│       └── wojak_basic.png
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── face_detection/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   └── landmarks.py
│   ├── image_processing/
│   │   ├── __init__.py
│   │   ├── transform.py
│   │   └── blend.py
│   ├── wojak_generator/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── templates.py
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py
│       └── file_utils.py
├── web/
│   ├── __init__.py
│   ├── app.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── img/
│   │       └── logo.png
│   └── templates/
│       ├── index.html
│       └── result.html
├── tests/
│   ├── __init__.py
│   ├── test_face_detection.py
│   ├── test_image_processing.py
│   └── test_generator.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## Key Components

1. **Face Detection Module**: Detects faces in the input image and extracts facial landmarks
2. **Image Processing Module**: Handles transformations, blending, and manipulations
3. **Wojak Generator Module**: Manages the generation process and template selection
4. **Web Interface**: Provides a user-friendly web application for users to interact with the generator
