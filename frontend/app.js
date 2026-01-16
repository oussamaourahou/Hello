// API Base URL - use relative path for deployment
const API_BASE = window.location.origin;

// Global state
let uploadedPhoto = null;
let uploadedMenuFile = null;

// Menu Items Management
function addMenuItem() {
    const input = document.getElementById('newItemInput');
    const itemName = input.value.trim();

    if (!itemName) {
        alert('Please enter an item name');
        return;
    }

    const menuList = document.getElementById('menuItemsList');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'menu-item';
    itemDiv.innerHTML = `
        <span>${itemName}</span>
        <button onclick="removeMenuItem(this)" class="btn-remove">×</button>
    `;

    menuList.appendChild(itemDiv);
    input.value = '';
}

function removeMenuItem(button) {
    button.parentElement.remove();
}

function getMenuItems() {
    const menuList = document.getElementById('menuItemsList');
    const items = [];
    menuList.querySelectorAll('.menu-item span').forEach(span => {
        items.push(span.textContent.trim());
    });
    return items;
}

// Photo Upload
function handlePhotoSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    uploadedPhoto = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewDiv = document.getElementById('photoPreview');
        const previewImg = document.getElementById('previewImg');
        const placeholder = document.querySelector('.upload-placeholder');

        previewImg.src = e.target.result;
        previewDiv.style.display = 'block';
        placeholder.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Menu File Upload (Stage 1)
function handleMenuFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    uploadedMenuFile = file;

    // Show file info
    const placeholder = document.getElementById('menuUploadPlaceholder');
    const fileInfo = document.getElementById('menuFileInfo');
    const fileName = document.getElementById('menuFileName');
    const extractBtn = document.getElementById('extractMenuBtn');

    fileName.textContent = file.name;
    placeholder.style.display = 'none';
    fileInfo.style.display = 'flex';
    extractBtn.style.display = 'block';
}

function clearMenuFile() {
    uploadedMenuFile = null;
    document.getElementById('menuFileInput').value = '';
    document.getElementById('menuUploadPlaceholder').style.display = 'block';
    document.getElementById('menuFileInfo').style.display = 'none';
    document.getElementById('extractMenuBtn').style.display = 'none';
}

// Stage 1: Extract Menu
async function extractMenu() {
    if (!uploadedMenuFile) {
        alert('Please upload a menu file first');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('menu_file', uploadedMenuFile);

        const response = await fetch(`${API_BASE}/api/stage1/extract`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to extract menu');
        }

        const result = await response.json();

        // Clear existing menu items
        const menuList = document.getElementById('menuItemsList');
        menuList.innerHTML = '';

        // Add extracted items to the menu list
        result.menu_items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'menu-item';
            itemDiv.innerHTML = `
                <span>${item}</span>
                <button onclick="removeMenuItem(this)" class="btn-remove">×</button>
            `;
            menuList.appendChild(itemDiv);
        });

        // Display extraction results
        const html = `
            <div class="result-card">
                <h4>Stage 1: Menu Extraction</h4>

                <div class="result-item">
                    <span class="result-label">Items Extracted:</span>
                    <span class="result-value quality-ready"><strong>${result.total_items} items</strong></span>
                </div>

                <div class="result-item">
                    <span class="result-label">Extraction Notes:</span>
                    <span class="result-value">${result.extraction_notes}</span>
                </div>

                <div class="result-item">
                    <span class="result-label">Menu Items:</span>
                    <div class="extracted-items">
                        ${result.menu_items.map(item => `<div class="extracted-item">${item}</div>`).join('')}
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-value quality-ready">✓ Menu items have been added to your list!</span>
                </div>
            </div>
        `;

        displayResults(html);

        // Clear the uploaded menu file
        clearMenuFile();

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Allow Enter key to add items
document.getElementById('newItemInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addMenuItem();
    }
});

// Show/Hide Loading
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsContent').innerHTML = '';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

// Display Results
function displayResults(html) {
    hideLoading();
    document.getElementById('resultsContent').innerHTML = html;
}

// Stage 2: Match Photo to Menu
async function runStage2() {
    if (!uploadedPhoto) {
        alert('Please upload a photo first');
        return;
    }

    const menuItems = getMenuItems();
    if (menuItems.length === 0) {
        alert('Please add at least one menu item');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('photo', uploadedPhoto);
        formData.append('menu_items', JSON.stringify(menuItems));

        const response = await fetch(`${API_BASE}/api/stage2/match`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to process photo');
        }

        const result = await response.json();

        // Display results
        const confidenceClass = result.confidence >= 75 ? 'confidence-high' :
                               result.confidence >= 50 ? 'confidence-medium' : 'confidence-low';

        const html = `
            <div class="result-card">
                <h4>Stage 2: Photo-to-Item Matching</h4>

                <div class="result-item">
                    <span class="result-label">Dish Identified:</span>
                    <span class="result-value">${result.dish_identified}</span>
                </div>

                <div class="result-item">
                    <span class="result-label">Matched Menu Item:</span>
                    <span class="result-value"><strong>${result.matched_item}</strong></span>
                </div>

                <div class="result-item">
                    <span class="result-label">Confidence Score:</span>
                    <span class="result-value ${confidenceClass}">${result.confidence}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.confidence}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Description:</span>
                    <span class="result-value">${result.description}</span>
                </div>

                <div class="result-item">
                    <span class="result-label">Reasoning:</span>
                    <span class="result-value">${result.reasoning}</span>
                </div>
            </div>
        `;

        displayResults(html);

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Stage 3: Assess Photo Quality
async function runStage3() {
    if (!uploadedPhoto) {
        alert('Please upload a photo first');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('photo', uploadedPhoto);

        const response = await fetch(`${API_BASE}/api/stage3/assess`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to assess photo');
        }

        const result = await response.json();

        // Display results
        const qualityClass = result.overall_quality === 'Ready' ? 'quality-ready' :
                            result.overall_quality === 'Needs Enhancement' ? 'quality-enhance' : 'quality-reject';

        const html = `
            <div class="result-card">
                <h4>Stage 3: Photo Quality Assessment</h4>

                <div class="result-item">
                    <span class="result-label">Overall Quality:</span>
                    <span class="result-value ${qualityClass}">${result.overall_quality}</span>
                </div>

                <div class="result-item">
                    <span class="result-label">Overall Score:</span>
                    <span class="result-value"><strong>${result.overall_score}%</strong></span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.overall_score}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Resolution:</span>
                    <span class="result-value">${result.resolution_score}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.resolution_score}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Lighting:</span>
                    <span class="result-value">${result.lighting_score}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.lighting_score}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Composition:</span>
                    <span class="result-value">${result.composition_score}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.composition_score}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Presentation:</span>
                    <span class="result-value">${result.presentation_score}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${result.presentation_score}%"></div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Recommendation:</span>
                    <span class="result-value">${result.recommendation}</span>
                </div>
            </div>
        `;

        displayResults(html);

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Stage 4: Enhance Photo with Photoroom
async function runStage4() {
    if (!uploadedPhoto) {
        alert('Please upload a photo first');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('photo', uploadedPhoto);
        formData.append('background_color', 'white');

        const response = await fetch(`${API_BASE}/api/stage4/enhance`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to enhance photo');
        }

        const result = await response.json();

        // Display results with images and download button
        const enhancedFilename = result.enhanced_image_url.split('/').pop();
        const html = `
            <div class="result-card">
                <h4>Stage 4: Photo Enhancement (Photoroom)</h4>

                <div class="result-item">
                    <span class="result-label">Status:</span>
                    <span class="result-value quality-ready">Enhanced Successfully</span>
                </div>

                <div class="result-item">
                    <span class="result-label">Transformations:</span>
                    <span class="result-value">${result.transformations_applied.join(', ')}</span>
                </div>

                <div class="enhanced-images">
                    <div>
                        <img src="${API_BASE}/api/uploads/${uploadedPhoto.name}" alt="Original">
                        <div class="image-label">Original</div>
                    </div>
                    <div>
                        <img src="${API_BASE}/api/uploads/${enhancedFilename}" alt="Enhanced">
                        <div class="image-label">Enhanced</div>
                        <a href="${API_BASE}/api/download/${enhancedFilename}?dish_name=enhanced_dish"
                           class="btn-download" download>
                            Download Enhanced
                        </a>
                    </div>
                </div>
            </div>
        `;

        displayResults(html);

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}

// Run Full Pipeline
async function runFullPipeline() {
    if (!uploadedPhoto) {
        alert('Please upload a photo first');
        return;
    }

    const menuItems = getMenuItems();
    if (menuItems.length === 0) {
        alert('Please add at least one menu item');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('photo', uploadedPhoto);
        formData.append('menu_items', JSON.stringify(menuItems));

        const response = await fetch(`${API_BASE}/api/full-pipeline`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to process pipeline');
        }

        const result = await response.json();

        // Display combined results
        const match = result.stage2_match;
        const quality = result.stage3_quality;
        const enhancement = result.stage4_enhancement;

        const confidenceClass = match.confidence >= 75 ? 'confidence-high' :
                               match.confidence >= 50 ? 'confidence-medium' : 'confidence-low';

        const qualityClass = quality.overall_quality === 'Ready' ? 'quality-ready' :
                            quality.overall_quality === 'Needs Enhancement' ? 'quality-enhance' : 'quality-reject';

        let enhancementHTML = '';
        if (enhancement) {
            const enhancedFilename = enhancement.enhanced_image_url.split('/').pop();
            enhancementHTML = `
                <div class="result-card">
                    <h4>Stage 4: Photo Enhancement</h4>
                    <div class="result-item">
                        <span class="result-label">Status:</span>
                        <span class="result-value quality-ready">Enhanced Successfully</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Transformations:</span>
                        <span class="result-value">${enhancement.transformations_applied.join(', ')}</span>
                    </div>
                    <div class="enhanced-images">
                        <div>
                            <img src="${API_BASE}/api/uploads/${uploadedPhoto.name}" alt="Original">
                            <div class="image-label">Original</div>
                        </div>
                        <div>
                            <img src="${API_BASE}/api/uploads/${enhancedFilename}" alt="Enhanced">
                            <div class="image-label">Enhanced - ${match.matched_item}</div>
                            <a href="${API_BASE}/api/download/${enhancedFilename}?dish_name=${encodeURIComponent(match.matched_item)}"
                               class="btn-download" download>
                                Download ${match.matched_item}
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }

        const html = `
            <div class="result-card">
                <h4>Stage 2: Photo-to-Item Matching</h4>
                <div class="result-item">
                    <span class="result-label">Matched Item:</span>
                    <span class="result-value"><strong>${match.matched_item}</strong></span>
                </div>
                <div class="result-item">
                    <span class="result-label">Confidence:</span>
                    <span class="result-value ${confidenceClass}">${match.confidence}%</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${match.confidence}%"></div>
                    </div>
                </div>
                <div class="result-item">
                    <span class="result-label">Description:</span>
                    <span class="result-value">${match.description}</span>
                </div>
            </div>

            <div class="result-card">
                <h4>Stage 3: Quality Assessment</h4>
                <div class="result-item">
                    <span class="result-label">Overall Quality:</span>
                    <span class="result-value ${qualityClass}">${quality.overall_quality}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Overall Score:</span>
                    <span class="result-value"><strong>${quality.overall_score}%</strong></span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${quality.overall_score}%"></div>
                    </div>
                </div>

                <div class="quality-breakdown">
                    <h5>Detailed Scores:</h5>
                    <div class="result-item">
                        <span class="result-label">Resolution:</span>
                        <span class="result-value">${quality.resolution_score}%</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${quality.resolution_score}%"></div>
                        </div>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Lighting:</span>
                        <span class="result-value">${quality.lighting_score}%</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${quality.lighting_score}%"></div>
                        </div>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Composition:</span>
                        <span class="result-value">${quality.composition_score}%</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${quality.composition_score}%"></div>
                        </div>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Presentation:</span>
                        <span class="result-value">${quality.presentation_score}%</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${quality.presentation_score}%"></div>
                        </div>
                    </div>
                </div>

                <div class="result-item">
                    <span class="result-label">Recommendation:</span>
                    <span class="result-value">${quality.recommendation}</span>
                </div>
            </div>

            ${enhancementHTML}
        `;

        displayResults(html);

    } catch (error) {
        hideLoading();
        alert(`Error: ${error.message}`);
    }
}
