// Add mouse movement effect to header
document.querySelector('header').addEventListener('mousemove', (e) => {
    const header = e.currentTarget;
    const rect = header.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    header.style.setProperty('--mouse-x', `${x}px`);
    header.style.setProperty('--mouse-y', `${y}px`);
});

// Add smooth reveal for sections
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, {
    threshold: 0.1
});

document.querySelectorAll('.section').forEach(section => {
    observer.observe(section);
});

// Add hover effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mousemove', (e) => {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        button.style.setProperty('--mouse-x', `${x}px`);
        button.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Animate skill tags when added
function animateSkillTag(tag) {
    tag.classList.add('animate-in');
    setTimeout(() => tag.classList.remove('animate-in'), 500);
}

// Add progress bar animation
function updateProgress(progress) {
    const progressBar = document.querySelector('.progress-fill');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
}

// Add typing animation to input fields
document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('focus', () => {
        input.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', () => {
        input.parentElement.classList.remove('focused');
    });
});
