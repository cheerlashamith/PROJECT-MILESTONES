import re

# Domain keywords list for construction-related topics
CONSTRUCTION_KEYWORDS = {
    # General Construction & Civil Engineering
    "construct", "construction", "build", "builder", "building", "civil", "structure", "structural",
    "engineer", "engineering", "architect", "architecture", "design", "site", "infrastructure",
    "foundation", "slab", "beam", "column", "wall", "floor", "roof", "plinth", "flyover", "bridge",
    "project", "portfolio", "telemetry", "progress", "completion", "status", "lead", "manager",
    "contract", "contractor", "subcontractor", "operation", "work", "report", "daily", "dpr",
    
    # Materials
    "material", "concrete", "cement", "steel", "rebar", "aggregate", "sand", "gravel", "brick",
    "mortar", "asphalt", "bitumen", "timber", "wood", "glass", "iron", "reinforcement",
    
    # Financial & Budgets
    "budget", "cost", "spent", "expenditure", "overrun", "variance", "financial", "money",
    "inr", "rupees", "cr", "lakh", "crore", "allocation", "estimate", "estimation", "pricing",
    
    # Safety & PPE & Regulations
    "safety", "ppe", "helmet", "hat", "vest", "boot", "glove", "glasses", "goggles", "harness",
    "incident", "accident", "hazard", "risk", "mitigate", "mitigation", "comply", "compliance",
    "audit", "inspection", "inspector", "guideline", "standard", "code", "regulation", "violation",
    
    # Specific project names in the workspace
    "noida", "metro", "oakridge", "highrise", "flyover", "highway", "mall", "glass", "tower", "station",
    
    # Technical Parameters
    "slump", "compressive", "strength", "grade", "m20", "m25", "m30", "m40", "ratio", "thickness",
    "curing", "weather", "rain", "wind", "temperature", "log", "equipment", "machinery"
}

# General greetings and assistant capabilities queries that are permitted
GREETINGS_AND_META = {
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening",
    "who are you", "what are you", "how are you", "help", "what can you do", "features",
    "thank you", "thanks", "bye", "goodbye"
}

# Prompt injection patterns
PROMPT_INJECTION_RE = re.compile(
    r"("
    r"ignore\s+(?:all\s+|any\s+|the\s+|of\s+)*(?:above|previous|system|instruction|rule|limit|constraint|safety|security)s?|"
    r"bypass\s+(?:all\s+|any\s+|the\s+|of\s+)*(?:limit|constraint|rule|filter|safety|security)s?|"
    r"you\s+are\s+now\s+a\s+(?:different|new|unrestricted|jailbreak)|"
    r"act\s+as\s+a\s+(?:developer|unrestricted|jailbroken|prompt|evil|hacker)|"
    r"forget\s+(?:everything|previous|instructions|rules|who\s+you\s+are)|"
    r"do\s+not\s+follow\s+(?:instructions|rules|constraints|system)|"
    r"override\s+(?:safety|system|instruction|rules|security)|"
    r"system\s+prompt\s+reveal|reveal\s+system\s+prompt|"
    r"print\s+the\s+system\s+prompt|show\s+the\s+system\s+prompt|"
    r"new\s+rule:|unrestricted\s+mode|jailbreak"
    r")",
    re.IGNORECASE
)

# Blocked off-topic categories patterns
OFF_TOPIC_PATTERNS = [
    (re.compile(r"\b(recipe|bake|cook|broil|fry|boil|ingredient|kitchen|food|sauce|cake|cookie|pasta|pizza|soup)\b", re.IGNORECASE), "Cooking/Recipes"),
    (re.compile(r"\b(joke|riddle|funny|laugh|comedy|humor)\b", re.IGNORECASE), "Entertainment/Jokes"),
    (re.compile(r"\b(poem|poetry|song|lyrics|verse|rhyme|write\s+a\s+story|creative\s+writing)\b", re.IGNORECASE), "Creative Writing"),
    (re.compile(r"\b(hack|crack|exploit|malware|virus|phish|ddos|sql\s+injection|bypass\s+auth)\b", re.IGNORECASE), "Cybersecurity Attacks"),
    (re.compile(r"\b(write\s+(python|javascript|java|c\+\+|html|css|sql|rust|go)\s+code|python\s+script\s+to)\b", re.IGNORECASE), "Software Development Coding (Unrelated to Construction)")
]

# Personal Identifiable Information (PII) pattern checks
PII_PATTERNS = {
    "Email Address": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "Phone Number": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "Credit Card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "Social Security Number (SSN)": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "Aadhaar Number (Indian UID)": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")
}

# System prompt exposure detector (checking if response mentions sensitive inner system instructions)
LEAK_PATTERNS = [
    "You are the Construction Intelligence Hub AI Assistant",
    "real-time live telemetry data from active projects",
    "under the 'Real-time Project Context' heading"
]

def check_prompt_injection(text: str) -> tuple[bool, str]:
    """Checks if the text contains prompt injection attempts."""
    match = PROMPT_INJECTION_RE.search(text)
    if match:
        return True, f"Prompt injection attempt detected: '{match.group(0)}'"
    return False, ""

def check_pii(text: str) -> tuple[bool, str]:
    """Checks if the text contains sensitive personal identifying information (PII)."""
    for label, pattern in PII_PATTERNS.items():
        match = pattern.search(text)
        if match:
            # Mask the matching PII for logs/safety description
            masked = match.group(0)[:3] + "..." + match.group(0)[-2:] if len(match.group(0)) > 5 else "..."
            return True, f"Sensitive PII detected ({label}): '{masked}'"
    return False, ""

def check_domain_relevance(text: str) -> tuple[bool, str]:
    """
    Checks if the text is relevant to construction and civil engineering.
    Permits general conversational phrases and greetings.
    """
    cleaned = text.strip().lower()
    
    # 1. Check if the text matches basic greetings or help queries
    words = re.findall(r"\b\w+\b", cleaned)
    if not words:
        return True, "" # Empty input is handled by app validations
        
    phrase = " ".join(words)
    # Check if the query is a common greeting or capabilities question
    for greet in GREETINGS_AND_META:
        if re.search(r"\b" + re.escape(greet) + r"\b", phrase):
            return True, ""
            
    # 2. Check for explicit blocked off-topic categories
    for pattern, category in OFF_TOPIC_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            return False, f"Off-topic content flagged: Request is categorized under {category}."

    # 3. Check for construction keywords.
    # We tokenise the input and check if there's a match.
    has_keyword = False
    for word in words:
        if word in CONSTRUCTION_KEYWORDS:
            has_keyword = True
            break
            
    if not has_keyword:
        # Give a warning that it doesn't seem construction-related
        return False, "Out-of-domain query. Please ask questions related to construction, safety audits, budgets, engineering, or project telemetry."
        
    return True, ""

def validate_input(text: str) -> tuple[bool, str, str]:
    """
    Validates user input against all input guardrails.
    Returns:
        (is_safe, error_category, reason)
    """
    # 1. Check prompt injection
    is_injection, reason = check_prompt_injection(text)
    if is_injection:
        return False, "Prompt Injection", reason
        
    # 2. Check PII leaks
    is_pii, reason = check_pii(text)
    if is_pii:
        return False, "PII Leak Prevention", reason
        
    # 3. Check domain relevance
    is_relevant, reason = check_domain_relevance(text)
    if not is_relevant:
        return False, "Domain Relevance Filter", reason
        
    return True, "", ""

def validate_output(response_text: str) -> tuple[bool, str, str]:
    """
    Validates model output before presenting it to the user.
    Returns:
        (is_safe, error_category, reason)
    """
    # 1. Check for system prompt leaks
    for leak_phrase in LEAK_PATTERNS:
        if leak_phrase in response_text:
            return False, "System Prompt Leak", f"Model response contains internal system instructions: '{leak_phrase}'"
            
    # 2. Check basic toxicity
    toxicity_terms = ["abuse", "stupid", "idiot", "dumb AI", "useless assistant", "fuck", "shit"]
    for term in toxicity_terms:
        if re.search(r"\b" + re.escape(term) + r"\b", response_text, re.IGNORECASE):
            return False, "Output Toxicity", "Model generated content violating professionalism guidelines."
            
    return True, "", ""
