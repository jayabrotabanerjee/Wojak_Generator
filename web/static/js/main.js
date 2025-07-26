// Wojak Generator - Main JavaScript Application

class WojakGenerator {
    constructor() {
        this.currentStep = 1;
        this.uploadedFileId = null;
        this.selectedTemplate = 'wojak_basic';
        this.templates = [];
        this.generationParams = {
            face_blend_strength: 0.6,
            eye_blend_strength: 0.8,
            mouth_blend_strength: 0.7,
            nose_blend_strength: 0.3,
            color_match_strength: 0.4,
            contrast_enhancement: 1.1
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTemplates();
        this.setupDragAndDrop();
        this.setupRangeInputs();
    }

    setupEventListeners() {
        // File input
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));

        // Change image button
        document.getElementById('changeImageBtn').addEventListener('click', () => {
            this.resetToUpload();
        });

        // Generate button
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateWojak();
        });

        // Result actions
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadResult();
        });

        document.getElementById('newWojakBtn').addEventListener('click', () => {
            this.resetToUpload();
        });

        document.getElementById('shareBtn').addEventListener('click', () => {
            this.shareResult();
        });

        // Error close
        document.getElementById('errorClose').addEventListener('click', () => {
            this.hideError();
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    setupRangeInputs() {
        const ranges = [
            'faceBlendStrength',
            'eyeBlendStrength', 
            'mouthBlendStrength',
            'colorMatchStrength'
        ];

        ranges.forEach(id => {
            const input = document.getElementById(id);
            const valueSpan = input.nextElementSibling;
            
            input.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                valueSpan.textContent = value.toFixed(1);
                
                // Update generation parameters
                const paramName = id.replace(/([A-Z])/g, '_$1').toLowerCase();
                this.generationParams[paramName] = value;
            });
        });
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            const data = await response.json();
            
            if (data.success) {
                this.templates = data.templates;
                this.renderTemplates();
            } else {
                this.showError('Failed to load templates');
            }
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Failed to load templates');
        }
    }

    renderTemplates() {
        const grid = document.getElementById('templateGrid');
        grid.innerHTML = '';

        this.templates.forEach(template => {
            const card = document.createElement('div');
            card.className = 'template-card';
            card.dataset.template = template.name;
            
            if (template.name === this.selectedTemplate) {
                card.classList.add('selected');
            }

            card.innerHTML = `
                <img src="${template.thumbnail}" alt="${template.display_name}" class="template-image">
                <div class="template-name">${template.display_name}</div>
                <div class="template-description">${template.description}</div>
            `;

            card.addEventListener('click', () => {
                this.selectTemplate(template.name);
            });

            grid.appendChild(card);
        });
    }

    selectTemplate(templateName) {
        this.selectedTemplate = templateName;
        
        // Update UI
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        document.querySelector(`[data-template="${templateName}"]`).classList.add('selected');
        
        // Show customize section
        this.showStep(3);
    }

    async handleFileSelect(file) {
        if (!file) return;

        // Validate file
        if (!this.isValidImageFile(file)) {
            this.showError('Please select a valid image file (JPG, PNG, GIF)');
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            this.showError('File too large. Maximum size is 16MB.');
            return;
        }

        // Show loading
        this.showLoading('Uploading and processing image...');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.uploadedFileId = data.file_id;
                this.showUploadPreview(data.thumbnail, data.validation);
                this.showStep(2);
            } else {
                this.showError(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Upload failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
        return validTypes.includes(file.type);
    }

    showUploadPreview(thumbnail, validation) {
        const preview = document.getElementById('uploadPreview');
        const image = document.getElementById('previewImage');
        const status = document.getElementById('previewStatus');

        image.src = thumbnail;
        
        if (validation.valid) {
            status.textContent = `✓ Face detected successfully! Quality: ${validation.image_quality}`;
            status.className = 'preview-status success';
        } else {
            status.textContent = `⚠ Issues found: ${validation.issues.join(', ')}`;
            status.className = 'preview-status error';
        }

        preview.style.display = 'block';
    }

    async generateWojak() {
        if (!this.uploadedFileId) {
            this.showError('Please upload an image first');
            return;
        }

        this.showLoading('Generating your Wojak...');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: this.uploadedFileId,
                    template: this.selectedTemplate,
                    params: this.generationParams
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showResult(data.result_image, data.download_id);
                this.showStep(4);
                
                // Store result for sharing
                this.downloadId = data.download_id;
                localStorage.setItem('wojakResult', data.result_image);
                localStorage.setItem('wojakDownloadId', data.download_id);
            } else {
                this.showError(data.error || 'Generation failed');
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showError('Generation failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showResult(imageBase64, downloadId) {
        const resultImage = document.getElementById('resultImage');
        resultImage.src = imageBase64;
        this.downloadId = downloadId;
    }

    downloadResult() {
        if (this.downloadId) {
            window.open(`/api/download/${this.downloadId}`, '_blank');
        }
    }

    shareResult() {
        if (navigator.share) {
            navigator.share({
                title: 'Check out my Wojak!',
                text: 'I just created this awesome Wojak meme!',
                url: window.location.href
            });
        } else {
            // Fallback: copy URL
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.showNotification('Link copied to clipboard!');
            });
        }
    }

    showStep(stepNumber) {
        // Hide all sections
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('templateSection').style.display = 'none';
        document.getElementById('customizeSection').style.display = 'none';
        document.getElementById('resultSection').style.display = 'none';

        // Show target section
        let sectionId;
        switch (stepNumber) {
            case 1:
                sectionId = 'uploadSection';
                break;
            case 2:
                sectionId = 'templateSection';
                break;
            case 3:
                sectionId = 'customizeSection';
                break;
            case 4:
                sectionId = 'resultSection';
                break;
        }

        if (sectionId) {
            const section = document.getElementById(sectionId);
            section.style.display = 'block';
            section.classList.add('section-enter');
            
            // Remove animation class after animation completes
            setTimeout(() => {
                section.classList.remove('section-enter');
            }, 500);
        }

        this.currentStep = stepNumber;
    }

    resetToUpload() {
        this.uploadedFileId = null;
        this.downloadId = null;
        this.selectedTemplate = 'wojak_basic';
        
        // Reset file input
        document.getElementById('fileInput').value = '';
        
        // Hide preview
        document.getElementById('uploadPreview').style.display = 'none';
        
        // Reset template selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset range inputs to defaults
        document.getElementById('faceBlendStrength').value = 0.6;
        document.getElementById('eyeBlendStrength').value = 0.8;
        document.getElementById('mouthBlendStrength').value = 0.7;
        document.getElementById('colorMatchStrength').value = 0.4;
        
        // Update display values
        document.querySelectorAll('.range-value').forEach((span, index) => {
            const values = [0.6, 0.8, 0.7, 0.4];
            span.textContent = values[index];
        });
        
        // Reset generation params
        this.generationParams = {
            face_blend_strength: 0.6,
            eye_blend_strength: 0.8,
            mouth_blend_strength: 0.7,
            nose_blend_strength: 0.3,
            color_match_strength: 0.4,
            contrast_enhancement: 1.1
        };
        
        // Show upload step
        this.showStep(1);
    }

    showLoading(message) {
        const overlay = document.getElementById('loadingOverlay');
        const text = document.getElementById('loadingText');
        text.textContent = message;
        overlay.style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        errorText.textContent = message;
        errorDiv.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }

    showNotification(message) {
        // Simple notification - could be enhanced with a proper notification system
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 1002;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WojakGenerator();
});

// Service Worker registration (optional, for offline functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
