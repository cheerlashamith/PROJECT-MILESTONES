"""
AI Guardrails Module
====================
Enforces domain restrictions and safety rules on both User Inputs and AI Outputs.
"""

# ── Allowed Topics (Layer 2 – Input Classification) ────────────────────────
# Comprehensive construction & civil engineering vocabulary.
# We are INCLUSIVE – if ANY of these appear, the query is allowed.
CONSTRUCTION_KEYWORDS = [
    # Materials
    "cement", "concrete", "brick", "bricks", "block", "blocks", "sand", "aggregate",
    "steel", "rebar", "rcc", "tmt", "iron", "gravel", "mortar", "plaster", "putty",
    "tile", "tiles", "marble", "granite", "wood", "timber", "lumber", "plywood",
    "glass", "paint", "emulsion", "primer", "waterproofing", "bitumen", "tar",
    "pvc", "pipe", "pipes", "wire", "cable", "fitting", "fittings",
    # Structural / engineering
    "foundation", "footing", "footings", "column", "columns", "beam", "beams",
    "slab", "slabs", "wall", "walls", "roof", "roofing", "ceiling", "ceilings",
    "staircase", "stairs", "stair", "ramp", "ramps", "lintel", "lintels",
    "shear wall", "retaining wall", "pile", "piles", "raft", "raft foundation",
    "load bearing", "load-bearing", "span", "spans", "structural", "structure",
    "framing", "frame", "truss", "trusses", "arch", "cantilever",
    "M20", "M25", "M30", "m20", "m25", "m30", "grade", "mix", "ratio", "w/c",
    "reinforcement", "reinforced", "shuttering", "formwork", "curing",
    "compressive", "tensile", "flexural", "shear", "torsion", "deflection",
    # House / room planning
    "house", "home", "villa", "apartment", "flat", "bungalow", "duplex",
    "bedroom", "bedrooms", "bathroom", "bathrooms", "kitchen", "living room",
    "dining", "hall", "lobby", "garage", "balcony", "terrace", "corridor",
    "room", "rooms", "floor plan", "layout", "elevation", "section", "drawing",
    "blueprint", "floor", "floors", "storey", "stories", "ground floor",
    "first floor", "second floor", "basement", "penthouse",
    # Construction process
    "construction", "build", "building", "built", "site", "excavation",
    "digging", "survey", "surveying", "estimate", "estimation", "estimating",
    "quantity", "quantities", "takeoff", "bill of materials", "bom",
    "schedule", "timeline", "milestone", "phase", "phases", "work order",
    "progress", "inspection", "quality", "qa", "qc", "testing", "compliance",
    "permit", "permits", "approval", "approvals", "drawings", "specifications",
    # Costs / finance in construction context
    "cost", "costs", "budget", "budgeting", "pricing", "price", "rates",
    "quotation", "quote", "bid", "tender", "contract", "contractor",
    "subcontractor", "labour", "labor", "manpower", "workers", "workforce",
    "project cost", "material cost", "construction cost", "overrun",
    "sq ft", "sqft", "square feet", "square foot", "square meter", "sqm",
    "cubic", "meter", "feet", "inch", "inches", "dimension", "dimensions",
    "area", "volume", "weight", "tons", "tonne", "kg", "kilogram",
    # MEP (Mechanical, Electrical, Plumbing)
    "plumbing", "drainage", "sewage", "water", "electrical", "wiring",
    "hvac", "ventilation", "air conditioning", "ac unit", "duct", "ducts",
    "sanitary", "septic", "tank", "pump", "pumping", "valve", "valves",
    # Safety & management
    "safety", "hazard", "hazards", "risk", "risks", "ppe", "helmet",
    "harness", "scaffold", "scaffolding", "osha", "regulation", "regulations",
    "code", "codes", "standard", "standards", "iso", "bis", "astm",
    "engineer", "engineering", "architect", "architecture", "civil",
    "structural engineer", "site engineer", "project manager",
    # Document / reporting
    "report", "reports", "daily report", "inspection report", "audit",
    "document", "documents", "specification", "specifications", "spec",
    "contract", "insurance", "claim", "warranty", "handover",
    # General construction synonyms
    "renovation", "remodeling", "retrofit", "repair", "maintenance",
    "demolition", "waterproof", "damp", "crack", "leakage", "seepage",
    "vastu", "feng shui", "layout optimization", "green building",
    "leed", "sustainability", "energy efficient", "solar", "rainwater",
    # AI/Analysis related to construction
    "analyze", "analysis", "calculate", "calculation", "estimation",
    "material", "materials", "how many", "how much", "what is",
    "recommend", "suggestion", "advise", "advice",
]

# ── Strictly Prohibited Topics (only TRUE off-topic subjects) ───────────────
RESTRICTED_KEYWORDS = [
    "cricket", "ipl", "virat kohli", "dhoni", "sachin", "football",
    "movie", "film", "actor", "actress", "celebrity", "bollywood", "netflix",
    "politics", "election", "vote", "minister", "government policy",
    "stock market", "trading", "crypto", "bitcoin", "forex",
    "medical", "disease", "medicine", "doctor", "hospital", "surgery",
    "hack", "hacking", "illegal", "bomb", "weapon", "terrorism",
]

# ── Words that ARE in the restricted list but are also valid construction terms ─
CONSTRUCTION_OVERRIDE = [
    # "finance" can appear in construction cost context – allow if combined
    # These are not in RESTRICTED but good to note for the override logic
]


def check_input_guardrails(query: str) -> bool:
    """
    Validates if the user query passes the input guardrails.

    Strategy:
    1. Reject explicit restricted topics.
    2. Allow if any construction keyword is found.
    3. Fallback: allow short/generic queries that don't match restricted
       (users may ask follow-up questions without repeating keywords).

    Returns True if query should be processed, False if it should be refused.
    """
    query_lower = query.lower()

    # Step 1: Reject explicit restricted topics
    if any(word in query_lower for word in RESTRICTED_KEYWORDS):
        return False

    # Step 2: Allow if any construction keyword found
    if any(word in query_lower for word in CONSTRUCTION_KEYWORDS):
        return True

    # Step 3: Fallback – allow short follow-up questions (< 15 words)
    # that don't contain any restricted words. Construction assistants
    # receive many short follow-ups like "Why?" / "What about the roof?"
    word_count = len(query_lower.split())
    if word_count <= 15:
        return True

    # Long query with no construction keywords and no restricted keywords:
    # still allow – the system prompt will redirect if truly off-topic.
    return True


def apply_output_guardrails(response: str) -> str:
    """
    Validates and modifies the AI's response before sending it to the user.
    Only blocks truly off-topic responses. Does NOT block construction responses
    that incidentally mention restricted words.
    """
    response_lower = response.lower()

    # Only block if the AI response is CLEARLY off-topic (no construction
    # keywords at all, but contains restricted topic keywords).
    has_construction = any(word in response_lower for word in CONSTRUCTION_KEYWORDS)
    has_restricted = any(word in response_lower for word in RESTRICTED_KEYWORDS)

    if has_restricted and not has_construction:
        return (
            "⚠️ **GUARDRAIL ALERT:** The generated response drifted outside the "
            "construction domain. As the Agentic AI for Safety Monitoring with Construction Risk Analytics AI, I am "
            "restricted to construction-related topics only. Please ask a "
            "construction-related question."
        )

    # Structural Engineering Safety Disclaimer
    structural_terms = [
        "load-bearing", "foundation design", "beam design",
        "column design", "column size", "structural integrity",
        "shear wall design", "pile design",
    ]
    if any(term in response_lower for term in structural_terms):
        disclaimer = (
            "\n\n---\n⚠️ **SAFETY NOTE:** The structural guidance above is for "
            "estimation and educational purposes only. **Always consult a licensed "
            "structural engineer or architect** before proceeding with load-bearing "
            "construction or foundation work."
        )
        if disclaimer not in response:
            response += disclaimer

    return response
