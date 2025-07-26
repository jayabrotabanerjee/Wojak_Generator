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
        // Use hardcoded templates for static demo
        this.templates = [
            {
                name: 'wojak_basic',
                display_name: 'Basic Wojak',
                description: 'Classic Wojak face',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y0ZjRmNCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+QmFzaWMgV29qYWs8L3RleHQ+PC9zdmc+'
            },
            {
                name: 'pointer_wojak',
                display_name: 'Pointer Wojak',
                description: 'Wojak pointing with finger',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y0ZjRmNCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEwIiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+UG9pbnRlcjwvdGV4dD48L3N2Zz4='
            },
            {
                name: 'doomer',
                display_name: 'Doomer',
                description: 'Depressed night-walking Wojak',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMzMzMyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+RG9vbWVyPC90ZXh0Pjwvc3ZnPg=='
            },
            {
                name: 'soyjak',
                display_name: 'Soyjak',
                description: 'Soy-consuming variant',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2ZmZmJkYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U295amFrPC90ZXh0Pjwvc3ZnPg=='
            },
            {
                name: 'brainlet',
                display_name: 'Brainlet',
                description: 'Low IQ Wojak variant',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2ZmZWVlZSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEwIiBmaWxsPSIjNjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+QnJhaW5sZXQ8L3RleHQ+PC9zdmc+'
            }
        ];
        this.renderTemplates();
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
        this.showLoading('Processing image...');

        // Simulate processing delay
        setTimeout(() => {
            try {
                // Create file ID and thumbnail for demo
                this.uploadedFileId = `demo_${Date.now()}`;
                const mockThumbnail = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2U4ZjVlOCIvPjx0ZXh0IHg9IjEwMCIgeT0iMTAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM0Yjc0NTciIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7inJMgRmFjZSBEZXRlY3RlZDwvdGV4dD48L3N2Zz4=';
                const mockValidation = {
                    valid: true,
                    face_detected: true,
                    landmarks_detected: true,
                    image_quality: 'high',
                    issues: []
                };

                this.showUploadPreview(mockThumbnail, mockValidation);
                this.showStep(2);
            } catch (error) {
                console.error('Processing error:', error);
                this.showError('Processing failed. Please try again.');
            } finally {
                this.hideLoading();
            }
        }, 1500);
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

        // Simulate processing delay
        setTimeout(() => {
            try {
                // Generate mock result based on selected template
                let mockResult;
                switch (this.selectedTemplate) {
                    case 'doomer':
                        mockResult = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9ImEiIGN4PSI1MCUiIGN5PSI1MCUiIHI9IjUwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzMzMyIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzExMSIvPjwvcmFkaWFsR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiBmaWxsPSJ1cmwoI2EpIi8+PGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI4MCIgZmlsbD0iIzU1NSIgc3Ryb2tlPSIjNzc3IiBzdHJva2Utd2lkdGg9IjIiLz48Y2lyY2xlIGN4PSIxMDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48Y2lyY2xlIGN4PSIxNDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48ZWxsaXBzZSBjeD0iMTI4IiBjeT0iMTcwIiByeD0iMTUiIHJ5PSI4IiBmaWxsPSIjMDAwIiB0cmFuc2Zvcm09InJvdGF0ZSgxODAgMTI4IDE3MCkiLz48dGV4dCB4PSIxMjgiIHk9IjIxMCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjYWFhIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5Eb29tZXIgV29qYWs8L3RleHQ+PC9zdmc+';
                        break;
                    case 'soyjak':
                        mockResult = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9ImEiIGN4PSI1MCUiIGN5PSI1MCUiIHI9IjUwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2ZmZmJkYyIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI2ZmZTdiYSIvPjwvcmFkaWFsR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiBmaWxsPSJ1cmwoI2EpIi8+PGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI4MCIgZmlsbD0iI2ZmZWJjYyIgc3Ryb2tlPSIjZmZkNzAwIiBzdHJva2Utd2lkdGg9IjIiLz48Y2lyY2xlIGN4PSIxMDgiIGN5PSIxMDgiIHI9IjEwIiBmaWxsPSIjZmZmIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPjxjaXJjbGUgY3g9IjEwOCIgY3k9IjEwOCIgcj0iNiIgZmlsbD0iIzAwMCIvPjxjaXJjbGUgY3g9IjE0OCIgY3k9IjEwOCIgcj0iMTAiIGZpbGw9IiNmZmYiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMTQ4IiBjeT0iMTA4IiByPSI2IiBmaWxsPSIjMDAwIi8+PGVsbGlwc2UgY3g9IjEyOCIgY3k9IjE2NSIgcng9IjIwIiByeT0iMTUiIGZpbGw9IiMwMDAiLz48ZWxsaXBzZSBjeD0iMTI4IiBjeT0iMTY1IiByeD0iMTUiIHJ5PSIxMCIgZmlsbD0iI2ZmZiIvPjx0ZXh0IHg9IjEyOCIgeT0iMjEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPlNveWphayBXb2phayE8L3RleHQ+PC9zdmc+';
                        break;
                    case 'brainlet':
                        mockResult = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9ImEiIGN4PSI1MCUiIGN5PSI1MCUiIHI9IjUwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2ZmZWVlZSIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI2VlZGRkZCIvPjwvcmFkaWFsR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiBmaWxsPSJ1cmwoI2EpIi8+PGVsbGlwc2UgY3g9IjEyOCIgY3k9IjE0MCIgcng9IjcwIiByeT0iNjAiIGZpbGw9IiNmZGMiIHN0cm9rZT0iI2NjYyIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMTE4IiBjeT0iMTMwIiByPSI2IiBmaWxsPSIjMDAwIi8+PGNpcmNsZSBjeD0iMTM4IiBjeT0iMTMwIiByPSI2IiBmaWxsPSIjMDAwIi8+PGVsbGlwc2UgY3g9IjEyOCIgY3k9IjE2MCIgcng9IjEwIiByeT0iNSIgZmlsbD0iIzAwMCIvPjx0ZXh0IHg9IjEyOCIgeT0iMjEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkJyYWlubGV0IFdvamFrPC90ZXh0Pjwvc3ZnPg==';
                        break;
                    case 'pointer_wojak':
                        mockResult = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9ImEiIGN4PSI1MCUiIGN5PSI1MCUiIHI9IjUwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2ZmZiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI2VlZSIvPjwvcmFkaWFsR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiBmaWxsPSJ1cmwoI2EpIi8+PGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI4MCIgZmlsbD0iI2ZkYyIgc3Ryb2tlPSIjY2NjIiBzdHJva2Utd2lkdGg9IjIiLz48Y2lyY2xlIGN4PSIxMDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48Y2lyY2xlIGN4PSIxNDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48ZWxsaXBzZSBjeD0iMTI4IiBjeT0iMTYwIiByeD0iMTUiIHJ5PSI4IiBmaWxsPSIjMDAwIi8+PGxpbmUgeDE9IjIwMCIgeTE9IjE0MCIgeDI9IjIzMCIgeTI9IjEyMCIgc3Ryb2tlPSIjZGNiYTk2IiBzdHJva2Utd2lkdGg9IjgiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxjaXJjbGUgY3g9IjIzMCIgY3k9IjEyMCIgcj0iNiIgZmlsbD0iI2RjYmE5NiIvPjx0ZXh0IHg9IjEyOCIgeT0iMjEwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPlBvaW50ZXIgV29qYWshPC90ZXh0Pjwvc3ZnPg==';
                        break;
                    default:
                        mockResult = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9ImEiIGN4PSI1MCUiIGN5PSI1MCUiIHI9IjUwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI2ZmZiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI2VlZSIvPjwvcmFkaWFsR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2IiBmaWxsPSJ1cmwoI2EpIi8+PGNpcmNsZSBjeD0iMTI4IiBjeT0iMTI4IiByPSI4MCIgZmlsbD0iI2ZkYyIgc3Ryb2tlPSIjY2NjIiBzdHJva2Utd2lkdGg9IjIiLz48Y2lyY2xlIGN4PSIxMDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48Y2lyY2xlIGN4PSIxNDgiIGN5PSIxMDgiIHI9IjgiIGZpbGw9IiMwMDAiLz48ZWxsaXBzZSBjeD0iMTI4IiBjeT0iMTYwIiByeD0iMTUiIHJ5PSI4IiBmaWxsPSIjMDAwIi8+PHRleHQgeD0iMTI4IiB5PSIyMTAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzY2NiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+QmFzaWMgV29qYWshPC90ZXh0Pjwvc3ZnPg==';
                }

                const downloadId = `generated_${this.selectedTemplate}_${Date.now()}.png`;

                this.showResult(mockResult, downloadId);
                this.showStep(4);

                // Store result for sharing
                this.downloadId = downloadId;
                localStorage.setItem('wojakResult', mockResult);
                localStorage.setItem('wojakDownloadId', downloadId);
            } catch (error) {
                console.error('Generation error:', error);
                this.showError('Generation failed. Please try again.');
            } finally {
                this.hideLoading();
            }
        }, 2000);
    }

    showResult(imageBase64, downloadId) {
        const resultImage = document.getElementById('resultImage');
        resultImage.src = imageBase64;
        this.downloadId = downloadId;
    }

    downloadResult() {
        if (this.downloadId) {
            // Create a download link for the generated image
            const resultImage = document.getElementById('resultImage');
            if (resultImage && resultImage.src) {
                const link = document.createElement('a');
                link.download = this.downloadId;
                link.href = resultImage.src;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
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
