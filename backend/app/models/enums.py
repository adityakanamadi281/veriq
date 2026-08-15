"""Shared enums for the assessment domain.

These values are part of the product contract and are referenced by both the
deterministic engine code and the Gemini prompt schemas.
"""

from __future__ import annotations

from enum import Enum


class Dimension(str, Enum):
    ENGINEERING_FUNDAMENTALS = "Engineering Fundamentals"
    PROBLEM_SOLVING = "Problem Solving"
    AI_FLUENCY = "AI Fluency"
    AGENTIC_ENGINEERING = "Agentic Engineering"
    PRACTICAL_REASONING = "Practical Reasoning"
    COMMUNICATION = "Communication"


# Ordered list for stable iteration / display ordering.
ALL_DIMENSIONS: list[Dimension] = list(Dimension)


class QuestionFormat(str, Enum):
    WRITTEN = "written"
    SCENARIO = "scenario"
    MULTIPLE_CHOICE = "multiple_choice"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    PRACTICAL_REASONING = "practical_reasoning"
    AGENT_INSTRUCTION = "agent_instruction"


class AssessmentStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReadinessClassification(str, Enum):
    READY = "Ready"
    DEVELOPING = "Developing"
    EMERGING = "Emerging"
    FOUNDATIONAL = "Foundational"


class Pathway(str, Enum):
    READY = "Ready"
    TARGETED = "Targeted Capability Development"
    STRUCTURED = "Structured Capability Development"
    FOUNDATION = "Foundation Development"
