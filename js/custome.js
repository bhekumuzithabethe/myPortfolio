// custome.js
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar functionality
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const body = document.body;
    const navbarToggler = document.querySelector('.navbar-toggler');

    // Function to open sidebar
    function openSidebar() {
        sidebar.classList.add('active');
        overlay.classList.add('active');
        body.style.overflow = 'hidden';
    }

    // Function to close sidebar
    function closeSidebar() {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        body.style.overflow = '';
    }

    // Make functions available globally
    window.openSidebar = openSidebar;
    window.closeSidebar = closeSidebar;

    // Close sidebar when clicking overlay
    overlay.addEventListener('click', closeSidebar);

    // Close sidebar with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });

    // Smooth scroll to section and close sidebar
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                const target = document.querySelector(href);
                if (target) {
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                    // Close sidebar after clicking a link on mobile
                    if (window.innerWidth <= 991) {
                        closeSidebar();
                    }
                }
            }
        });
    });

    // Theme button in sidebar
    document.querySelector('.sidebar-theme-btn')?.addEventListener('click', function() {
        toggleTheme();
        if (window.innerWidth <= 991) {
            setTimeout(closeSidebar, 300);
        }
    });

    // Project filtering functionality
    const filterButtons = document.querySelectorAll('.filter-buttons .btn');
    const projectItems = document.querySelectorAll('.project-item');
    
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const filterValue = this.getAttribute('data-filter');
                
                // Filter projects
                projectItems.forEach(item => {
                    if (filterValue === 'all' || item.getAttribute('data-category').includes(filterValue)) {
                        item.style.display = 'block';
                        setTimeout(() => {
                            item.classList.remove('hidden');
                        }, 10);
                    } else {
                        item.classList.add('hidden');
                        setTimeout(() => {
                            item.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
    }

    // Project details modal
    const projectDetails = {
        tutorking: {
            title: "Tutor King E-Learning Platform",
            description: "A sophisticated Learning Management System built to facilitate online tutoring operations. The platform supports multiple user roles (students, tutors, administrators) with comprehensive course management capabilities.",
            features: [
                "Course creation and management with multimedia content support",
                "Student progress tracking and performance analytics",
                "Interactive assignment submission and grading system",
                "Real-time messaging between tutors and students",
                "Payment gateway integration for course enrollment",
                "Admin dashboard for comprehensive oversight"
            ],
            technologies: ["Django", "PostgreSQL", "Bootstrap 5", "JavaScript", "RESTful APIs", "Azure Deployment"],
            challenges: "Implementing real-time notifications and ensuring scalable database architecture for concurrent user access.",
            solutions: "Utilized Django Channels for WebSocket communication and optimized database queries with selective prefetching."
        },
        teddysambu: {
            title: "Teddy Sambu Photography Booking System",
            description: "A complete booking management solution for professional photographers, streamlining client appointments and portfolio management.",
            features: [
                "Interactive booking calendar with time slot management",
                "Client database with session history",
                "Portfolio gallery with category filtering",
                "Automated email confirmation system",
                "Payment processing for session deposits",
                "Mobile-responsive client interface"
            ],
            technologies: ["Django", "PostgreSQL", "Bootstrap", "jQuery", "FullCalendar.js", "Stripe API"],
            challenges: "Synchronizing multiple calendars and preventing booking conflicts.",
            solutions: "Implemented constraint validation and buffer times between appointments with database-level locking."
        },
        ontec: {
            title: "Ontec Systems Corporate Website",
            description: "A modern, responsive corporate website designed to showcase services and attract potential clients through compelling UI/UX.",
            features: [
                "Responsive design for all device sizes",
                "Service portfolio with case studies",
                "Contact form with backend processing",
                "Blog section for company updates",
                "Performance optimized for fast loading",
                "SEO-friendly structure"
            ],
            technologies: ["HTML5", "CSS3", "JavaScript", "Bootstrap", "Azure Static Web Apps"],
            challenges: "Achieving perfect cross-browser compatibility while maintaining design consistency.",
            solutions: "Utilized CSS Grid and Flexbox with progressive enhancement techniques."
        },
        tobias: {
            title: "Tobias Mafiet's Portfolio Website",
            description: "Modern portfolio website with interactive project showcases, responsive design, and smooth animations to highlight creative work effectively.",
            features: [
                "Responsive design for all devices",
                "Interactive project gallery",
                "Smooth CSS animations",
                "Contact form integration",
                "Fast loading performance",
                "SEO optimized"
            ],
            technologies: ["HTML5", "CSS3", "JavaScript", "Bootstrap 5", "CSS Animations"],
            challenges: "Creating smooth animations without impacting performance.",
            solutions: "Used CSS hardware acceleration and optimized animation performance."
        },
        todo: {
            title: "Django ToDo List Application",
            description: "Full-featured task management application with user authentication, priority sorting, due date tracking, and CRUD operations implementation.",
            features: [
                "User authentication and authorization",
                "Task creation, updating, and deletion",
                "Priority levels and due dates",
                "Task categorization",
                "Search and filter functionality",
                "Responsive design"
            ],
            technologies: ["Django", "SQLite", "Bootstrap", "Authentication", "CRUD Operations"],
            challenges: "Implementing secure user authentication and session management.",
            solutions: "Used Django's built-in authentication system with custom user models and middleware."
        },
        employee: {
            title: "Django Employee Management System",
            description: "Comprehensive HR management system featuring employee records, department management, attendance tracking, and reporting functionalities.",
            features: [
                "Employee record management",
                "Department organization",
                "Attendance tracking",
                "Performance reporting",
                "Admin dashboard",
                "Data export functionality"
            ],
            technologies: ["Django", "PostgreSQL", "Bootstrap", "Admin Panel", "Data Export"],
            challenges: "Managing complex relationships between employees, departments, and attendance records.",
            solutions: "Implemented proper database design with foreign key relationships and optimized queries."
        },
        resume: {
            title: "Ispani Resume Builder",
            description: "Professional resume creation platform with customizable templates, PDF export functionality, and user profile management for job seekers.",
            features: [
                "Customizable resume templates",
                "PDF export functionality",
                "User profile management",
                "Resume preview",
                "Multiple format support",
                "User authentication"
            ],
            technologies: ["Django", "PostgreSQL", "Bootstrap", "PDF Generation", "User Profiles"],
            challenges: "Generating high-quality PDFs from HTML content.",
            solutions: "Used xhtml2pdf library with custom CSS styling for PDF generation."
        },
        banking: {
            title: "Thabethe Banking System",
            description: "Full-scale banking simulation platform with multi-role access (clients, consultants, managers), transaction processing, and account management.",
            features: [
                "Multi-role access control",
                "Transaction processing",
                "Account management",
                "Balance tracking",
                "Transaction history",
                "Secure authentication"
            ],
            technologies: ["Django", "PostgreSQL", "Bootstrap", "Role-Based Access", "Transaction Processing"],
            challenges: "Ensuring data consistency during concurrent transactions.",
            solutions: "Implemented database transactions and locking mechanisms to prevent race conditions."
        }
    };

    // Modal functionality
    const viewDetailButtons = document.querySelectorAll('.view-details');
    const projectModal = new bootstrap.Modal(document.getElementById('projectModal'));
    
    if (viewDetailButtons.length > 0) {
        viewDetailButtons.forEach(button => {
            button.addEventListener('click', function() {
                const projectId = this.getAttribute('data-project');
                const details = projectDetails[projectId] || {
                    title: "Project Details",
                    description: "Detailed information coming soon...",
                    features: [],
                    technologies: [],
                    challenges: "",
                    solutions: ""
                };
                
                // Populate modal content
                const modalContent = `
                    <h4>${details.title}</h4>
                    <p class="mb-4">${details.description}</p>
                    
                    <h6>Key Features:</h6>
                    <ul class="mb-3">
                        ${details.features.map(feature => `<li>${feature}</li>`).join('')}
                    </ul>
                    
                    <h6>Technologies Used:</h6>
                    <div class="mb-3">
                        ${details.technologies.map(tech => `<span class="badge bg-primary me-1 mb-1">${tech}</span>`).join('')}
                    </div>
                    
                    ${details.challenges ? `
                        <h6>Challenges:</h6>
                        <p class="mb-3">${details.challenges}</p>
                    ` : ''}
                    
                    ${details.solutions ? `
                        <h6>Solutions Implemented:</h6>
                        <p>${details.solutions}</p>
                    ` : ''}
                `;
                
                document.getElementById('projectDetails').innerHTML = modalContent;
                projectModal.show();
            });
        });
    }

    // Expandable card text functionality
    document.querySelectorAll('.card-text').forEach(text => {
        text.addEventListener('click', function(e) {
            if (e.target.classList.contains('view-details') || 
                e.target.tagName === 'A' || 
                e.target.tagName === 'BUTTON') return;
            
            this.classList.toggle('expanded');
            if (this.classList.contains('expanded')) {
                this.style.whiteSpace = 'normal';
                this.style.overflow = 'visible';
                this.style.textOverflow = 'clip';
            } else {
                this.style.whiteSpace = 'nowrap';
                this.style.overflow = 'hidden';
                this.style.textOverflow = 'ellipsis';
            }
        });
    });

    // Smooth scrolling for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#" or external link
            if (href === '#' || href.includes('://') || href.includes('mailto:')) {
                return;
            }
            
            e.preventDefault();
            const targetElement = document.querySelector(href);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Update URL
                if (history.pushState) {
                    history.pushState(null, null, href);
                } else {
                    window.location.hash = href;
                }
            }
        });
    });

    // Initialize theme icon in sidebar
    updateThemeIcon();
});

// Update theme icon in sidebar
function updateThemeIcon() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const themeIcon = document.getElementById('theme-icon-sidebar');
    if (themeIcon) {
        themeIcon.className = isDark ? 'fas fa-sun me-3' : 'fas fa-moon me-3';
    }
}

// Listen for theme changes
document.addEventListener('themeChanged', updateThemeIcon);