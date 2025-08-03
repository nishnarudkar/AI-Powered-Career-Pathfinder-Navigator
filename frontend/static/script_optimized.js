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
    const forceRefreshBtn = document.getElementById('force-refresh');
    const performanceTestBtn = document.getElementById('performance-test');
    const loading = document.getElementById('loading');
    const roadmapContainer = document.getElementById('roadmap-container');
    const roadmapList = document.getElementById('roadmap-list');
    const resourcesContainer = document.getElementById('resources-container');
    const resources = document.getElementById('resources');
    const performanceInfo = document.getElementById('performance-info');

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
                resumeInput.dataset.sessionId = data.session_id;
                fileName.textContent = `✅ ${file.name}`;
                fileName.style.color = '#48bb78';
                showMessage('Resume uploaded successfully!', 'success');
            } else {
                fileName.textContent = `❌ ${file.name}`;
                fileName.style.color = '#f56565';
                showMessage(data.error || 'Upload failed', 'warning');
            }
        } catch (error) {
            fileName.textContent = `❌ Error uploading ${file.name}`;
            fileName.style.color = '#f56565';
        }
    }

    // Handle skill addition with enhanced UI and space-separated parsing
    function addSkill(skillText) {
        if (!skillText.trim()) return;
        
        // Parse space-separated skills
        const skills = skillText.split(/\s+/).filter(skill => skill.trim());
        
        // Get existing skills to check for duplicates
        const existingSkills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent.toLowerCase()
        );
        
        skills.forEach(skill => {
            const cleanSkill = skill.trim();
            if (!cleanSkill) return;
            
            // Check for duplicates
            if (existingSkills.includes(cleanSkill.toLowerCase())) {
                showMessage(`Skill "${cleanSkill}" already added!`, 'warning');
                return;
            }
            
            const li = document.createElement('li');
            li.className = 'skill-tag';
            li.innerHTML = `
                <span>${cleanSkill}</span>
                <button class="skill-remove" onclick="removeSkill(this)">×</button>
            `;
            skillsList.appendChild(li);
            existingSkills.push(cleanSkill.toLowerCase()); // Add to existing skills to prevent duplicates within the same input
        });
        
        // If skills were added manually, create a session for them
        if (skills.length > 0 && !resumeInput.dataset.sessionId) {
            createManualSession();
        }
    }
    
    // Create a session for manual skills entry
    async function createManualSession() {
        try {
            const allSkills = Array.from(skillsList.children).map(li => 
                li.querySelector('span').textContent
            );
            
            const response = await fetch('/create-manual-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skills: allSkills.join(' ') })
            });
            
            const data = await response.json();
            if (data.success) {
                resumeInput.dataset.sessionId = data.session_id;
                showMessage('Manual skills session created!', 'success');
            }
        } catch (error) {
            console.error('Error creating manual session:', error);
        }
    }
    
    // Remove skill and update session
    function removeSkill(button) {
        button.parentElement.remove();
        // Update manual session if it exists
        if (resumeInput.dataset.sessionId && resumeInput.dataset.sessionId.startsWith('manual_session_')) {
            createManualSession();
        }
    }
    
    // Make removeSkill globally available
    window.removeSkill = removeSkill;

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
            const response = await fetch('/extract-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: resumeInput.dataset.sessionId })
            });
            const data = await response.json();

            if (data.success && data.skills) {
                // Clear existing skills
                skillsList.innerHTML = '';
                
                // Add extracted skills
                data.skills.forEach(skill => {
                    const li = document.createElement('li');
                    li.className = 'skill-tag';
                    li.innerHTML = `
                        <span>${skill}</span>
                        <button class="skill-remove" onclick="removeSkill(this)">×</button>
                    `;
                    skillsList.appendChild(li);
                });
                
                showMessage(`Extracted ${data.skills.length} skills from your resume!`, 'success');
            } else {
                showMessage('Failed to extract skills. Please try adding them manually.', 'warning');
            }
        } catch (error) {
            showMessage('Error extracting skills', 'warning');
        }
    });

    // Enhanced roadmap generation
    async function generateRoadmap(forceRefresh = false) {
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

        // Create manual session if no session exists but skills are present
        if (!resumeInput.dataset.sessionId) {
            await createManualSession();
            if (!resumeInput.dataset.sessionId) {
                showMessage('Failed to create session for manual skills!', 'warning');
                return;
            }
        }

        loading.style.display = 'block';
        roadmapContainer.style.display = 'none';
        performanceInfo.style.display = 'none';
        generateRoadmapBtn.disabled = true;
        if (forceRefreshBtn) forceRefreshBtn.disabled = true;

        const startTime = Date.now();

        try {
            const response = await fetch('/generate-roadmap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    skills, 
                    role, 
                    session_id: resumeInput.dataset.sessionId,
                    force_refresh: forceRefresh
                })
            });
            const data = await response.json();
            
            const endTime = Date.now();
            const totalTime = (endTime - startTime) / 1000;
            
            if (data.success) {
                displayRoadmap(data);
                displayPerformanceMetrics(data.performance, totalTime);
            } else {
                showMessage(`Error: ${data.error}`, 'warning');
            }
        } catch (error) {
            showMessage(`Network error: ${error.message}`, 'warning');
        } finally {
            loading.style.display = 'none';
            generateRoadmapBtn.disabled = false;
            if (forceRefreshBtn) forceRefreshBtn.disabled = false;
        }
    }

    generateRoadmapBtn.addEventListener('click', () => generateRoadmap(false));
    
    if (forceRefreshBtn) {
        forceRefreshBtn.addEventListener('click', () => {
            showMessage('Forcing refresh - bypassing cache...', 'info');
            generateRoadmap(true);
        });
    }

    if (performanceTestBtn) {
        performanceTestBtn.addEventListener('click', async () => {
            showMessage('Running performance test...', 'info');
            
            try {
                const response = await fetch('/performance-test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input: 'Test engineer with Python, SQL, and React experience',
                        role: 'Data Scientist'
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    const perf = data.performance_comparison;
                    showMessage(
                        `Performance Test Results:\\n` +
                        `First run: ${perf.optimized_time}s\\n` +
                        `Cached run: ${perf.cached_time}s\\n` +
                        `Cache speedup: ${perf.cache_speedup}x`, 
                        'success'
                    );
                    
                    // Show detailed metrics
                    displayPerformanceMetrics(perf.performance_summary, perf.optimized_time);
                } else {
                    showMessage('Performance test failed', 'warning');
                }
            } catch (error) {
                showMessage(`Performance test error: ${error.message}`, 'warning');
            }
        });
    }

    function displayPerformanceMetrics(performance, totalTime) {
        if (!performance || !performanceInfo) return;
        
        const generationTime = document.getElementById('generation-time');
        const cacheRatio = document.getElementById('cache-ratio');
        const llmTime = document.getElementById('llm-time');
        
        if (generationTime) {
            generationTime.textContent = `${performance.generation_time || totalTime}s`;
        }
        
        if (cacheRatio) {
            const ratio = performance.cache_hit_ratio || 0;
            cacheRatio.textContent = `${(ratio * 100).toFixed(1)}%`;
        }
        
        if (llmTime && performance.step_timings) {
            const llmCallTime = performance.step_timings.llm_call || 0;
            llmTime.textContent = `${llmCallTime}s`;
        }
        
        performanceInfo.style.display = 'block';
    }

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
