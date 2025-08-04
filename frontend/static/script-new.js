document.addEventListener('DOMContentLoaded', () => {
    // Initialize elements
    const elements = {
        resumeInput: document.getElementById('resume-input'),
        uploadArea: document.getElementById('upload-area'),
        fileInfo: document.getElementById('file-info'),
        fileName: document.getElementById('file-name'),
        skillInput: document.getElementById('skill-input'),
        addSkillBtn: document.getElementById('add-skill'),
        extractSkillsBtn: document.getElementById('extract-skills'),
        skillsList: document.getElementById('skills-list'),
        jobRole: document.getElementById('job-role'),
        generateRoadmapBtn: document.getElementById('generate-roadmap'),
        loading: document.getElementById('loading'),
        progressFill: document.querySelector('.progress-fill'),
        readinessResults: document.getElementById('readiness-results'),
        industryEvaluation: document.getElementById('industry-evaluation')
    };

    // Initialize tooltips
    tippy('[data-tooltip]', {
        placement: 'top',
        animation: 'scale',
        theme: 'gradient'
    });

    // File upload handling with progress simulation
    function handleFileUpload(file) {
        elements.fileName.textContent = `📄 ${file.name}`;
        elements.fileInfo.style.display = 'block';
        elements.uploadArea.classList.add('uploaded');
        
        // Simulate upload progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            elements.progressFill.style.width = `${progress}%`;
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    elements.progressFill.style.width = '0%';
                    elements.uploadArea.classList.add('complete');
                }, 500);
            }
        }, 100);
    }

    // Enhanced drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('dragover');
    });

    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });

    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Skills management
    function addSkill(skillName) {
        if (!skillName) return;
        
        const skillTag = document.createElement('div');
        skillTag.className = 'skill-tag animate__animated animate__fadeIn';
        skillTag.innerHTML = `
            ${skillName}
            <button class="skill-remove" aria-label="Remove skill">×</button>
        `;

        skillTag.querySelector('.skill-remove').addEventListener('click', () => {
            skillTag.classList.add('animate__fadeOut');
            setTimeout(() => skillTag.remove(), 500);
        });

        elements.skillsList.appendChild(skillTag);
        elements.skillInput.value = '';
    }

    elements.addSkillBtn.addEventListener('click', () => {
        addSkill(elements.skillInput.value.trim());
    });

    elements.skillInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addSkill(elements.skillInput.value.trim());
        }
    });

    // Job role selection effects
    elements.jobRole.addEventListener('change', () => {
        if (elements.jobRole.value) {
            elements.readinessResults.style.display = 'block';
            elements.industryEvaluation.style.display = 'block';
            elements.generateRoadmapBtn.classList.remove('disabled');
            
            // Simulate loading state
            elements.loading.style.display = 'block';
            setTimeout(() => {
                elements.loading.style.display = 'none';
                updateReadinessChart();
            }, 1500);
        }
    });

    // Readiness visualization with Chart.js
    function updateReadinessChart() {
        const ctx = document.getElementById('readiness-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Technical Skills', 'Experience', 'Education', 'Soft Skills', 'Industry Knowledge'],
                datasets: [{
                    label: 'Your Profile',
                    data: [75, 68, 90, 85, 70],
                    fill: true,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgb(102, 126, 234)',
                    pointBackgroundColor: 'rgb(102, 126, 234)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(102, 126, 234)'
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        });
    }

    // Initialize animations for sections
    const sections = document.querySelectorAll('.section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__fadeInUp');
                sectionObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        sectionObserver.observe(section);
    });
});
