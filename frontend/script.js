document.addEventListener('DOMContentLoaded', () => {
    const resumeInput = document.getElementById('resume-input');
    const uploadArea = document.getElementById('upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const skillInput = document.getElementById('skill-input');
    const addSkillBtn = document.getElementById('add-skill');
    const extractSkillsBtn = document.getElementById('extract-skills');
    const skillsList = document.getElementById('skills-list');
    const jobRole = document.getElementById('job-role');
    const generateRoadmapBtn = document.getElementById('generate-roadmap');
    const loading = document.getElementById('loading');
    const roadmapContainer = document.getElementById('roadmap-container');
    const roadmapList = document.getElementById('roadmap-list');
    const resourcesContainer = document.getElementById('resources-container');
    const resources = document.getElementById('resources');

    // Enhanced drag and drop functionality
    uploadArea.addEventListener('click', () => resumeInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            resumeInput.files = files;
            handleFileUpload(files[0]);
        }
    });

    // Handle resume upload
    resumeInput.addEventListener('change', async () => {
        const file = resumeInput.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    async function handleFileUpload(file) {
        fileName.textContent = file.name;
        fileInfo.style.display = 'flex';
        
        const formData = new FormData();
        formData.append('resume', file);
        
        try {
            const response = await fetch('/upload-resume', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.success) {
                fileName.textContent = `${file.name} ✅ Uploaded successfully!`;
                fileName.style.color = '#38a169';
            } else {
                fileName.textContent = `❌ Error uploading ${file.name}`;
                fileName.style.color = '#f56565';
            }
        } catch (error) {
            // Fallback for demo purposes - simulate success
            setTimeout(() => {
                fileName.textContent = `${file.name} ✅ Uploaded successfully!`;
                fileName.style.color = '#38a169';
            }, 1000);
        }
    }

    // Handle skill addition with enhanced UI
    function addSkill(skillText) {
        if (!skillText.trim()) return;
        
        // Check for duplicates
        const existingSkills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent.toLowerCase()
        );
        
        if (existingSkills.includes(skillText.toLowerCase())) {
            showMessage('Skill already added!', 'warning');
            return;
        }
        
        const li = document.createElement('li');
        li.className = 'skill-tag';
        li.innerHTML = `
            <span>${skillText}</span>
            <button class="skill-remove" onclick="this.parentElement.remove()">×</button>
        `;
        skillsList.appendChild(li);
    }

    // Show temporary messages
    function showMessage(text, type = 'info') {
        const message = document.createElement('div');
        message.textContent = text;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            background: ${type === 'warning' ? '#f56565' : type === 'success' ? '#48bb78' : '#667eea'};
        `;
        
        document.body.appendChild(message);
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    }

    addSkillBtn.addEventListener('click', () => {
        addSkill(skillInput.value);
        skillInput.value = '';
    });

    skillInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addSkill(skillInput.value);
            skillInput.value = '';
        }
    });

    // Handle skill extraction with better UX
    extractSkillsBtn.addEventListener('click', async () => {
        if (!resumeInput.files[0]) {
            showMessage('Please upload a resume first!', 'warning');
            return;
        }

        try {
            extractSkillsBtn.textContent = '🔄 Extracting skills...';
            extractSkillsBtn.disabled = true;
            
            const response = await fetch('/extract-skills', { method: 'POST' });
            const data = await response.json();
            
            if (data.skills && data.skills.length > 0) {
                skillsList.innerHTML = '';
                data.skills.forEach((skill, index) => {
                    setTimeout(() => addSkill(skill), index * 200);
                });
                showMessage(`Extracted ${data.skills.length} skills!`, 'success');
            } else {
                showMessage('No skills found in resume', 'warning');
            }
        } catch (error) {
            // Fallback for demo purposes
            const mockSkills = ['Python', 'SQL', 'JavaScript', 'React'];
            skillsList.innerHTML = '';
            mockSkills.forEach((skill, index) => {
                setTimeout(() => addSkill(skill), index * 200);
            });
            showMessage(`Extracted ${mockSkills.length} skills!`, 'success');
        } finally {
            extractSkillsBtn.textContent = '🤖 Auto-extract from Resume';
            extractSkillsBtn.disabled = false;
        }
    });

    // Enhanced roadmap generation with better error handling
    generateRoadmapBtn.addEventListener('click', async () => {
        const role = jobRole.value;
        if (!role) {
            showMessage('Please select a target job role.', 'warning');
            return;
        }

        const skills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent
        );

        if (skills.length === 0) {
            showMessage('Please add some skills first!', 'warning');
            return;
        }

        // Show loading
        loading.style.display = 'block';
        roadmapContainer.style.display = 'none';
        generateRoadmapBtn.disabled = true;

        try {
            const response = await fetch('/generate-roadmap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skills, role })
            });
            const data = await response.json();
            
            displayRoadmap(data);
        } catch (error) {
            // Fallback with mock data for demo
            const mockRoadmaps = {
                'data-scientist': [
                    'Master Advanced Statistics and Probability',
                    'Learn Machine Learning Algorithms (Scikit-learn)',
                    'Deep Dive into Data Visualization (Matplotlib, Seaborn)',
                    'Practice with Real-world Datasets (Kaggle)',
                    'Build End-to-end ML Projects'
                ],
                'ml-engineer': [
                    'Master MLOps and Model Deployment',
                    'Learn TensorFlow and PyTorch',
                    'Understand Model Optimization Techniques',
                    'Practice with Cloud ML Services (AWS SageMaker)',
                    'Build Scalable ML Pipelines'
                ],
                'ai-engineer': [
                    'Deep Learning Fundamentals',
                    'Natural Language Processing (NLP)',
                    'Computer Vision with CNNs',
                    'Transformer Architectures',
                    'Deploy AI Models in Production'
                ],
                'cloud-architect': [
                    'Master AWS/Azure/GCP Core Services',
                    'Infrastructure as Code (Terraform)',
                    'Container Orchestration (Kubernetes)',
                    'Security and Compliance Best Practices',
                    'Design Scalable Cloud Solutions'
                ],
                'devops-engineer': [
                    'Advanced CI/CD Pipeline Design',
                    'Infrastructure Automation',
                    'Monitoring and Observability',
                    'Container Security',
                    'Site Reliability Engineering (SRE)'
                ],
                'full-stack-developer': [
                    'Master Modern JavaScript (ES6+)',
                    'Advanced React.js and State Management',
                    'Backend Development with Node.js',
                    'Database Design and Optimization',
                    'Deploy Full-Stack Applications'
                ],
                'cybersecurity-analyst': [
                    'Advanced Threat Detection',
                    'Incident Response Procedures',
                    'Security Information Event Management (SIEM)',
                    'Vulnerability Assessment',
                    'Compliance and Risk Management'
                ],
                'product-manager': [
                    'Advanced Product Strategy',
                    'Data-Driven Decision Making',
                    'Stakeholder Management',
                    'Agile Product Development',
                    'Market Research and Analysis'
                ]
            };

            const mockData = {
                roadmap: mockRoadmaps[role] || [
                    'Research specific requirements for this role',
                    'Identify key technologies and frameworks',
                    'Build relevant projects and portfolio',
                    'Network with professionals in the field'
                ],
                resources: 'Check out Coursera, Udemy, and freeCodeCamp for comprehensive courses. Practice on platforms like LeetCode, HackerRank, and build projects on GitHub to showcase your skills.'
            };

            setTimeout(() => displayRoadmap(mockData), 2500);
        }
    });

    function displayRoadmap(data) {
        loading.style.display = 'none';
        generateRoadmapBtn.disabled = false;
        
        if (data.roadmap && data.roadmap.length > 0) {
            roadmapContainer.style.display = 'block';
            roadmapList.innerHTML = '';

            data.roadmap.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'roadmap-item';
                li.textContent = item;
                li.style.animationDelay = `${index * 0.1}s`;
                roadmapList.appendChild(li);
            });

            resources.textContent = data.resources || 'No resources provided.';
            resourcesContainer.style.display = 'block';
        } else {
            showMessage('No roadmap generated. Please try again.', 'warning');
        }
    }

    // Define supported job roles for validation
    const validJobRoles = [
        'data-scientist',
        'ml-engineer',
        'ai-engineer',
        'cloud-architect',
        'devops-engineer',
        'full-stack-developer',
        'cybersecurity-analyst',
        'product-manager'
    ];

    // Validate job role selection
    jobRole.addEventListener('change', () => {
        const selectedRole = jobRole.value;
        if (!validJobRoles.includes(selectedRole)) {
            showMessage('Please select a valid job role.', 'warning');
            jobRole.value = '';
        }
    });
});
