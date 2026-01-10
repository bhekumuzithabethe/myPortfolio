document.addEventListener('DOMContentLoaded', function() {
    const learnerBtn = document.getElementById('learnerBtn');
    const tutorBtn = document.getElementById('tutorBtn');
    
    function setActiveButton(activeBtn, inactiveBtn) {
        // Set active button
        activeBtn.classList.remove('btn-outline-primary');
        activeBtn.classList.add('btn-primary');
        
        // Set inactive button
        inactiveBtn.classList.remove('btn-primary');
        inactiveBtn.classList.add('btn-outline-primary');
    }
    
    learnerBtn.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent immediate navigation
        setActiveButton(learnerBtn, tutorBtn);
        // Navigate after a brief delay for visual feedback
        setTimeout(() => {
            window.location.href = learnerBtn.href;
        }, 300);
    });
    
    tutorBtn.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent immediate navigation
        setActiveButton(tutorBtn, learnerBtn);
        // Navigate after a brief delay for visual feedback
        setTimeout(() => {
            window.location.href = tutorBtn.href;
        }, 300);
    });
    
    // Optional: Set initial active state based on current URL
    const currentPath = window.location.pathname;
    if (currentPath.includes('tutor')) {
        setActiveButton(tutorBtn, learnerBtn);
    } else {
        setActiveButton(learnerBtn, tutorBtn); // Default to learner
    }
});