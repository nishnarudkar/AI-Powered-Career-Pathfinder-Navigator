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

    // Drag and drop functionality
    uploadArea.addEventListener('click', () => resumeInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            resumeInput.files = e.dataTransfer.files;
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // Handle file selection
    resumeInput.addEventListener('change', () => {
        if (resumeInput.files.length > 0) {
            handleFileUpload(resumeInput.files[0]);
        }
    });

    async function handleFileUpload(file) {
        fileName.textContent = `Uploading ${file.name}...`;
        fileInfo.style.display = 'block';
        
        const formData = new FormData();
        formData.append('resume', file);
        
        try {
            const response = await fetch('/upload-resume', { method: 'POST', body: formData });
            const data = await response.json();
            
            if (data.success) {
                fileName.textContent = `✅ ${file.name}`;
                fileInfo.style.color = '#10b981';
                resumeInput.dataset.sessionId = data.session_id;
            } else {
                showError(`Upload failed: ${data.error}`);
            }
        } catch (error) {
            showError('An error occurred during upload.');
        }
    }
    
    function showError(message) {
        fileName.textContent = `❌ ${message}`;
        fileInfo.style.color = '#ef4444';
    }

    // Handle adding and displaying skills
    function addSkill(skillText) {
        if (!skillText.trim()) return;
        const existingSkills = Array.from(skillsList.querySelectorAll('span')).map(s => s.textContent.toLowerCase());
        if (existingSkills.includes(skillText.toLowerCase())) return;
        
        const li = document.createElement('li');
        li.className = 'skill-tag';
        li.innerHTML = `<span>${skillText}</span><button class="skill-remove">&times;</button>`;
        li.querySelector('.skill-remove').addEventListener('click', () => li.remove());
        skillsList.appendChild(li);
    }

    addSkillBtn.addEventListener('click', () => {
        addSkill(skillInput.value);
        skillInput.value = '';
    });
    skillInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSkill(skillInput.value);
            skillInput.value = '';
        }
    });

    // Handle auto-extraction of skills
    extractSkillsBtn.addEventListener('click', async () => {
        if (!resumeInput.dataset.sessionId) {
            alert('Please upload a resume first!');
            return;
        }
        extractSkillsBtn.textContent = 'Extracting...';
        extractSkillsBtn.disabled = true;

        try {
            const response = await fetch('/extract-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: resumeInput.dataset.sessionId })
            });
            const data = await response.json();
            
            if (data.success && data.skills) {
                skillsList.innerHTML = '';
                data.skills.forEach(addSkill);
            } else {
                alert(`Error: ${data.error || 'Could not extract skills.'}`);
            }
        } catch (error) {
            alert('An error occurred while extracting skills.');
        } finally {
            extractSkillsBtn.textContent = '🤖 Auto-extract from Resume';
            extractSkillsBtn.disabled = false;
        }
    });

    // Handle roadmap generation
    generateRoadmapBtn.addEventListener('click', async () => {
        const role = jobRole.value;
        if (!role) {
            alert('Please select a target job role.');
            return;
        }
        if (!resumeInput.dataset.sessionId) {
            alert('Please upload a resume first!');
            return;
        }
        const skills = Array.from(skillsList.querySelectorAll('span')).map(s => s.textContent);
        if (skills.length === 0) {
            alert('Please add or extract some skills first.');
            return;
        }

        loading.style.display = 'block';
        roadmapContainer.style.display = 'none';
        generateRoadmapBtn.disabled = true;
        generateRoadmapBtn.style.animationPlayState = 'paused';


        try {
            const response = await fetch('/generate-roadmap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, session_id: resumeInput.dataset.sessionId, skills })
            });
            const data = await response.json();
            
            if (data.success) {
                displayRoadmap(data.roadmap);
            } else {
                alert(`Error: ${data.error || 'Could not generate roadmap.'}`);
            }
        } catch (error) {
            alert('An error occurred while generating the roadmap.');
        } finally {
            loading.style.display = 'none';
            generateRoadmapBtn.disabled = false;
            generateRoadmapBtn.style.animationPlayState = 'running';
        }
    });

    // Updated function to display the roadmap with staggered animations
    function displayRoadmap(roadmapData) {
        roadmapContainer.style.display = 'block';
        roadmapList.innerHTML = '';

        if (!roadmapData || roadmapData.length === 0) {
            roadmapList.innerHTML = '<p>No learning path could be generated. You may already possess all the required skills for this role!</p>';
            return;
        }

        let itemCounter = 0;
        roadmapData.forEach(phase => {
            const phaseDiv = document.createElement('div');
            phaseDiv.className = 'timeline-item phase-header';
            phaseDiv.style.animationDelay = `${itemCounter * 150}ms`;
            itemCounter++;
            phaseDiv.innerHTML = `
                <div class="timeline-icon">📖</div>
                <div class="timeline-content">
                    <h3>${phase.phase}</h3>
                </div>
            `;
            roadmapList.appendChild(phaseDiv);

            phase.skills.forEach(item => {
                const skillDiv = document.createElement('div');
                skillDiv.className = 'timeline-item skill-item';
                skillDiv.style.animationDelay = `${itemCounter * 150}ms`;
                itemCounter++;
                skillDiv.innerHTML = `
                    <div class="timeline-icon">💡</div>
                    <div class="timeline-content">
                        <h4>${item.skill}</h4>
                        ${item.course.title !== 'N/A' ? `
                        <div class="course-info">
                            <p><strong>Recommended Course:</strong> <a href="${item.course.url}" target="_blank" rel="noopener noreferrer">${item.course.title}</a></p>
                            <p><strong>Platform:</strong> ${item.course.platform}</p>
                            <p><strong>Reason:</strong> ${item.course.reason}</p>
                        </div>
                        ` : ''}
                    </div>
                `;
                roadmapList.appendChild(skillDiv);
            });
        });
    }
});