"""
Recommendation Engine for EduPilot AI.
Provides next-study suggestions, priority topics, and resource recommendations.
"""
from ml.dataset_generator import SUBJECT_COLS

SUBJECT_LABELS = {
    "math": "Mathematics", "reading": "Reading", "writing": "Writing",
    "science": "Science", "history": "History",
}

# Learning resources database
RESOURCE_DATABASE = {
    "math": {
        "Algebra": [
            {"title": "Khan Academy — Algebra", "type": "video", "url": "https://www.khanacademy.org/math/algebra", "difficulty": "beginner"},
            {"title": "Algebra Practice Problems", "type": "practice", "url": "#", "difficulty": "intermediate"},
        ],
        "Geometry": [
            {"title": "GeoGebra Interactive", "type": "interactive", "url": "https://www.geogebra.org", "difficulty": "beginner"},
            {"title": "Geometry Proofs Guide", "type": "article", "url": "#", "difficulty": "advanced"},
        ],
        "Calculus": [
            {"title": "3Blue1Brown — Essence of Calculus", "type": "video", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr", "difficulty": "beginner"},
        ],
        "Statistics": [
            {"title": "StatQuest with Josh Starmer", "type": "video", "url": "https://www.youtube.com/c/joshstarmer", "difficulty": "beginner"},
        ],
    },
    "reading": {
        "Comprehension": [
            {"title": "Active Reading Strategies", "type": "article", "url": "#", "difficulty": "beginner"},
        ],
        "Vocabulary": [
            {"title": "Vocabulary.com", "type": "interactive", "url": "https://www.vocabulary.com", "difficulty": "beginner"},
        ],
    },
    "writing": {
        "Essay Structure": [
            {"title": "Purdue OWL Writing Guide", "type": "article", "url": "https://owl.purdue.edu", "difficulty": "beginner"},
        ],
        "Grammar": [
            {"title": "Grammarly Blog", "type": "article", "url": "https://www.grammarly.com/blog", "difficulty": "beginner"},
        ],
    },
    "science": {
        "Physics Basics": [
            {"title": "Physics Classroom", "type": "interactive", "url": "https://www.physicsclassroom.com", "difficulty": "beginner"},
        ],
        "Chemistry": [
            {"title": "Tyler DeWitt Chemistry", "type": "video", "url": "https://www.youtube.com/user/tdewitt451", "difficulty": "beginner"},
        ],
    },
    "history": {
        "World History": [
            {"title": "CrashCourse World History", "type": "video", "url": "https://www.youtube.com/playlist?list=PLBDA2E52FB1EF80C9", "difficulty": "beginner"},
        ],
    },
}

# Study technique suggestions based on learning style
STUDY_TECHNIQUES = {
    "visual": [
        "Create mind maps for each chapter",
        "Use color-coded flashcards",
        "Watch educational videos before reading textbook",
        "Draw diagrams and flowcharts",
    ],
    "auditory": [
        "Record yourself explaining concepts",
        "Listen to educational podcasts",
        "Study with a partner and discuss topics",
        "Use text-to-speech for notes review",
    ],
    "kinesthetic": [
        "Practice problems actively",
        "Use physical models for abstract concepts",
        "Take walking breaks between sessions",
        "Write notes by hand",
    ],
    "general": [
        "Use the Pomodoro technique (25 min focus + 5 min break)",
        "Teach concepts to someone else (Feynman technique)",
        "Create summary sheets after each study session",
        "Mix different subjects in one session (interleaving)",
        "Quiz yourself before reviewing material (active recall)",
    ],
}


def get_study_recommendations(weakness_data: dict, progress_data: dict = None) -> dict:
    """Generate comprehensive study recommendations."""

    recommendations = {
        "next_study": [],
        "priority_topics": [],
        "resources": [],
        "techniques": STUDY_TECHNIQUES["general"],
        "motivational_tip": _get_motivational_tip(progress_data),
    }

    # What to study next (based on weakness severity)
    for subj in weakness_data.get("subject_analysis", [])[:5]:
        if subj["needs_improvement"]:
            recommendations["next_study"].append({
                "subject": subj["label"],
                "subject_key": subj["subject"],
                "reason": f"Score gap: {abs(subj['gap_from_target']):.0f} points below target",
                "priority": subj["severity"],
            })

            # Add priority topics
            subject_key = subj["subject"]
            if subject_key in RESOURCE_DATABASE:
                for topic, resources in RESOURCE_DATABASE[subject_key].items():
                    recommendations["priority_topics"].append({
                        "subject": subj["label"],
                        "topic": topic,
                        "priority": subj["severity"],
                    })
                    recommendations["resources"].extend(resources[:2])

    # If student is doing well, suggest advanced topics
    for subj in weakness_data.get("strong_subjects", []):
        recommendations["next_study"].append({
            "subject": subj["label"],
            "subject_key": subj["subject"],
            "reason": "Maintain your strong performance",
            "priority": "maintenance",
        })

    return recommendations


def _get_motivational_tip(progress_data: dict = None) -> str:
    """Get a contextual motivational tip."""
    tips = [
        "💪 Consistency beats intensity. 30 minutes daily > 5 hours on weekends.",
        "🧠 Your brain consolidates learning during sleep. Don't sacrifice rest!",
        "🎯 Focus on understanding, not memorizing. Deep learning lasts longer.",
        "🔄 Mistakes are learning opportunities. Review wrong answers carefully.",
        "📈 Small improvements compound. 1% better every day = 37x better in a year!",
        "🌟 You've got this! Every expert was once a beginner.",
    ]

    if progress_data:
        streak = progress_data.get("study_streak", 0)
        if streak >= 7:
            return f"🔥 Amazing {streak}-day streak! You're building unstoppable momentum!"
        elif streak >= 3:
            return f"✨ {streak}-day streak! Keep going — habits form in 21 days!"
        elif streak == 0:
            return "🚀 Start fresh today! One study session is all it takes to begin your streak."

    import random
    return random.choice(tips)
