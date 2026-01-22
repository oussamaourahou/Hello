// API Base URL
const API_BASE = window.location.origin;

// Global state
let clerkInstance = null;
let currentRestaurant = null;
let menuItems = [];
let uploadedPhotos = [];
let currentStep = 0;

// Initialize Clerk
window.addEventListener('load', async () => {
    if (window.Clerk) {
        try {
            clerkInstance = window.Clerk;
            await clerkInstance.load();

            if (clerkInstance.user) {
                const userButtonContainer = document.getElementById('user-button-container');
                if (userButtonContainer) {
                    clerkInstance.mountUserButton(userButtonContainer);
                }
            } else {
                clerkInstance.redirectToSignIn();
            }
        } catch (error) {
            console.error('Clerk initialization error:', error);
            alert('Authentication system failed to load. Please refresh the page.');
        }
    }
});

// Helper function to get auth token
async function getAuthToken() {
    if (!clerkInstance || !clerkInstance.session) {
        throw new Error('Not authenticated');
    }
    return await clerkInstance.session.getToken();
}

// Navigation
function goToStep(step) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active', 'completed'));

    // Show target screen
    document.getElementById(`screen-${step}`).classList.add('active');
    document.getElementById(`step-${step}`).classList.add('active');

    // Mark previous steps as completed
    for (let i = 0; i < step; i++) {
        document.getElementById(`step-${i}`).classList.add('completed');
    }

    currentStep = step;
}

// Step 0: Create Restaurant
async function createRestaurant() {
    const name = document.getElementById('restaurantName').value.trim();
    const cuisineType = document.getElementById('cuisineType').value.trim();

    if (!name) {
        alert('Please enter a restaurant name');
        return;
    }

    try {
        const token = await getAuthToken();
        const formData = new FormData();
        formData.append('name', name);
        if (cuisineType) formData.append('cuisine_type', cuisineType);

        const response = await fetch(`${API_BASE}/api/restaurants`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (!response.ok) throw new Error('Failed to create restaurant');

        currentRestaurant = await response.json();
        console.log('Restaurant created:', currentRestaurant);

        goToStep(1);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Step 1: Upload Menu
async function handleMenuUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const uploadArea = document.getElementById('menuUploadArea');
    uploadArea.classList.add('has-file');
    uploadArea.innerHTML = `<div>✓ ${file.name}</div>`;

    checkExtractButton();
}

// Step 1: Upload Photos
async function handlePhotosUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    const uploadArea = document.getElementById('photosUploadArea');
    uploadArea.classList.add('has-file');
    uploadArea.innerHTML = `<div>✓ ${files.length} photos selected</div>`;

    checkExtractButton();
}

function checkExtractButton() {
    const menuFile = document.getElementById('menuFileInput').files[0];
    const photoFiles = document.getElementById('photosFileInput').files;

    const extractBtn = document.getElementById('extractBtn');
    extractBtn.disabled = !(menuFile && photoFiles.length > 0);
}

// Step 1: Extract Menu & Upload Photos
async function extractMenu() {
    const menuFile = document.getElementById('menuFileInput').files[0];
    const photoFiles = Array.from(document.getElementById('photosFileInput').files);

    if (!menuFile || photoFiles.length === 0) {
        alert('Please upload both menu and photos');
        return;
    }

    document.getElementById('loading-1').classList.add('show');

    try {
        const token = await getAuthToken();

        // 1. Extract menu items
        const menuFormData = new FormData();
        menuFormData.append('menu_file', menuFile);

        const menuResponse = await fetch(`${API_BASE}/api/restaurants/${currentRestaurant.id}/upload-menu`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: menuFormData
        });

        if (!menuResponse.ok) throw new Error('Failed to extract menu');

        const menuResult = await menuResponse.json();
        menuItems = menuResult.menu_items;

        // 2. Upload all photos
        uploadedPhotos = [];
        for (const photoFile of photoFiles) {
            const photoFormData = new FormData();
            photoFormData.append('photo', photoFile);

            const photoResponse = await fetch(`${API_BASE}/api/restaurants/${currentRestaurant.id}/upload-photo`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: photoFormData
            });

            if (photoResponse.ok) {
                const photoResult = await photoResponse.json();
                uploadedPhotos.push(photoResult);
            }
        }

        // Show results
        const resultsDiv = document.getElementById('uploadResults');
        resultsDiv.innerHTML = `
            <div class="result-list">
                <div class="result-item">
                    <strong>Menu Items Extracted:</strong> ${menuItems.length} items
                </div>
                <div class="result-item">
                    <strong>Photos Uploaded:</strong> ${uploadedPhotos.length} photos
                </div>
            </div>
        `;

        document.getElementById('loading-1').classList.remove('show');

        // Auto-proceed to matching
        setTimeout(() => {
            matchPhotos();
        }, 1000);

    } catch (error) {
        document.getElementById('loading-1').classList.remove('show');
        alert(`Error: ${error.message}`);
    }
}

// Step 2: Match Photos to Menu Items
async function matchPhotos() {
    goToStep(2);
    document.getElementById('loading-2').classList.add('show');

    try {
        const token = await getAuthToken();

        const response = await fetch(`${API_BASE}/api/restaurants/${currentRestaurant.id}/match-all`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to match photos');

        const matchResults = await response.json();

        // Display matches
        const matchingDiv = document.getElementById('matchingResults');
        let html = '<div class="result-list">';

        for (const match of matchResults) {
            const confidenceLevel = match.confidence >= 75 ? 'high' : match.confidence >= 50 ? 'medium' : 'low';
            const confidenceClass = `confidence-${confidenceLevel}`;
            const itemClass = `match-item ${confidenceLevel}-confidence`;

            html += `
                <div class="${itemClass}">
                    <div>
                        <strong>${match.matched_item}</strong><br>
                        <small>Photo ID: ${match.photo_id.substring(0, 8)}...</small>
                    </div>
                    <span class="confidence-badge ${confidenceClass}">
                        ${match.confidence}% ${confidenceLevel.toUpperCase()}
                    </span>
                </div>
            `;
        }

        html += '</div>';
        matchingDiv.innerHTML = html;

        document.getElementById('loading-2').classList.remove('show');

    } catch (error) {
        document.getElementById('loading-2').classList.remove('show');
        alert(`Error: ${error.message}`);
    }
}

// Step 3: Proceed to Quality Check
function proceedToQuality() {
    goToStep(3);

    const qualityDiv = document.getElementById('qualityResults');
    qualityDiv.innerHTML = `
        <div class="result-item">
            <p>Click "Enhance All Photos" to process all matched photos with Photoroom.</p>
            <p>Low quality photos will be flagged for replacement or AI generation.</p>
        </div>
    `;
}

// Step 3: Enhance All Photos
async function enhanceAllPhotos() {
    document.getElementById('loading-3').classList.add('show');
    document.getElementById('enhanceBtn').disabled = true;

    try {
        const token = await getAuthToken();

        const response = await fetch(`${API_BASE}/api/restaurants/${currentRestaurant.id}/enhance-all`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to enhance photos');

        const enhanceResults = await response.json();

        // Display results
        const qualityDiv = document.getElementById('qualityResults');
        let html = '<div class="result-list">';

        let lowQualityCount = 0;
        for (const result of enhanceResults) {
            const qualityClass = result.quality_score >= 75 ? 'high' : result.quality_score >= 50 ? 'medium' : 'low';

            if (result.quality_score < 75) lowQualityCount++;

            html += `
                <div class="match-item ${qualityClass}-confidence">
                    <div>
                        <strong>${result.menu_item_name}</strong><br>
                        <small>Quality: ${result.quality_score}%</small>
                    </div>
                    <span class="confidence-badge confidence-${qualityClass}">
                        ${result.enhanced_url ? '✓ Enhanced' : '⚠ Needs Review'}
                    </span>
                </div>
            `;
        }

        html += `</div>
            <div class="result-item" style="margin-top: 20px; background: #fff3cd; border-left: 4px solid #ffc107;">
                <strong>${lowQualityCount} items need attention</strong><br>
                These will be available for AI generation in the next step.
            </div>
        `;

        qualityDiv.innerHTML = html;

        document.getElementById('loading-3').classList.remove('show');

        // Auto-proceed to gap filling
        setTimeout(() => {
            showGapFilling(enhanceResults);
        }, 2000);

    } catch (error) {
        document.getElementById('loading-3').classList.remove('show');
        document.getElementById('enhanceBtn').disabled = false;
        alert(`Error: ${error.message}`);
    }
}

// Step 4: Gap Filling
function showGapFilling(enhanceResults) {
    goToStep(4);

    const gapDiv = document.getElementById('gapResults');
    let html = '<div class="result-list">';

    const itemsNeedingGeneration = enhanceResults.filter(r => r.quality_score < 75 || !r.enhanced_url);

    if (itemsNeedingGeneration.length === 0) {
        html += `
            <div class="result-item">
                <strong>✓ All items have good quality photos!</strong><br>
                No gaps to fill. Ready to export.
            </div>
        `;
    } else {
        html += `
            <div class="result-item" style="margin-bottom: 20px;">
                <strong>${itemsNeedingGeneration.length} items need AI-generated photos</strong>
            </div>
        `;

        for (const item of itemsNeedingGeneration) {
            html += `
                <div class="match-item low-confidence">
                    <div>
                        <strong>${item.menu_item_name}</strong><br>
                        <small>Quality: ${item.quality_score}%</small>
                    </div>
                    <button class="btn btn-primary" onclick="generateImageForItem('${item.menu_item_name}', '${item.menu_item_id}')">
                        🎨 Generate
                    </button>
                </div>
            `;
        }
    }

    html += '</div>';
    gapDiv.innerHTML = html;
}

// Generate AI image for specific item
async function generateImageForItem(dishName, itemId) {
    try {
        const token = await getAuthToken();
        const formData = new FormData();
        formData.append('dish_name', dishName);

        const response = await fetch(`${API_BASE}/api/generate-image`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (!response.ok) throw new Error('Failed to generate image');

        const result = await response.json();
        alert(`✓ Generated image for ${dishName}!`);

    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Step 5: Export
function exportData() {
    goToStep(5);

    fetch(`${API_BASE}/api/restaurants/${currentRestaurant.id}/export`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
    })
    .then(r => r.json())
    .then(data => {
        const exportDiv = document.getElementById('exportResults');
        exportDiv.innerHTML = `
            <div class="result-item">
                <strong>✓ Export Complete!</strong><br><br>
                <pre style="background: #f9f9f9; padding: 15px; border-radius: 8px; overflow: auto; max-height: 400px;">
${JSON.stringify(data, null, 2)}
                </pre>
            </div>
        `;
    })
    .catch(err => alert(`Error: ${err.message}`));
}

// Start over
function startOver() {
    if (confirm('Start a new restaurant? This will reset the current workflow.')) {
        currentRestaurant = null;
        menuItems = [];
        uploadedPhotos = [];
        document.getElementById('restaurantName').value = '';
        document.getElementById('cuisineType').value = '';
        goToStep(0);
    }
}
