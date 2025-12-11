// Sidebar functionality
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const body = document.body;
const navbarToggler = document.querySelector('.navbar-toggler');

// Function to open sidebar
function openSidebar() {
    console.log('Opening sidebar'); // Debug log
    sidebar.classList.add('active');
    overlay.classList.add('active');
    body.style.overflow = 'hidden';
    document.dispatchEvent(new Event('sidebarOpened'));
}

// Function to close sidebar
function closeSidebar() {
    console.log('Closing sidebar'); // Debug log
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
    body.style.overflow = '';
    document.dispatchEvent(new Event('sidebarClosed'));
}

// Close sidebar when clicking overlay
overlay.addEventListener('click', closeSidebar);

// Close sidebar with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('active')) {
        closeSidebar();
    }
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 && 
        sidebar.classList.contains('active') && 
        !sidebar.contains(e.target) && 
        e.target !== navbarToggler && 
        !navbarToggler.contains(e.target)) {
        closeSidebar();
    }
});

// Prevent clicks inside sidebar from closing it
sidebar.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Update theme icon in sidebar
function updateThemeIcon() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const themeIcon = document.getElementById('theme-icon-sidebar');
    if (themeIcon) {
        themeIcon.className = isDark ? 'fas fa-sun me-3' : 'fas fa-moon me-3';
    }
}

// Update sidebar theme icon when theme changes
document.addEventListener('themeChanged', updateThemeIcon);

// Initialize theme icon on load
document.addEventListener('DOMContentLoaded', updateThemeIcon);

// Smooth scroll to section and close sidebar
document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                // Close sidebar after clicking a link on mobile
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            }
        }
    });
});

// Also close sidebar when clicking theme button in sidebar
document.querySelector('.sidebar-theme-btn')?.addEventListener('click', function() {
    if (window.innerWidth <= 768) {
        setTimeout(closeSidebar, 300); // Close after theme transition
    }
});

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    // Make sure sidebar is hidden by default
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
});

// Smooth scrolling functionality
function initSmoothScroll() {
    // Function to scroll to element with offset
    function scrollToElement(element, offset = 80) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
    
    // Handle all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#" or has a different protocol
            if (href === '#' || href.includes('://') || href.includes('mailto:')) return;
            
            const targetElement = document.querySelector(href);
            
            if (targetElement) {
                e.preventDefault();
                scrollToElement(targetElement, 100);
                
                // Update URL without page reload
                if (history.pushState) {
                    history.pushState(null, null, href);
                } else {
                    window.location.hash = href;
                }
            }
        });
    });
}

// Initialize smooth scrolling when DOM is loaded
document.addEventListener('DOMContentLoaded', initSmoothScroll);

// Also run if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSmoothScroll);
} else {
    initSmoothScroll();
}