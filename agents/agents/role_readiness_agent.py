"""
Role Readiness Assessment Agent

Analyzes user skills against job role requirements and provides readiness scores,
missing skills analysis, and quick-win recommendations.
"""

import json
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class SkillImportance(Enum):
    MUST = "must"
    NICE = "nice"

class ReadinessLevel(Enum):
    READY = "Ready / Strong fit"
    WORKABLE = "Workable with targeted upskilling"
    NEEDS_FOUNDATION = "Needs foundation"

@dataclass
class UserSkill:
    skill: str
    level: int  # 0-3

@dataclass
class RequiredSkill:
    skill: str
    target_level: int  # 2 or 3
    importance: SkillImportance

@dataclass
class MissingSkill:
    skill: str
    current_level: int
    target_level: int
    gap_degree: int
    importance: SkillImportance

@dataclass
class RoleMatch:
    role_name: str
    readiness_score: float
    readiness_label: str
    missing_skills: List[Dict]
    quick_win_recommendations: List[str]

class RoleReadinessAgent:
    def __init__(self):
        self.role_catalog = self._initialize_role_catalog()
        self.cache = {}
        self.course_catalog = self._initialize_course_catalog()
    
    def _initialize_role_catalog(self) -> Dict[str, List[RequiredSkill]]:
        """Initialize static role catalog with required skills"""
        return {
            "data-scientist": [
                RequiredSkill("python", 3, SkillImportance.MUST),
                RequiredSkill("sql", 3, SkillImportance.MUST),
                RequiredSkill("statistics", 3, SkillImportance.MUST),
                RequiredSkill("machine-learning", 3, SkillImportance.MUST),
                RequiredSkill("pandas", 3, SkillImportance.MUST),
                RequiredSkill("numpy", 2, SkillImportance.MUST),
                RequiredSkill("scikit-learn", 2, SkillImportance.MUST),
                RequiredSkill("data-visualization", 2, SkillImportance.MUST),
                RequiredSkill("jupyter", 2, SkillImportance.NICE),
                RequiredSkill("tensorflow", 2, SkillImportance.NICE),
                RequiredSkill("pytorch", 2, SkillImportance.NICE),
                RequiredSkill("deep-learning", 2, SkillImportance.NICE),
                RequiredSkill("r", 2, SkillImportance.NICE),
            ],
            "ml-engineer": [
                RequiredSkill("python", 3, SkillImportance.MUST),
                RequiredSkill("machine-learning", 3, SkillImportance.MUST),
                RequiredSkill("tensorflow", 3, SkillImportance.MUST),
                RequiredSkill("pytorch", 2, SkillImportance.MUST),
                RequiredSkill("deep-learning", 3, SkillImportance.MUST),
                RequiredSkill("docker", 2, SkillImportance.MUST),
                RequiredSkill("kubernetes", 2, SkillImportance.MUST),
                RequiredSkill("sql", 2, SkillImportance.MUST),
                RequiredSkill("git", 2, SkillImportance.MUST),
                RequiredSkill("linux", 2, SkillImportance.MUST),
                RequiredSkill("aws", 2, SkillImportance.NICE),
                RequiredSkill("mlops", 2, SkillImportance.NICE),
                RequiredSkill("scikit-learn", 2, SkillImportance.NICE),
            ],
            "ai-engineer": [
                RequiredSkill("python", 3, SkillImportance.MUST),
                RequiredSkill("deep-learning", 3, SkillImportance.MUST),
                RequiredSkill("tensorflow", 3, SkillImportance.MUST),
                RequiredSkill("pytorch", 2, SkillImportance.MUST),
                RequiredSkill("machine-learning", 3, SkillImportance.MUST),
                RequiredSkill("neural-networks", 3, SkillImportance.MUST),
                RequiredSkill("computer-vision", 2, SkillImportance.MUST),
                RequiredSkill("nlp", 2, SkillImportance.MUST),
                RequiredSkill("transformers", 2, SkillImportance.NICE),
                RequiredSkill("llm", 2, SkillImportance.NICE),
                RequiredSkill("hugging-face", 2, SkillImportance.NICE),
            ],
            "cloud-architect": [
                RequiredSkill("aws", 3, SkillImportance.MUST),
                RequiredSkill("azure", 2, SkillImportance.MUST),
                RequiredSkill("docker", 3, SkillImportance.MUST),
                RequiredSkill("kubernetes", 3, SkillImportance.MUST),
                RequiredSkill("terraform", 2, SkillImportance.MUST),
                RequiredSkill("linux", 3, SkillImportance.MUST),
                RequiredSkill("networking", 2, SkillImportance.MUST),
                RequiredSkill("security", 2, SkillImportance.MUST),
                RequiredSkill("monitoring", 2, SkillImportance.MUST),
                RequiredSkill("gcp", 2, SkillImportance.NICE),
                RequiredSkill("ansible", 2, SkillImportance.NICE),
                RequiredSkill("jenkins", 2, SkillImportance.NICE),
            ],
            "devops-engineer": [
                RequiredSkill("linux", 3, SkillImportance.MUST),
                RequiredSkill("docker", 3, SkillImportance.MUST),
                RequiredSkill("kubernetes", 2, SkillImportance.MUST),
                RequiredSkill("git", 3, SkillImportance.MUST),
                RequiredSkill("ci-cd", 3, SkillImportance.MUST),
                RequiredSkill("jenkins", 2, SkillImportance.MUST),
                RequiredSkill("terraform", 2, SkillImportance.MUST),
                RequiredSkill("aws", 2, SkillImportance.MUST),
                RequiredSkill("bash", 2, SkillImportance.MUST),
                RequiredSkill("monitoring", 2, SkillImportance.MUST),
                RequiredSkill("ansible", 2, SkillImportance.NICE),
                RequiredSkill("python", 2, SkillImportance.NICE),
                RequiredSkill("azure", 2, SkillImportance.NICE),
            ],
            "full-stack-developer": [
                RequiredSkill("javascript", 3, SkillImportance.MUST),
                RequiredSkill("html", 3, SkillImportance.MUST),
                RequiredSkill("css", 3, SkillImportance.MUST),
                RequiredSkill("react", 3, SkillImportance.MUST),
                RequiredSkill("nodejs", 3, SkillImportance.MUST),
                RequiredSkill("sql", 2, SkillImportance.MUST),
                RequiredSkill("git", 2, SkillImportance.MUST),
                RequiredSkill("rest-api", 2, SkillImportance.MUST),
                RequiredSkill("express", 2, SkillImportance.MUST),
                RequiredSkill("typescript", 2, SkillImportance.NICE),
                RequiredSkill("vuejs", 2, SkillImportance.NICE),
                RequiredSkill("angular", 2, SkillImportance.NICE),
                RequiredSkill("mongodb", 2, SkillImportance.NICE),
                RequiredSkill("postgresql", 2, SkillImportance.NICE),
            ],
            "cybersecurity-analyst": [
                RequiredSkill("security", 3, SkillImportance.MUST),
                RequiredSkill("networking", 3, SkillImportance.MUST),
                RequiredSkill("linux", 2, SkillImportance.MUST),
                RequiredSkill("windows", 2, SkillImportance.MUST),
                RequiredSkill("incident-response", 2, SkillImportance.MUST),
                RequiredSkill("vulnerability-assessment", 2, SkillImportance.MUST),
                RequiredSkill("penetration-testing", 2, SkillImportance.MUST),
                RequiredSkill("siem", 2, SkillImportance.MUST),
                RequiredSkill("python", 2, SkillImportance.NICE),
                RequiredSkill("powershell", 2, SkillImportance.NICE),
                RequiredSkill("forensics", 2, SkillImportance.NICE),
            ],
            "product-manager": [
                RequiredSkill("product-strategy", 3, SkillImportance.MUST),
                RequiredSkill("user-research", 2, SkillImportance.MUST),
                RequiredSkill("data-analysis", 2, SkillImportance.MUST),
                RequiredSkill("roadmap-planning", 3, SkillImportance.MUST),
                RequiredSkill("agile", 2, SkillImportance.MUST),
                RequiredSkill("stakeholder-management", 3, SkillImportance.MUST),
                RequiredSkill("market-research", 2, SkillImportance.MUST),
                RequiredSkill("sql", 2, SkillImportance.NICE),
                RequiredSkill("excel", 2, SkillImportance.NICE),
                RequiredSkill("jira", 2, SkillImportance.NICE),
                RequiredSkill("figma", 2, SkillImportance.NICE),
            ]
        }
    
    def _initialize_course_catalog(self) -> Dict[str, Dict]:
        """Initialize enhanced course catalog with IDs, duration, and micro-tasks"""
        return {
            "python": {
                "courses": [
                    {"id": "PY001", "name": "Python for Everybody Specialization", "provider": "Coursera", "duration": "40h"},
                    {"id": "PY002", "name": "Complete Python Bootcamp", "provider": "Udemy", "duration": "22h"},
                    {"id": "PY003", "name": "Python Crash Course", "provider": "FreeCodeCamp", "duration": "4h"}
                ],
                "micro_tasks": [
                    "Write a script to read/write CSV files using pandas (1-2h)",
                    "Build a simple calculator with functions and error handling (2h)",
                    "Create a web scraper using requests and BeautifulSoup (3h)"
                ]
            },
            "sql": {
                "courses": [
                    {"id": "SQL001", "name": "SQL for Data Science", "provider": "Coursera", "duration": "15h"},
                    {"id": "SQL002", "name": "Complete SQL Bootcamp", "provider": "Udemy", "duration": "12h"},
                    {"id": "SQL003", "name": "SQL Tutorial", "provider": "W3Schools", "duration": "6h"}
                ],
                "micro_tasks": [
                    "Write and run 10 SQL queries covering JOINs and aggregations (2h)",
                    "Design a simple database schema and implement it (3h)",
                    "Optimize 5 slow queries using indexes and query analysis (2h)"
                ]
            },
            "machine-learning": {
                "courses": [
                    {"id": "ML001", "name": "Machine Learning Course", "provider": "Stanford/Coursera", "duration": "60h"},
                    {"id": "ML002", "name": "Applied Machine Learning", "provider": "MIT", "duration": "45h"},
                    {"id": "ML003", "name": "ML Crash Course", "provider": "Google", "duration": "15h"}
                ],
                "micro_tasks": [
                    "Implement linear regression from scratch and evaluate it (3h)",
                    "Build a classification model using scikit-learn on iris dataset (2h)",
                    "Create a simple recommendation system using collaborative filtering (4h)"
                ]
            },
            "statistics": {
                "courses": [
                    {"id": "STAT001", "name": "Statistics for Data Science", "provider": "Coursera", "duration": "25h"},
                    {"id": "STAT002", "name": "Intro to Statistics", "provider": "Khan Academy", "duration": "15h"},
                    {"id": "STAT003", "name": "Statistical Thinking", "provider": "DataCamp", "duration": "4h"}
                ],
                "micro_tasks": [
                    "Do a 2-hour crash course on hypothesis testing and probability basics (2h)",
                    "Calculate confidence intervals for 3 different datasets (1h)",
                    "Perform A/B test analysis on sample e-commerce data (3h)"
                ]
            },
            "javascript": {
                "courses": [
                    {"id": "JS001", "name": "JavaScript: The Complete Guide", "provider": "Udemy", "duration": "52h"},
                    {"id": "JS002", "name": "JavaScript Algorithms and Data Structures", "provider": "FreeCodeCamp", "duration": "300h"},
                    {"id": "JS003", "name": "Modern JavaScript Course", "provider": "Coursera", "duration": "40h"}
                ],
                "micro_tasks": [
                    "Build a to-do app with local storage using vanilla JS (4h)",
                    "Create 5 different array manipulation functions (2h)",
                    "Implement async/await patterns with API calls (3h)"
                ]
            },
            "react": {
                "courses": [
                    {"id": "REACT001", "name": "React - The Complete Guide", "provider": "Udemy", "duration": "48h"},
                    {"id": "REACT002", "name": "React Fundamentals", "provider": "Pluralsight", "duration": "8h"},
                    {"id": "REACT003", "name": "React Tutorial", "provider": "Official Docs", "duration": "4h"}
                ],
                "micro_tasks": [
                    "Build a simple counter app with hooks (2h)",
                    "Create a component library with 5 reusable components (4h)",
                    "Implement state management with Context API (3h)"
                ]
            },
            "docker": {
                "courses": [
                    {"id": "DOCK001", "name": "Docker Mastery", "provider": "Udemy", "duration": "19h"},
                    {"id": "DOCK002", "name": "Docker and Kubernetes", "provider": "Coursera", "duration": "35h"},
                    {"id": "DOCK003", "name": "Docker Tutorial", "provider": "Docker Docs", "duration": "6h"}
                ],
                "micro_tasks": [
                    "Containerize a simple web app and run it locally (2h)",
                    "Create a multi-stage Dockerfile for a Node.js app (2h)",
                    "Set up a development environment with docker-compose (3h)"
                ]
            },
            "aws": {
                "courses": [
                    {"id": "AWS001", "name": "AWS Cloud Practitioner", "provider": "AWS Training", "duration": "6h"},
                    {"id": "AWS002", "name": "AWS Solutions Architect", "provider": "A Cloud Guru", "duration": "30h"},
                    {"id": "AWS003", "name": "AWS Fundamentals", "provider": "Coursera", "duration": "15h"}
                ],
                "micro_tasks": [
                    "Deploy a static website using S3 and CloudFront (2h)",
                    "Create an EC2 instance and configure basic security groups (1h)",
                    "Set up a simple Lambda function with API Gateway (3h)"
                ]
            },
            "linux": {
                "courses": [
                    {"id": "LIN001", "name": "Linux Command Line Basics", "provider": "Udemy", "duration": "8h"},
                    {"id": "LIN002", "name": "Linux System Administration", "provider": "Linux Academy", "duration": "25h"},
                    {"id": "LIN003", "name": "RHCSA Certification", "provider": "Red Hat", "duration": "40h"}
                ],
                "micro_tasks": [
                    "Practice 20 essential Linux commands on a virtual machine (2h)",
                    "Write shell scripts for file management automation (3h)",
                    "Configure a basic web server using Apache or Nginx (2h)"
                ]
            },
            "kubernetes": {
                "courses": [
                    {"id": "K8S001", "name": "Kubernetes for Beginners", "provider": "Udemy", "duration": "8h"},
                    {"id": "K8S002", "name": "Certified Kubernetes Administrator", "provider": "Linux Foundation", "duration": "30h"},
                    {"id": "K8S003", "name": "Kubernetes Fundamentals", "provider": "Pluralsight", "duration": "6h"}
                ],
                "micro_tasks": [
                    "Deploy a simple app to local Kubernetes cluster (3h)",
                    "Configure ConfigMaps and Secrets for an application (2h)",
                    "Set up basic monitoring with Kubernetes dashboard (2h)"
                ]
            },
            "ci-cd": {
                "courses": [
                    {"id": "CICD001", "name": "DevOps CI/CD Pipeline", "provider": "Udemy", "duration": "12h"},
                    {"id": "CICD002", "name": "Jenkins Complete Guide", "provider": "Pluralsight", "duration": "8h"},
                    {"id": "CICD003", "name": "GitHub Actions Tutorial", "provider": "GitHub Learning Lab", "duration": "3h"}
                ],
                "micro_tasks": [
                    "Set up a basic CI/CD pipeline using GitHub Actions (3h)",
                    "Create automated tests that run on every commit (2h)",
                    "Configure deployment automation to staging environment (4h)"
                ]
            }
        }
    
    def normalize_user_skills(self, raw_skills: List[str]) -> List[UserSkill]:
        """
        Convert raw skill list to normalized UserSkill objects with levels.
        For now, assigns default level 2 to all skills. In production, this would
        use skill assessment or user input.
        """
        normalized_skills = []
        for skill in raw_skills:
            # Normalize skill name (lowercase, hyphenated)
            canonical_name = skill.lower().replace(' ', '-').replace('_', '-')
            # Default level assignment - in production this would come from assessment
            level = 2  # Assume intermediate level for existing skills
            normalized_skills.append(UserSkill(canonical_name, level))
        
        return normalized_skills
    
    def compute_readiness_score(self, user_skills: List[UserSkill], role_requirements: List[RequiredSkill]) -> Tuple[float, List[MissingSkill]]:
        """
        Compute readiness score for a role based on user skills.
        
        Returns:
            Tuple of (readiness_score, missing_skills)
        """
        # Create lookup dictionary for user skills
        user_skill_map = {skill.skill: skill.level for skill in user_skills}
        
        total_contribution = 0.0
        total_weight = 0.0
        missing_skills = []
        
        for req_skill in role_requirements:
            user_level = user_skill_map.get(req_skill.skill, 0)
            target_level = req_skill.target_level
            
            # Calculate credit (capped at 1.0)
            credit = min(user_level / target_level, 1.0) if target_level > 0 else 0.0
            
            # Calculate weight based on importance
            weight = 1.2 if req_skill.importance == SkillImportance.MUST else 1.0
            
            # Calculate contribution
            contribution = credit * weight
            
            total_contribution += contribution
            total_weight += weight
            
            # Track missing skills
            if user_level < target_level:
                gap_degree = target_level - user_level
                missing_skills.append(MissingSkill(
                    skill=req_skill.skill,
                    current_level=user_level,
                    target_level=target_level,
                    gap_degree=gap_degree,
                    importance=req_skill.importance
                ))
        
        # Calculate readiness score
        readiness_score = total_contribution / total_weight if total_weight > 0 else 0.0
        
        return readiness_score, missing_skills
    
    def get_readiness_label(self, score: float) -> str:
        """Convert readiness score to human-readable label"""
        if score >= 0.8:
            return ReadinessLevel.READY.value
        elif score >= 0.5:
            return ReadinessLevel.WORKABLE.value
        else:
            return ReadinessLevel.NEEDS_FOUNDATION.value
    
    def generate_quick_win_recommendations(self, missing_skills: List[MissingSkill]) -> List[str]:
        """
        Generate actionable quick-win recommendations with specific micro-tasks and course IDs.
        
        Returns top 2 missing "must" skills with largest gap_degree.
        """
        # Filter to "must" skills and sort by gap_degree descending
        must_skills = [skill for skill in missing_skills if skill.importance == SkillImportance.MUST]
        must_skills.sort(key=lambda x: x.gap_degree, reverse=True)
        
        recommendations = []
        
        # Take top 2 missing must skills
        for skill in must_skills[:2]:
            skill_name = skill.skill
            gap = skill.gap_degree
            current = skill.current_level
            target = skill.target_level
            
            # Check if we have detailed catalog entry for this skill
            if skill_name in self.course_catalog:
                catalog_entry = self.course_catalog[skill_name]
                
                if gap >= 2:
                    # Foundation needed - recommend course
                    best_course = catalog_entry["courses"][0]  # Take first (usually most comprehensive)
                    rec = f"Foundation needed in {skill_name.replace('-', ' ')}: Start with course {best_course['id']} - '{best_course['name']}' ({best_course['duration']}) (Level {current}→{target})"
                else:
                    # Quick upskill - recommend micro-task
                    if catalog_entry.get("micro_tasks"):
                        micro_task = catalog_entry["micro_tasks"][0]  # Take first micro-task
                        rec = f"Quick upskill in {skill_name.replace('-', ' ')}: {micro_task} (Level {current}→{target})"
                    else:
                        # Fallback to course if no micro-tasks available
                        quick_course = next((c for c in catalog_entry["courses"] if "3h" in c["duration"] or "4h" in c["duration"]), catalog_entry["courses"][-1])
                        rec = f"Quick upskill in {skill_name.replace('-', ' ')}: Complete course {quick_course['id']} - '{quick_course['name']}' ({quick_course['duration']}) (Level {current}→{target})"
            else:
                # Fallback for skills not in catalog
                skill_display = skill_name.replace('-', ' ').title()
                if gap >= 2:
                    rec = f"Foundation needed in {skill_display}: Dedicate 8-12 hours to comprehensive training through online courses or bootcamps (Level {current}→{target})"
                else:
                    rec = f"Quick upskill in {skill_display}: Spend 2-4 hours on focused practice through tutorials and hands-on projects (Level {current}→{target})"
            
            recommendations.append(rec)
        
        return recommendations
    
    def generate_cache_key(self, user_skills: List[UserSkill]) -> str:
        """Generate cache key based on user skills"""
        skill_str = "|".join([f"{skill.skill}:{skill.level}" for skill in sorted(user_skills, key=lambda x: x.skill)])
        return hashlib.md5(skill_str.encode()).hexdigest()
    
    def assess_single_role_readiness(self, user_skills: List[UserSkill], target_role: str, force_refresh: bool = False) -> Dict:
        """
        Assess user readiness for a specific target role only.
        
        Args:
            user_skills: List of UserSkill objects with normalized skill names and levels
            target_role: The specific role to assess (e.g., 'data-scientist')
            force_refresh: If True, bypass cache
            
        Returns:
            JSON structure with single role readiness assessment
        """
        # Check if role exists
        if target_role not in self.role_catalog:
            raise ValueError(f"Unknown role: {target_role}")
        
        # Check cache
        cache_key = f"{self.generate_cache_key(user_skills)}_{target_role}"
        if not force_refresh and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Assess readiness for the target role
        requirements = self.role_catalog[target_role]
        readiness_score, missing_skills = self.compute_readiness_score(user_skills, requirements)
        readiness_label = self.get_readiness_label(readiness_score)
        quick_wins = self.generate_quick_win_recommendations(missing_skills)
        
        # Convert missing skills to dict format
        missing_skills_dict = [
            {
                "skill": skill.skill,
                "current_level": skill.current_level,
                "target_level": skill.target_level,
                "gap_degree": skill.gap_degree,
                "importance": skill.importance.value
            }
            for skill in missing_skills
        ]
        
        role_assessment = {
            "role_name": target_role,
            "readiness_score": round(readiness_score, 3),
            "readiness_label": readiness_label,
            "missing_skills": missing_skills_dict,
            "quick_win_recommendations": quick_wins
        }
        
        result = {
            "target_role": target_role,
            "role_assessment": role_assessment
        }
        
        # Cache the result
        self.cache[cache_key] = result
        
        return result

    def assess_role_readiness(self, user_skills: List[UserSkill], force_refresh: bool = False) -> Dict:
        """
        Main method to assess user readiness for all roles.
        
        Args:
            user_skills: List of UserSkill objects with normalized skill names and levels
            force_refresh: If True, bypass cache
            
        Returns:
            JSON structure with matched roles and readiness metrics
        """
        # Check cache
        cache_key = self.generate_cache_key(user_skills)
        if not force_refresh and cache_key in self.cache:
            return self.cache[cache_key]
        
        matched_roles = []
        
        # Assess readiness for each role
        for role_name, requirements in self.role_catalog.items():
            readiness_score, missing_skills = self.compute_readiness_score(user_skills, requirements)
            readiness_label = self.get_readiness_label(readiness_score)
            quick_wins = self.generate_quick_win_recommendations(missing_skills)
            
            # Convert missing skills to dict format
            missing_skills_dict = [
                {
                    "skill": skill.skill,
                    "current_level": skill.current_level,
                    "target_level": skill.target_level,
                    "gap_degree": skill.gap_degree,
                    "importance": skill.importance.value
                }
                for skill in missing_skills
            ]
            
            role_match = {
                "role_name": role_name,
                "readiness_score": round(readiness_score, 3),
                "readiness_label": readiness_label,
                "missing_skills": missing_skills_dict,
                "quick_win_recommendations": quick_wins
            }
            
            matched_roles.append(role_match)
        
        # Sort by readiness score descending and take top 5
        matched_roles.sort(key=lambda x: x["readiness_score"], reverse=True)
        top_roles = matched_roles[:5]
        
        result = {
            "matched_roles": top_roles
        }
        
        # Cache the result
        self.cache[cache_key] = result
        
        return result
    
    def generate_role_summary(self, role_match: Dict) -> str:
        """
        Generate a concise UI summary for a role readiness assessment.
        
        Args:
            role_match: Single role object with readiness data
            
        Returns:
            Plain text summary under 50 words for UI display
        """
        role_name = role_match['role_name']
        score = role_match['readiness_score']
        label = role_match['readiness_label']
        missing_skills = role_match.get('missing_skills', [])
        quick_wins = role_match.get('quick_win_recommendations', [])
        
        # Format score as percentage
        score_pct = int(score * 100)
        
        # Build base summary
        summary = f"You're {score_pct}% fit for {role_name} ({label})"
        
        # Add missing skills context (limit to 2-3 key skills)
        if missing_skills:
            key_missing = [skill['skill'].replace('-', ' ').title() 
                          for skill in missing_skills[:2]]
            if key_missing:
                summary += f". Missing: {', '.join(key_missing)}"
        
        # Add quick win if available (quick_wins are strings, not objects)
        if quick_wins:
            first_win = quick_wins[0]
            # Extract just the action part, truncate if too long
            if ":" in first_win:
                action_part = first_win.split(":", 1)[1].strip()
            else:
                action_part = first_win
            
            if len(action_part) > 30:
                action_part = action_part[:27] + "..."
            summary += f". Quick win: {action_part}"
        
        return summary + "."
    
    def assess_from_raw_skills(self, raw_skills: List[str], force_refresh: bool = False) -> Dict:
        """
        Convenience method to assess readiness from raw skill list.
        
        Args:
            raw_skills: List of skill names as strings
            force_refresh: If True, bypass cache
            
        Returns:
            JSON structure with matched roles and readiness metrics
        """
        normalized_skills = self.normalize_user_skills(raw_skills)
        return self.assess_role_readiness(normalized_skills, force_refresh)

    def assess_single_role_from_raw_skills(self, raw_skills: List[str], target_role: str, force_refresh: bool = False) -> Dict:
        """
        Convenience method to assess readiness for a single role from raw skill list.
        
        Args:
            raw_skills: List of skill names as strings
            target_role: The specific role to assess (e.g., 'data-scientist')
            force_refresh: If True, bypass cache
            
        Returns:
            JSON structure with single role readiness assessment
        """
        normalized_skills = self.normalize_user_skills(raw_skills)
        return self.assess_single_role_readiness(normalized_skills, target_role, force_refresh)


# Convenience function for integration with existing pipeline
def assess_role_readiness(user_skills: List[str], force_refresh: bool = False) -> Dict:
    """
    Standalone function to assess role readiness from skill list.
    
    Args:
        user_skills: List of skill names
        force_refresh: If True, bypass cache
        
    Returns:
        JSON with role readiness assessment
    """
    agent = RoleReadinessAgent()
    return agent.assess_from_raw_skills(user_skills, force_refresh)


def assess_single_role_readiness(user_skills: List[str], target_role: str, force_refresh: bool = False) -> Dict:
    """
    Standalone function to assess readiness for a single role from skill list.
    
    Args:
        user_skills: List of skill names
        target_role: The specific role to assess (e.g., 'data-scientist')
        force_refresh: If True, bypass cache
        
    Returns:
        JSON with single role readiness assessment
    """
    agent = RoleReadinessAgent()
    return agent.assess_single_role_from_raw_skills(user_skills, target_role, force_refresh)


if __name__ == "__main__":
    # Test the agent
    test_skills = [
        "python", "sql", "machine-learning", "pandas", "numpy", 
        "scikit-learn", "jupyter", "git", "statistics"
    ]
    
    agent = RoleReadinessAgent()
    result = agent.assess_from_raw_skills(test_skills)
    
    print("🧪 Role Readiness Assessment Test")
    print("=" * 50)
    print(json.dumps(result, indent=2))
