// Email Archive Explorer JavaScript

const API_BASE = 'http://localhost:8000/api';
let currentPage = 0;
let searchResults = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkIndexingStatus();
    loadStats();

    // Poll indexing status every 5 seconds
    setInterval(checkIndexingStatus, 5000);
});

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Load tab-specific data
    if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// Indexing functions
async function startIndexing() {
    const mboxPath = document.getElementById('mbox-path').value.trim();

    if (!mboxPath) {
        alert('Please enter the path to your mbox file');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('mbox_path', mboxPath);

        const response = await fetch(`${API_BASE}/email/index`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert('Indexing started! This may take a while for large files. Check the status indicator.');
            checkIndexingStatus();
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error starting indexing: ${error.message}`);
    }
}

async function checkIndexingStatus() {
    try {
        const response = await fetch(`${API_BASE}/email/index/status`);
        const data = await response.json();

        const statusDisplay = document.getElementById('status-display');
        const indicator = statusDisplay.querySelector('.status-indicator');
        const statusText = statusDisplay.querySelector('span:last-child');

        // Remove all status classes
        indicator.classList.remove('ready', 'indexing', 'error', 'not-started');

        switch (data.status) {
            case 'completed':
                indicator.classList.add('ready');
                statusText.textContent = 'Indexed';
                loadStats(); // Refresh stats after indexing completes
                break;
            case 'indexing':
                indicator.classList.add('indexing');
                statusText.textContent = 'Indexing...';
                break;
            case 'error':
                indicator.classList.add('error');
                statusText.textContent = 'Error';
                break;
            default:
                indicator.classList.add('not-started');
                statusText.textContent = 'Not Indexed';
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Statistics functions
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/email/stats`);
        const data = await response.json();

        document.getElementById('stat-total').textContent = data.total_emails.toLocaleString();
        document.getElementById('stat-senders').textContent = data.unique_senders.toLocaleString();
        document.getElementById('stat-attachments').textContent = data.emails_with_attachments.toLocaleString();
        document.getElementById('stat-size').textContent = `${data.total_size_mb} MB`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Search functions
function handleSearch(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
}

async function performSearch() {
    const query = document.getElementById('search-query').value.trim();
    const sender = document.getElementById('filter-sender').value.trim();
    const subject = document.getElementById('filter-subject').value.trim();
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;

    // Build query parameters
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (sender) params.append('sender', sender);
    if (subject) params.append('subject', subject);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    params.append('limit', 50);
    params.append('offset', currentPage * 50);

    try {
        const response = await fetch(`${API_BASE}/email/search?${params}`);
        const data = await response.json();

        searchResults = data;
        displaySearchResults(data);
    } catch (error) {
        console.error('Error searching:', error);
        document.getElementById('search-results').innerHTML =
            '<p style="color: red; text-align: center;">Error performing search</p>';
    }
}

function displaySearchResults(data) {
    const container = document.getElementById('search-results');

    if (!data.results || data.results.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No emails found</p>';
        return;
    }

    let html = `<p style="margin-bottom: 15px; color: #666;">Found ${data.total_count} emails (showing ${data.results.length})</p>`;
    html += '<ul class="email-list">';

    data.results.forEach(email => {
        const date = email.date ? new Date(email.date).toLocaleDateString() : 'No date';
        const subject = email.subject || '(No subject)';
        const sender = email.sender_email || 'Unknown';

        html += `
            <li class="email-item" onclick="viewEmail(${email.id})">
                <div class="email-subject">${escapeHtml(subject)}</div>
                <div class="email-meta">
                    <span>From: ${escapeHtml(sender)}</span>
                    <span>${date}</span>
                </div>
                ${email.has_attachments ? '<span class="email-badge">Has Attachments</span>' : ''}
            </li>
        `;
    });

    html += '</ul>';

    // Add pagination
    if (data.total_count > 50) {
        html += '<div class="pagination">';
        if (currentPage > 0) {
            html += '<button onclick="previousPage()">Previous</button>';
        }
        html += `<span>Page ${currentPage + 1}</span>`;
        if (data.has_more) {
            html += '<button onclick="nextPage()">Next</button>';
        }
        html += '</div>';
    }

    container.innerHTML = html;
}

async function viewEmail(emailId) {
    try {
        const response = await fetch(`${API_BASE}/email/${emailId}`);
        const email = await response.json();

        const detailContainer = document.getElementById('email-detail');

        let html = `
            <div class="email-detail">
                <div class="email-detail-header">
                    <h3>${escapeHtml(email.subject || '(No subject)')}</h3>
                    <p><strong>From:</strong> ${escapeHtml(email.sender || '')} &lt;${escapeHtml(email.sender_email || '')}&gt;</p>
                    <p><strong>To:</strong> ${escapeHtml(email.recipient || '')} &lt;${escapeHtml(email.recipient_email || '')}&gt;</p>
                    <p><strong>Date:</strong> ${email.date ? new Date(email.date).toLocaleString() : 'Unknown'}</p>
                    ${email.attachments && email.attachments.length > 0 ? `
                        <p><strong>Attachments:</strong> ${email.attachments.map(a => escapeHtml(a.filename)).join(', ')}</p>
                    ` : ''}
                </div>
                <div class="email-detail-body">
                    ${escapeHtml(email.body_text || '(No body text)')}
                </div>
                <button onclick="closeEmailDetail()" style="margin-top: 15px; background: #6c757d;">Close</button>
            </div>
        `;

        detailContainer.innerHTML = html;
        detailContainer.style.display = 'block';
        detailContainer.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error loading email:', error);
        alert('Error loading email details');
    }
}

function closeEmailDetail() {
    document.getElementById('email-detail').style.display = 'none';
}

function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        performSearch();
    }
}

function nextPage() {
    if (searchResults && searchResults.has_more) {
        currentPage++;
        performSearch();
    }
}

function clearFilters() {
    document.getElementById('search-query').value = '';
    document.getElementById('filter-sender').value = '';
    document.getElementById('filter-subject').value = '';
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    currentPage = 0;
    document.getElementById('search-results').innerHTML =
        '<p style="text-align: center; color: #666; padding: 40px;">Enter search criteria above to find emails</p>';
}

// Analytics functions
async function loadAnalytics() {
    loadTopSenders();
    loadTopRecipients();
    loadEmailsByYear();
    loadEmailsByDay();
}

async function loadTopSenders() {
    try {
        const response = await fetch(`${API_BASE}/email/analytics/top-senders?limit=10`);
        const result = await response.json();

        const container = document.getElementById('analytics-senders');

        if (!result.data || result.data.length === 0) {
            container.innerHTML = '<p style="color: #666;">No data available</p>';
            return;
        }

        let html = '<ul class="email-list">';
        result.data.forEach(sender => {
            html += `
                <li class="email-item">
                    <div class="email-subject">${escapeHtml(sender.sender_email || 'Unknown')}</div>
                    <div class="email-meta">
                        <span>${sender.email_count} emails</span>
                        <span class="email-badge">${(sender.total_size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                </li>
            `;
        });
        html += '</ul>';

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading senders:', error);
    }
}

async function loadTopRecipients() {
    try {
        const response = await fetch(`${API_BASE}/email/analytics/top-recipients?limit=10`);
        const result = await response.json();

        const container = document.getElementById('analytics-recipients');

        if (!result.data || result.data.length === 0) {
            container.innerHTML = '<p style="color: #666;">No data available</p>';
            return;
        }

        let html = '<ul class="email-list">';
        result.data.forEach(recipient => {
            html += `
                <li class="email-item">
                    <div class="email-subject">${escapeHtml(recipient.recipient_email || 'Unknown')}</div>
                    <div class="email-meta">
                        <span>${recipient.email_count} emails</span>
                        <span class="email-badge">${(recipient.total_size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                </li>
            `;
        });
        html += '</ul>';

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading recipients:', error);
    }
}

async function loadEmailsByYear() {
    try {
        const response = await fetch(`${API_BASE}/email/analytics/by-year`);
        const result = await response.json();

        const container = document.getElementById('analytics-years');

        if (!result.data || result.data.length === 0) {
            container.innerHTML = '<p style="color: #666;">No data available</p>';
            return;
        }

        let html = '<div class="chart-container">';
        result.data.forEach(item => {
            const percentage = 100; // Simplified visualization
            html += `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>${item.year || 'Unknown'}</strong>
                        <span>${item.count} emails</span>
                    </div>
                    <div style="background: #ddd; height: 20px; border-radius: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${percentage}%;"></div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading years:', error);
    }
}

async function loadEmailsByDay() {
    try {
        const response = await fetch(`${API_BASE}/email/analytics/by-day`);
        const result = await response.json();

        const container = document.getElementById('analytics-days');

        if (!result.data || result.data.length === 0) {
            container.innerHTML = '<p style="color: #666;">No data available</p>';
            return;
        }

        const maxCount = Math.max(...result.data.map(d => d.count));

        let html = '<div class="chart-container">';
        result.data.forEach(item => {
            const percentage = (item.count / maxCount) * 100;
            html += `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>${item.day_of_week}</strong>
                        <span>${item.count} emails</span>
                    </div>
                    <div style="background: #ddd; height: 20px; border-radius: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${percentage}%;"></div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading days:', error);
    }
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
