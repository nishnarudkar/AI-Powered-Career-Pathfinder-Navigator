document.addEventListener('DOMContentLoaded', () => {
    // Initialize elements
    const resumeInput = document.getElementById('resume-input');
    const uploadArea = document.getElementById('upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const skillInput = document.getElementById('skill-input');
    const addSkillBtn = document.getElementById('add-skill');
    const extractSkillsBtn = document.getElementById('extract-skills');
    const readinessResults = document.getElementById('readiness-results');
    const readinessAssessment = document.getElementById('readiness-assessment');
    const selectedRoleName = document.getElementById('selected-role-name');
    const industryEvaluation = document.getElementById('industry-evaluation');
    const industryAssessment = document.getElementById('industry-assessment');
    const skillsList = document.getElementById('skills-list');
    const jobRole = document.getElementById('job-role');
    const generateRoadmapBtn = document.getElementById('generate-roadmap');
    const loading = document.getElementById('loading');
    const roadmapContainer = document.getElementById('roadmap-container');
    const roadmapList = document.getElementById('roadmap-list');
    const resourcesContainer = document.getElementById('resources-container');
    const resources = document.getElementById('resources');
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tippy(tooltip, {
            content: tooltip.getAttribute('data-tooltip'),
            placement: 'top',
            animation: 'scale',
        });
    });

    // Debug: Check if all elements are found
    console.log('Elements found:');
    console.log('generateRoadmapBtn:', generateRoadmapBtn);
    console.log('jobRole:', jobRole);
    console.log('skillsList:', skillsList);

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
            showMessage('Please upload a resume first or add skills manually.', 'warning');
            return;
        }

        try {
            const response = await fetch('/extract-skills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: resumeInput.dataset.sessionId })
            });
            const data = await response.json();

            if (data.success) {
                skillsList.innerHTML = '';
                data.skills.forEach(skill => addSkillToList(skill));
                showMessage(`Extracted ${data.skills.length} skills from your resume!`, 'success');
            } else {
                showMessage(data.error || 'Failed to extract skills', 'warning');
            }
        } catch (error) {
            showMessage('Error extracting skills. Please try again.', 'warning');
        }
    });

    // Target role readiness assessment function
    async function assessTargetRoleReadiness(targetRole) {
        console.log('assessTargetRoleReadiness called with:', targetRole);
        
        const skills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent
        );
        console.log('Skills for assessment:', skills);

        if (skills.length === 0) {
            showMessage('Please add some skills first or extract them from your resume.', 'warning');
            return;
        }

        try {
            const readinessResultsContainer = document.getElementById('readiness-results');
            readinessResultsContainer.style.display = 'none'; // Hide the target role assessment
            readinessAssessment.innerHTML = '<div class="loading">🔄 Assessing readiness for ' + targetRole.replace('-', ' ') + '...</div>';

            console.log('Making request to backend for role:', targetRole);
            const response = await fetch('/assess-target-role-readiness', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    skills: skills,
                    target_role: targetRole
                })
            });
            const data = await response.json();
            console.log('Backend response for role', targetRole, ':', data);

            if (data.success) {
                console.log('Role assessment successful, displaying results for:', targetRole);
                // Don't display target role readiness, just enable button
                displayTargetRoleReadiness(data.role_readiness.role_assessment);
                
                // Always display industry evaluation if available
                if (data.industry_evaluation) {
                    displayIndustryEvaluation(data.industry_evaluation, targetRole);
                } else {
                    console.log('No industry evaluation available for role:', targetRole);
                    industryEvaluation.style.display = 'none';
                }
                
                showMessage('Role readiness assessment complete!', 'success');
            } else {
                console.log('Role assessment failed:', data.error);
                showMessage(data.error || 'Failed to assess role readiness', 'warning');
                const readinessResultsContainer = document.getElementById('readiness-results');
                readinessResultsContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error in assessTargetRoleReadiness:', error);
            showMessage('Error assessing role readiness. Please try again.', 'warning');
            const readinessResultsContainer = document.getElementById('readiness-results');
            readinessResultsContainer.style.display = 'none';
        }
    }

    async function displayTargetRoleReadiness(roleAssessment) {
        // Don't display the target role readiness in the readiness-assessment div
        // Just enable the roadmap button
        generateRoadmapBtn.disabled = false;
        generateRoadmapBtn.innerHTML = '✨ Generate My Learning Roadmap';
        console.log('Button enabled after role assessment:', generateRoadmapBtn.disabled);
    }

    function getReadinessClass(label) {
        if (label.includes('Ready')) return 'ready';
        if (label.includes('Workable')) return 'workable';
        return 'needs-foundation';
    }

    function formatRoleName(roleName) {
        return roleName.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    function displayIndustryEvaluation(evaluation, targetRole) {
        const industryEvaluationDiv = document.getElementById('industry-evaluation');
        const industryAssessmentDiv = document.getElementById('industry-assessment');
        
        if (!industryEvaluationDiv || !industryAssessmentDiv) {
            console.error('Industry evaluation elements not found');
            return;
        }

        const overallScore = Math.round(evaluation.overall_score * 100);
        const scoreClass = overallScore >= 80 ? 'high' : (overallScore >= 60 ? 'medium' : 'low');
        
        const evaluationHtml = `
            <div class="industry-overview">
                <div>
                    <h4>Overall Industry Readiness</h4>
                    <div class="industry-overall-score ${scoreClass}">${overallScore}%</div>
                    <div class="industry-readiness-level ${scoreClass}">${evaluation.readiness_level}</div>
                </div>
            </div>

            <div class="skill-breakdown">
                ${evaluation.breakdown.map(category => {
                    const categoryScore = Math.round(category.score * 100);
                    const categoryClass = categoryScore >= 80 ? 'high' : (categoryScore >= 60 ? 'medium' : 'low');
                    
                    return `
                        <div class="skill-category">
                            <div class="category-header">
                                <div class="category-title">${category.category}</div>
                                <div class="category-score ${categoryClass}">${categoryScore}%</div>
                            </div>
                            
                            ${category.present_skills && category.present_skills.length > 0 ? `
                                <div class="skills-present">
                                    <div class="skills-label">✅ Present Skills:</div>
                                    <div class="skills-list">
                                        ${category.present_skills.map(skill => `<span class="skill-tag present">${skill}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${category.missing_critical && category.missing_critical.length > 0 ? `
                                <div class="skills-missing">
                                    <div class="skills-label">❌ Missing Skills:</div>
                                    <div class="skills-list">
                                        ${category.missing_critical.map(skill => `<span class="skill-tag missing">${skill}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            
                            <div class="category-notes">${category.notes}</div>
                        </div>
                    `;
                }).join('')}
            </div>

            ${evaluation.recommendations && evaluation.recommendations.length > 0 ? `
                <div class="recommendations-section">
                    <h4>🎯 Priority Recommendations</h4>
                    ${evaluation.recommendations.map(rec => `
                        <div class="recommendation-item">
                            <div class="rec-priority">Priority ${rec.priority}</div>
                            <div class="rec-skill">${rec.skill}</div>
                            <div class="rec-action">${rec.action}</div>
                            <div class="rec-timeline">Timeline: ${rec.timeline} | ${rec.impact}</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            ${evaluation.strengths && evaluation.strengths.length > 0 ? `
                <div class="strengths-section">
                    <h4>💪 Your Strengths</h4>
                    ${evaluation.strengths.map(strength => `
                        <div class="strength-item">${strength}</div>
                    `).join('')}
                </div>
            ` : ''}

            ${evaluation.next_steps ? `
                <div class="next-steps">
                    <strong>🗺️ Next Steps:</strong> ${evaluation.next_steps}
                </div>
            ` : ''}
        `;

        industryAssessmentDiv.innerHTML = evaluationHtml;
        industryEvaluationDiv.style.display = 'block';
    }

    function addSkillToList(skill) {
        const existingSkills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent.toLowerCase()
        );
        
        if (existingSkills.includes(skill.toLowerCase())) {
            return; // Skip duplicates
        }

        const li = document.createElement('li');
        li.className = 'skill-tag';
        li.innerHTML = `
            <span>${skill}</span>
            <button class="skill-remove" onclick="removeSkill(this)">×</button>
        `;
        skillsList.appendChild(li);
    }

    // Roadmap generation
    async function generateRoadmap() {
        console.log('Generate roadmap clicked!');
        console.log('Button disabled:', generateRoadmapBtn.disabled);
        console.log('Job role value:', jobRole.value);
        
        const role = jobRole.value;
        if (!role) {
            showMessage('Please select a target job role.', 'warning');
            console.log('No role selected, stopping');
            return;
        }

        const skills = Array.from(skillsList.children).map(li => 
            li.querySelector('span').textContent
        );
        console.log('Skills found:', skills);

        if (skills.length === 0) {
            showMessage('Please add some skills first!', 'warning');
            console.log('No skills found, stopping');
            return;
        }

        console.log('About to start roadmap generation...');

        // Create manual session if no session exists but skills are present
        if (!resumeInput.dataset.sessionId) {
            console.log('No session ID, creating manual session...');
            await createManualSession();
            if (!resumeInput.dataset.sessionId) {
                showMessage('Failed to create session for manual skills!', 'warning');
                console.log('Failed to create session');
                return;
            }
            console.log('Manual session created:', resumeInput.dataset.sessionId);
        }

        console.log('Showing loading indicator...');
        loading.style.display = 'block';
        roadmapContainer.style.display = 'none';
        generateRoadmapBtn.disabled = true;

        try {
            console.log('Making request to /generate-roadmap...');
            const response = await fetch('/generate-roadmap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    skills, 
                    role, 
                    session_id: resumeInput.dataset.sessionId
                })
            });
            console.log('Response received:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                console.log('Success! Displaying roadmap...');
                displayRoadmap(data);
            } else {
                console.log('Error from server:', data.error);
                showMessage(`Error: ${data.error}`, 'warning');
            }
        } catch (error) {
            console.log('Network error:', error);
            showMessage(`Network error: ${error.message}`, 'warning');
        } finally {
            console.log('Hiding loading indicator...');
            loading.style.display = 'none';
            generateRoadmapBtn.disabled = false;
        }
    }

    function displayRoadmap(data) {
        roadmapContainer.style.display = 'block';
        roadmapList.innerHTML = '';
        resources.textContent = data.resources || 'No resources provided.';
        resourcesContainer.style.display = 'block';

        // Display time estimates if available
        const timeEstimatesContainer = document.getElementById('time-estimates-container');
        if (data.time_estimates && timeEstimatesContainer) {
            const overallTimeFrame = document.getElementById('overall-time-frame');
            const totalHours = document.getElementById('total-hours');
            const bufferedHours = document.getElementById('buffered-hours');
            const weeklyCommitment = document.getElementById('weekly-commitment');
            
            if (overallTimeFrame) overallTimeFrame.textContent = data.time_estimates.overall_time_frame || 'Time estimates not available';
            if (totalHours) totalHours.textContent = `Base time: ${data.time_estimates.overall_total_hours || 0}h`;
            if (bufferedHours) bufferedHours.textContent = `With buffer: ${data.time_estimates.overall_buffered_hours || 0}h`;
            if (weeklyCommitment) weeklyCommitment.textContent = `Weekly commitment: ${data.time_estimates.weekly_hours || 8}h`;
            
            timeEstimatesContainer.style.display = 'block';
        }

        if (data.roadmap && data.roadmap.length > 0) {
            data.roadmap.forEach((phase, phaseIndex) => {
                const phaseHeader = document.createElement('h3');
                phaseHeader.className = 'phase-header';
                phaseHeader.textContent = phase.phase;
                roadmapList.appendChild(phaseHeader);

                // Add phase time information
                if (phase.phase_time_frame) {
                    const phaseTimeDiv = document.createElement('div');
                    phaseTimeDiv.className = 'phase-time-info';
                    phaseTimeDiv.textContent = phase.phase_time_frame;
                    roadmapList.appendChild(phaseTimeDiv);
                }

                phase.skills.forEach((item, itemIndex) => {
                    const li = document.createElement('li');
                    li.className = 'roadmap-item';
                    li.style.animationDelay = `${(phaseIndex * phase.skills.length + itemIndex) * 0.1}s`;
                    
                    const skillSpan = document.createElement('span');
                    skillSpan.textContent = item.skill;
                    
                    // Add estimated hours if available
                    if (item.est_hours) {
                        const hoursSpan = document.createElement('span');
                        hoursSpan.className = 'skill-hours';
                        hoursSpan.textContent = `(~${item.est_hours}h)`;
                        skillSpan.appendChild(hoursSpan);
                    }
                    
                    li.appendChild(skillSpan);

                    if (item.course.title !== 'N/A') {
                        const courseDiv = document.createElement('div');
                        courseDiv.className = 'course-info';
                        
                        // Show duration if available, otherwise show platform
                        const timeInfo = item.course.duration && item.course.duration !== 'N/A' 
                            ? item.course.duration 
                            : (item.course.platform !== 'N/A' ? item.course.platform : 'Self-paced');
                        
                        // Create course paragraph with proper link handling
                        const courseParagraph = document.createElement('p');
                        const courseLabel = document.createElement('strong');
                        courseLabel.textContent = 'Course: ';
                        courseParagraph.appendChild(courseLabel);
                        
                        // Create course link or text based on URL availability
                        if (item.course.url && item.course.url.trim() !== '' && item.course.url !== 'N/A') {
                            // Create clickable link
                            const courseLink = document.createElement('a');
                            let courseUrl = item.course.url.trim();
                            if (!courseUrl.startsWith('http://') && !courseUrl.startsWith('https://')) {
                                courseUrl = 'https://' + courseUrl;
                            }
                            courseLink.href = courseUrl;
                            courseLink.target = '_blank';
                            courseLink.rel = 'noopener noreferrer';
                            courseLink.textContent = item.course.title;
                            courseParagraph.appendChild(courseLink);
                        } else {
                            // Just add course title as text
                            const courseText = document.createTextNode(item.course.title);
                            courseParagraph.appendChild(courseText);
                        }
                        
                        // Add time info
                        const timeText = document.createTextNode(` (${timeInfo})`);
                        courseParagraph.appendChild(timeText);
                        
                        // Create reason paragraph
                        const reasonParagraph = document.createElement('p');
                        const reasonLabel = document.createElement('strong');
                        reasonLabel.textContent = 'Why: ';
                        reasonParagraph.appendChild(reasonLabel);
                        const reasonText = document.createTextNode(item.course.reason);
                        reasonParagraph.appendChild(reasonText);
                        
                        // Append paragraphs to course div
                        courseDiv.appendChild(courseParagraph);
                        courseDiv.appendChild(reasonParagraph);
                        
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

    // Job role selection listener - assess readiness for target role
    jobRole.addEventListener('change', async () => {
        const selectedRole = jobRole.value;
        console.log('Role changed to:', selectedRole);
        
        if (!validJobRoles.includes(selectedRole)) {
            showMessage('Please select a valid job role.', 'warning');
            jobRole.value = '';
            const readinessResultsContainer = document.getElementById('readiness-results');
            readinessResultsContainer.style.display = 'none';
            industryEvaluation.style.display = 'none';
            generateRoadmapBtn.disabled = true;
            return;
        }
        
        if (selectedRole) {
            selectedRoleName.textContent = selectedRole.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            console.log('About to assess role readiness for:', selectedRole);
            
            // Clear previous assessments first
            readinessAssessment.innerHTML = '';
            industryEvaluation.style.display = 'none';
            
            // Get current skills
            const currentSkills = Array.from(skillsList.children).map(li => 
                li.querySelector('span').textContent
            );
            console.log('Current skills for assessment:', currentSkills);
            
            if (currentSkills.length > 0) {
                await assessTargetRoleReadiness(selectedRole);
            } else {
                showMessage('Please add some skills first to see your role readiness assessment.', 'warning');
                const readinessResultsContainer = document.getElementById('readiness-results');
                readinessResultsContainer.style.display = 'none';
                generateRoadmapBtn.disabled = true;
            }
        } else {
            const readinessResultsContainer = document.getElementById('readiness-results');
            readinessResultsContainer.style.display = 'none';
            industryEvaluation.style.display = 'none';
            generateRoadmapBtn.disabled = true;
        }
    });

    // Add event listener at the very end to ensure all elements are ready
    generateRoadmapBtn.addEventListener('click', () => {
        console.log('Generate roadmap button clicked!');
        generateRoadmap();
    });

    // Global test function for onclick
    window.testClick = function() {
        console.log('Test click function called!');
        generateRoadmap();
    };
});
