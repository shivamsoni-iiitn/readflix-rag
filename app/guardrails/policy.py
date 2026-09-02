MAX_INPUT_LENGTH = 200

BLOCK_MESSAGES = {
    "invalid": "Please enter a valid question.",
    "extraction": "I can't provide internal instructions or hidden information.",
    "jailbreak": "I can't help with attempts to bypass my instructions.",
    "sensitive": "I can only assist with safe READFLIX Library-related questions.",
    "pii": "Please don't share personal information.",
    "secrets": "Please don't share passwords, API keys, or other credentials.",
    "off_topic": "I can only help with READFLIX Library-related questions.",
    "output": "I can't provide that information.",
    "grounding": "I can't verify that information right now. Please contact the READFLIX manager, Mr. Jeewan, for more information.",
}

GREETING_RESPONSES = [
    "Hello! How can I help you with READFLIX Library?",
    "Hi! What would you like to know about READFLIX?",
    "Hello! Ask me anything about READFLIX Library.",
]

FAREWELL_RESPONSES = [
    "Goodbye! Feel free to return for READFLIX information.",
    "See you later!",
]

CAPABILITY_RESPONSE = (
    "I can help with READFLIX Library timings, seating, membership, "
    "facilities, parking, rules, study environment, and other library information."
)

READFLIX_TOPICS = [
    "READFLIX Library",
    "library timings and opening hours",
    "membership and fees",
    "seating and study areas",
    "study environment",
    "facilities and services",
    "parking and location",
    "library rules and policies",
    "books and reading",
    "Wi-Fi",
    "drinking water",
    "washrooms",
    "access and eligibility",
]