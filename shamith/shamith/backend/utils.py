"""
Shared Utilities
================
Helper functions used across the CIH backend.
"""


def format_number(n, decimals: int = 0) -> str:
    """
    Format a number with comma separators.

    Args:
        n: Number to format.
        decimals: Number of decimal places.

    Returns:
        Formatted string (e.g., '45,000' or '12.50').
    """
    if decimals > 0:
        return f"{n:,.{decimals}f}"
    return f"{n:,.0f}"


def validate_project_data(data: dict) -> tuple:
    """
    Validate project data fields.

    Args:
        data: Project data dictionary.

    Returns:
        (is_valid: bool, errors: list of strings)
    """
    errors = []

    if not data.get("owner_name", "").strip():
        errors.append("Owner name is required.")
    if not data.get("location", "").strip():
        errors.append("Location is required.")

    area = data.get("area", 0)
    if area <= 0:
        errors.append("Construction area must be greater than 0.")
    elif area > 100000:
        errors.append("Construction area seems unusually large. Please verify.")

    budget = data.get("budget", 0)
    if budget <= 0:
        errors.append("Budget must be greater than 0.")

    floors = data.get("floors", 0)
    if floors <= 0:
        errors.append("Number of floors must be at least 1.")

    return (len(errors) == 0, errors)


def get_project_context_string(project_data: dict, room_data: dict) -> str:
    """
    Build a context string from project and room data for AI prompts.

    Args:
        project_data: Project details dictionary.
        room_data: Room dimensions dictionary.

    Returns:
        Formatted context string.
    """
    lines = [
        f"Project Type: {project_data.get('house_type', 'N/A')}",
        f"Location: {project_data.get('location', 'N/A')}",
        f"Total Area: {project_data.get('area', 'N/A')} sq ft",
        f"Floors: {project_data.get('floors', 'N/A')}",
        f"Budget: ${project_data.get('budget', 0):,}",
        f"Start Date: {project_data.get('start_date', 'N/A')}",
        "",
        "Rooms:",
    ]

    for room, dims in room_data.items():
        area = dims["length"] * dims["width"]
        lines.append(f"  - {room}: {dims['length']}ft × {dims['width']}ft = {area} sq ft")

    return "\n".join(lines)
