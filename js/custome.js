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