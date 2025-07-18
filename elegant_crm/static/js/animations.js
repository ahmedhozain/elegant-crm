// ===== ELEGANT CRM - Animations & Interactivity =====

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Loading Screen Animation =====
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        // Hide loading screen after 1 second
        setTimeout(() => {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }, 1000);
    }

    // ===== Initialize Animations =====
    initializeAnimations();
    
    // ===== Form Interactions =====
    initializeFormInteractions();
    
    // ===== Table Interactions =====
    initializeTableInteractions();
    
    // ===== Navigation Interactions =====
    initializeNavigationInteractions();
    
    // ===== Button Interactions =====
    initializeButtonInteractions();
    
    // ===== Scroll Animations =====
    initializeScrollAnimations();
    
    // ===== Page Transitions =====
    initializePageTransitions();
});

// ===== Simple Animations (without GSAP) =====
function initializeAnimations() {
    // Animate main content on page load
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(20px)';
        setTimeout(() => {
            mainContent.style.transition = 'all 0.8s ease';
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }

    // Animate cards with stagger
    const cards = document.querySelectorAll('.elegant-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });

    // Animate form elements
    const formElements = document.querySelectorAll('.form-control, .form-select');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateX(0)';
        }, 300 + (index * 50));
    });
}

// ===== Form Interactions =====
function initializeFormInteractions() {
    const formControls = document.querySelectorAll('.form-control, .form-select');
    
    formControls.forEach(control => {
        // Add focus effects
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'all 0.3s ease';
        });

        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            this.style.transform = 'scale(1)';
        });

        // Add input validation feedback
        control.addEventListener('input', function() {
            validateField(this);
        });
    });

    // Form submission animation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> جاري الإرسال...';
                
                // Simulate loading (remove in production)
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> تم الإرسال';
                    submitBtn.classList.add('elegant-btn-success');
                }, 2000);
            }
        });
    });
}

// ===== Table Interactions =====
function initializeTableInteractions() {
    const tableRows = document.querySelectorAll('.elegant-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.transition = 'all 0.3s ease';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '#ffffff';
        });

        // Add click effect
        row.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'all 0.1s ease';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
}

// ===== Navigation Interactions =====
function initializeNavigationInteractions() {
    const navLinks = document.querySelectorAll('.elegant-nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'all 0.3s ease';
        });

        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Active link highlighting
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.style.backgroundColor = 'rgba(220, 53, 69, 0.2)';
        }
    });
}

// ===== Button Interactions =====
function initializeButtonInteractions() {
    const buttons = document.querySelectorAll('.elegant-btn, .btn');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
            this.style.transition = 'all 0.3s ease';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });

        button.addEventListener('click', function(e) {
            // Ripple effect
            createRippleEffect(this, e);
        });
    });
}

// ===== Scroll Animations =====
function initializeScrollAnimations() {
    // Simple scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for scroll animation
    const animateElements = document.querySelectorAll('.elegant-card, .elegant-form, .elegant-table');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

// ===== Page Transitions =====
function initializePageTransitions() {
    // Add page transition class to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('page-transition');
    }

    // Smooth scroll to top on navigation
    const navLinks = document.querySelectorAll('.elegant-nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    });
}

// ===== Utility Functions =====

// Field validation
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const fieldName = field.name;

    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');

    // Basic validation rules
    if (field.hasAttribute('required') && !value) {
        field.classList.add('is-invalid');
        return false;
    }

    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.classList.add('is-invalid');
            return false;
        }
    }

    // Phone validation
    if (fieldName === 'client_phone' && value) {
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        if (!phoneRegex.test(value)) {
            field.classList.add('is-invalid');
            return false;
        }
    }

    // If validation passes
    if (value) {
        field.classList.add('is-valid');
    }

    return true;
}

// Ripple effect for buttons
function createRippleEffect(button, event) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `elegant-alert elegant-alert-${type} slide-in`;
    notification.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill'}"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transition = 'all 0.5s ease';
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Add ripple effect CSS
const rippleCSS = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .btn {
        position: relative;
        overflow: hidden;
    }
`;

// Inject ripple CSS
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// ===== Performance Optimizations =====

// Debounce function for scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for resize events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Optimize scroll events
window.addEventListener('scroll', throttle(() => {
    // Add scroll-based animations here if needed
}, 16));

// ===== Accessibility Enhancements =====

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Tab navigation enhancement
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

// Remove keyboard navigation class on mouse use
document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// Focus management for modals and forms
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        }
    });
}

// Initialize focus trap for forms
document.querySelectorAll('form').forEach(form => {
    trapFocus(form);
}); 