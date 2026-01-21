/**
 * Keja Conciergerie - Website JavaScript
 * Handles interactivity, form submission, and UI components
 */

// ==========================================
// Mobile Navigation
// ==========================================
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');

if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenuBtn.classList.toggle('active');
        navLinks.classList.toggle('mobile-open');
    });

    // Close mobile menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuBtn.classList.remove('active');
            navLinks.classList.remove('mobile-open');
        });
    });
}

// ==========================================
// Navbar Scroll Effect
// ==========================================
const navbar = document.getElementById('navbar');

if (navbar) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ==========================================
// FAQ Accordion
// ==========================================
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');

    question.addEventListener('click', () => {
        // Close other open items
        faqItems.forEach(otherItem => {
            if (otherItem !== item && otherItem.classList.contains('active')) {
                otherItem.classList.remove('active');
            }
        });

        // Toggle current item
        item.classList.toggle('active');
    });
});

// ==========================================
// Smooth Scroll for Anchor Links
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');

        // Skip if it's just "#"
        if (href === '#') return;

        const target = document.querySelector(href);

        if (target) {
            e.preventDefault();

            const navbarHeight = navbar ? navbar.offsetHeight : 0;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ==========================================
// Revenue Estimate Form
// ==========================================
const estimateForm = document.getElementById('revenueEstimateForm');

if (estimateForm) {
    estimateForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = estimateForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        // Show loading state
        submitBtn.innerHTML = `
            <svg class="spinner" viewBox="0 0 24 24" width="20" height="20">
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="31.4 31.4" style="animation: spin 1s linear infinite; transform-origin: center;"/>
            </svg>
            Submitting...
        `;
        submitBtn.disabled = true;

        // Collect form data
        const formData = {
            location: document.getElementById('location').value,
            bedrooms: document.getElementById('bedrooms').value,
            furnishing: document.getElementById('furnishing').value,
            channels: document.getElementById('channels').value,
            target: document.getElementById('target').value,
            whatsapp: document.getElementById('whatsapp').value,
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            submittedAt: new Date().toISOString()
        };

        // Simulate API call (replace with actual API endpoint)
        try {
            // For demo purposes, we'll just log and show success
            console.log('Form submission:', formData);

            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Show success message
            showNotification('Thank you! We\'ll send your revenue estimate within 24 hours.', 'success');

            // Reset form
            estimateForm.reset();

        } catch (error) {
            console.error('Form submission error:', error);
            showNotification('Something went wrong. Please try again or contact us via WhatsApp.', 'error');
        } finally {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

// ==========================================
// Notification System
// ==========================================
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <svg class="notification-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                ${type === 'success'
                    ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'
                    : '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
                }
            </svg>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        animation: slideIn 0.3s ease forwards;
    `;

    const content = notification.querySelector('.notification-content');
    content.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background-color: ${type === 'success' ? '#10B981' : '#EF4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        font-size: 0.9375rem;
        font-weight: 500;
    `;

    const icon = notification.querySelector('.notification-icon');
    icon.style.cssText = 'width: 24px; height: 24px; flex-shrink: 0;';

    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0;
        margin-left: 8px;
        opacity: 0.8;
        transition: opacity 0.2s;
    `;

    // Add animation keyframes
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(100px); }
                to { opacity: 1; transform: translateX(0); }
            }
            @keyframes slideOut {
                from { opacity: 1; transform: translateX(0); }
                to { opacity: 0; transform: translateX(100px); }
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .spinner {
                animation: spin 1s linear infinite;
            }
        `;
        document.head.appendChild(style);
    }

    // Add to document
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// ==========================================
// Intersection Observer for Animations
// ==========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements that should animate on scroll
document.querySelectorAll('.step-card, .service-card, .owner-card, .testimonial-card, .pricing-card, .faq-item').forEach(el => {
    el.style.opacity = '0';
    observer.observe(el);
});

// ==========================================
// WhatsApp Click Tracking (Optional)
// ==========================================
document.querySelectorAll('a[href*="wa.me"]').forEach(link => {
    link.addEventListener('click', () => {
        console.log('WhatsApp link clicked');
        // Add your analytics tracking here
    });
});

// ==========================================
// Form Validation Helpers
// ==========================================
function validateKenyanPhone(phone) {
    // Accepts formats: +254XXXXXXXXX, 0XXXXXXXXX, 254XXXXXXXXX
    const cleaned = phone.replace(/\s+/g, '').replace(/-/g, '');
    const pattern = /^(\+?254|0)?[17]\d{8}$/;
    return pattern.test(cleaned);
}

function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

// Add real-time validation
const whatsappInput = document.getElementById('whatsapp');
const emailInput = document.getElementById('email');

if (whatsappInput) {
    whatsappInput.addEventListener('blur', () => {
        if (whatsappInput.value && !validateKenyanPhone(whatsappInput.value)) {
            whatsappInput.style.borderColor = '#EF4444';
        } else {
            whatsappInput.style.borderColor = '';
        }
    });
}

if (emailInput) {
    emailInput.addEventListener('blur', () => {
        if (emailInput.value && !validateEmail(emailInput.value)) {
            emailInput.style.borderColor = '#EF4444';
        } else {
            emailInput.style.borderColor = '';
        }
    });
}

// ==========================================
// Initialize on DOM Ready
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Keja Conciergerie website loaded');

    // Set current year in footer
    const yearSpan = document.querySelector('.footer-bottom p');
    if (yearSpan) {
        yearSpan.innerHTML = yearSpan.innerHTML.replace('2025', new Date().getFullYear());
    }
});
