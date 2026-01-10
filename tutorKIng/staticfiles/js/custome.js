// Get references to DOM elements
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById("overlay");


// Function to toggle sidebar visibility and overlay activation
function openSidebar() {
    // Toggle sidebar visibility
    sidebar.classList.toggle('show');

    // Activate or deactivate overlay
    overlay.classList.toggle("active");

    // Prevent background scrolling when sidebar is open
    document.body.classList.toggle("sidebar-open");
}

// Close sidebar when clicking the overlay area
overlay.addEventListener("click", () => {
    // Hide sidebar
    sidebar.classList.remove("show");

    // Remove overlay effect
    overlay.classList.remove("active");

    // Restore background scroll functionality
    document.body.classList.remove("sidebar-open");
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
