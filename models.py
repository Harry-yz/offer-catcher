# models.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Education:
    school: str = ""
    major: str = ""
    degree: str = ""
    gpa: str = ""
    start_date: str = ""
    end_date: str = ""

@dataclass
class Project:
    name: str = ""
    description: str = ""
    key_achievements: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)

@dataclass
class Internship:
    company: str = ""
    position: str = ""
    duration: str = ""
    description: str = ""
    key_achievements: List[str] = field(default_factory=list)

@dataclass
class WorkExperience:
    company: str = ""
    position: str = ""
    duration: str = ""
    description: str = ""
    key_achievements: List[str] = field(default_factory=list)

@dataclass
class Certificate:
    name: str = ""
    issuer: str = ""
    date: str = ""

@dataclass
class Award:
    name: str = ""
    date: str = ""
    description: str = ""

@dataclass
class Resume:
    name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    education: Education = field(default_factory=Education)
    work_experience: List[WorkExperience] = field(default_factory=list)
    internships: List[Internship] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certificates: List[Certificate] = field(default_factory=list)
    awards: List[Award] = field(default_factory=list)
    self_evaluation: str = ""

@dataclass
class Requirement:
    skill: str = ""
    importance: str = "中"

@dataclass
class Requirements:
    must_have: List[Requirement] = field(default_factory=list)
    nice_to_have: List[Requirement] = field(default_factory=list)

@dataclass
class JobDescription:
    company: str = ""
    position: str = ""
    location: str = ""
    requirements: Requirements = field(default_factory=Requirements)
    responsibilities: List[str] = field(default_factory=list)

@dataclass
class MatchItem:
    requirement: str = ""
    evidence: str = ""
    strength: str = "中"
    score: int = 0

@dataclass
class MissingItem:
    requirement: str = ""
    severity: str = "中"
    suggestion: str = ""

@dataclass
class Optimization:
    original: str = ""
    suggested: str = ""
    reason: str = ""

@dataclass
class MatchResult:
    overall_score: int = 0
    matched: List[MatchItem] = field(default_factory=list)
    missing: List[MissingItem] = field(default_factory=list)
    analysis: str = ""
    optimization: List[Optimization] = field(default_factory=list)
    company: str = ""
    position: str = ""
    location: str = ""

@dataclass
class SelfIntro:
    formal: str = ""
    colloquial: str = ""
    key_points: List[str] = field(default_factory=list)

@dataclass
class InterviewQuestion:
    question: str = ""
    intent: str = ""
    answer: str = ""
    colloquial_answer: str = ""
    follow_ups: List[str] = field(default_factory=list)

@dataclass
class InterviewPrep:
    self_intro: SelfIntro = field(default_factory=SelfIntro)
    questions: List[InterviewQuestion] = field(default_factory=list)

@dataclass
class MockScores:
    technical_depth: int = 60
    quantitative_support: int = 60
    logical_clarity: int = 60

@dataclass
class MockReply:
    scores: MockScores = field(default_factory=MockScores)
    overall: int = 60
    feedback: str = ""
    next_question: str = ""
    tips: List[str] = field(default_factory=list)
