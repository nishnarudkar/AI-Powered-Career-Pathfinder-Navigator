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
                resumeInput.dataset.sessionId = data.session_id;
            } else {
                fileName.textContent = `❌ Error uploading ${file.name}: ${data.error}`;
                fileName.style.color = '#f56565';
            }
        } catch (error) {
            fileName.textContent = `❌ Error uploading ${file.name}`;
            fileName.style.color = '#f56565';
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

    // Handle skill extraction
    extractSkillsBtn.addEventListener('click', async () => {
        if (!resumeInput.dataset.sessionId) {
            showMessage('Please upload a resume first!', 'warning');
            return;
        }

        try {
            extractSkillsBtn.textContent = '🔄 Extracting skills...';
            extractSkillsBtn.disabled = true;
            
            const response = await fetch('/extract-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: resumeInput.dataset.sessionId })
            });
            const data = await response.json();
            
            if (data.success) {
                skillsList.innerHTML = '';
                data.skills.forEach((skill, index) => {
                    setTimeout(() => addSkill(skill), index * 200);
                });
                showMessage(`Extracted ${data.skills.length} skills!`, 'success');
            } else {
                showMessage(`Error: ${data.error}`, 'warning');
            }
        } catch (error) {
            showMessage('Error extracting skills', 'warning');
        } finally {
            extractSkillsBtn.textContent = '🤖 Auto-extract from Resume';
            extractSkillsBtn.disabled = false;
        }
    });

    // Enhanced roadmap generation
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

        if (!resumeInput.dataset.sessionId) {
            showMessage('Please upload a resume first!', 'warning');
            return;
        }

        loading.style.display = 'block';
        roadmapContainer.style.display = 'none';
        generateRoadmapBtn.disabled = true;

        try {
            const response = await fetch('/generate-roadmap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    skills, 
                    role, 
                    session_id: resumeInput.dataset.sessionId 
                })
            });
            const data = await response.json();
            
            if (data.success) {
                displayRoadmap(data);
            } else {
                showMessage(`Error: ${data.error}`, 'warning');
            }
        } catch (error) {
            showMessage('Error generating roadmap', 'warning');
        } finally {
            loading.style.display = 'none';
            generateRoadmapBtn.disabled = false;
        }
    });

    function displayRoadmap(data) {
        roadmapContainer.style.display = 'block';
        roadmapList.innerHTML = '';
        resources.textContent = data.resources || 'No resources provided.';
        resourcesContainer.style.display = 'block';

        if (data.roadmap && data.roadmap.length > 0) {
            data.roadmap.forEach((phase, phaseIndex) => {
                const phaseHeader = document.createElement('h3');
                phaseHeader.className = 'phase-header';
                phaseHeader.textContent = phase.phase;
                roadmapList.appendChild(phaseHeader);

                phase.skills.forEach((item, itemIndex) => {
                    const li = document.createElement('li');
                    li.className = 'roadmap-item';
                    li.style.animationDelay = `${(phaseIndex * phase.skills.length + itemIndex) * 0.1}s`;
                    
                    const skillSpan = document.createElement('span');
                    skillSpan.textContent = item.skill;
                    li.appendChild(skillSpan);

                    if (item.course.title !== 'N/A') {
                        const courseDiv = document.createElement('div');
                        courseDiv.className = 'course-info';
                        courseDiv.innerHTML = `
                            <p><strong>Course:</strong> <a href="${item.course.url}" target="_blank">${item.course.title}</a> (${item.course.platform})</p>
                            <p><strong>Why:</strong> ${item.course.reason}</p>
                        `;
                        li.appendChild(courseDiv);
                    }

                    roadmapList.appendChild(li);
                });
            });
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