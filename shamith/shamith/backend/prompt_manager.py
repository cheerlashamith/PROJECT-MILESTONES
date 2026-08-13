"""
Prompt Manager – System Prompts & Templates
============================================
All AI prompt templates in one place. Each method returns a
fully-formatted prompt string ready to send to Llama.
"""

from backend.config import Config


class PromptManager:
    """Manages and generates prompts for all AI interactions."""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    # ── System Prompt ────────────────────────────────────────────────

    def get_system_prompt(self) -> str:
        """Return the master system prompt for the construction AI."""
        return self.config.SYSTEM_PROMPT

    # ── Chat Prompt (with project context) ───────────────────────────

    def get_chat_prompt(self, user_message: str, project_context: str = "") -> str:
        """
        Enrich a user chat message with project context.

        Args:
            user_message: The raw user message.
            project_context: Formatted string of project data.

        Returns:
            Enriched prompt with context.
        """
        if project_context:
            return (
                f"[PROJECT CONTEXT]\n{project_context}\n\n"
                f"[USER QUESTION]\n{user_message}"
            )
        return user_message

    # ── Material Analysis Prompt ─────────────────────────────────────

    def get_material_analysis_prompt(
        self,
        area: float,
        floors: int,
        house_type: str,
        room_data: dict,
        materials: dict,
    ) -> str:
        """Generate a prompt for detailed AI material analysis."""
        rooms_str = ""
        for room, dims in room_data.items():
            rooms_str += f"  - {room}: {dims['length']}ft × {dims['width']}ft = {dims['length'] * dims['width']} sq ft\n"

        materials_str = ""
        for mat, data in materials.items():
            materials_str += f"  - {mat}: {data['quantity']:.1f} {data['unit']}\n"

        return (
            f"I am building a {house_type} with {floors} floor(s) and a total construction area "
            f"of {area:.0f} sq ft.\n\n"
            f"Room Layout:\n{rooms_str}\n"
            f"My calculated material estimates are:\n{materials_str}\n"
            f"Please provide:\n"
            f"1. A detailed analysis of whether these material estimates are reasonable.\n"
            f"2. Any materials I might be missing.\n"
            f"3. Tips to reduce wastage.\n"
            f"4. Quality recommendations for each material.\n"
            f"5. Any safety considerations.\n\n"
            f"Use industry-standard formulas and explain your reasoning."
        )

    # ── Cost Analysis Prompt ─────────────────────────────────────────

    def get_cost_analysis_prompt(
        self,
        costs: dict,
        area: float,
        budget: float,
        house_type: str,
    ) -> str:
        """Generate a prompt for AI cost optimization suggestions."""
        costs_str = ""
        total = 0
        for category, data in costs.items():
            costs_str += f"  - {category}: ${data['value']:,.0f}\n"
            total += data['value']

        budget_diff = budget - total
        status = "under budget" if budget_diff >= 0 else "over budget"

        return (
            f"I am building a {house_type} with a total area of {area:.0f} sq ft.\n\n"
            f"My budget is ${budget:,.0f}.\n\n"
            f"Current cost breakdown:\n{costs_str}"
            f"Total estimated cost: ${total:,.0f}\n"
            f"I am ${abs(budget_diff):,.0f} {status}.\n\n"
            f"Please provide:\n"
            f"1. Analysis of whether these costs are reasonable for my project.\n"
            f"2. Areas where I can save money without compromising quality.\n"
            f"3. Cost optimization strategies.\n"
            f"4. What I should NOT cut corners on (safety-critical items).\n"
            f"5. A recommended budget allocation percentage for each category.\n"
            f"6. Suggestions for phased construction if I'm over budget."
        )

    # ── Project Insights Prompt ──────────────────────────────────────

    def get_project_insights_prompt(self, project_data: dict, room_data: dict) -> str:
        """Generate a prompt for AI project insights after saving project details."""
        rooms_str = ""
        for room, dims in room_data.items():
            rooms_str += f"  - {room}: {dims['length']}ft × {dims['width']}ft\n"

        return (
            f"I am planning a construction project with the following details:\n\n"
            f"- Owner: {project_data.get('owner_name', 'N/A')}\n"
            f"- Location: {project_data.get('location', 'N/A')}\n"
            f"- House Type: {project_data.get('house_type', 'N/A')}\n"
            f"- Floors: {project_data.get('floors', 'N/A')}\n"
            f"- Total Area: {project_data.get('area', 'N/A')} sq ft\n"
            f"- Budget: ${project_data.get('budget', 0):,}\n"
            f"- Start Date: {project_data.get('start_date', 'N/A')}\n\n"
            f"Planned Rooms:\n{rooms_str}\n"
            f"Please provide:\n"
            f"1. Overall assessment of this project plan.\n"
            f"2. Is the budget realistic for this type of construction?\n"
            f"3. Timeline recommendations.\n"
            f"4. Key things to prepare before construction starts.\n"
            f"5. Potential challenges and how to mitigate them.\n"
            f"6. Recommendations for permits and approvals needed."
        )

    # ── Room Optimization Prompt ─────────────────────────────────────

    def get_room_optimization_prompt(
        self, room_data: dict, house_type: str, total_area: float
    ) -> str:
        """Generate a prompt for AI room layout optimization."""
        rooms_str = ""
        total_room_area = 0
        for room, dims in room_data.items():
            room_area = dims["length"] * dims["width"]
            total_room_area += room_area
            rooms_str += f"  - {room}: {dims['length']}ft × {dims['width']}ft = {room_area} sq ft\n"

        return (
            f"I am designing a {house_type} with a total construction area of {total_area:.0f} sq ft.\n\n"
            f"Current room layout:\n{rooms_str}\n"
            f"Total room area: {total_room_area:.0f} sq ft\n"
            f"Remaining area (hallways, walls, etc.): {total_area - total_room_area:.0f} sq ft\n\n"
            f"Please provide:\n"
            f"1. Are the room proportions well-balanced?\n"
            f"2. Suggested improvements to room dimensions.\n"
            f"3. Any rooms I should consider adding (utility room, storage, etc.).\n"
            f"4. Optimal room placement for natural light and ventilation.\n"
            f"5. Tips for maximizing usable space.\n"
            f"6. Vastu/Feng Shui considerations (if applicable)."
        )

    # ── Report Summary Prompt ────────────────────────────────────────

    def get_report_summary_prompt(
        self, project_data: dict, room_data: dict, materials: dict, costs: dict
    ) -> str:
        """Generate a prompt for a comprehensive AI project summary."""
        rooms_str = ""
        for room, dims in room_data.items():
            rooms_str += f"  - {room}: {dims['length']}ft × {dims['width']}ft\n"

        materials_str = ""
        for mat, data in materials.items():
            materials_str += f"  - {mat}: {data['quantity']:.1f} {data['unit']}\n"

        costs_str = ""
        total_cost = 0
        for cat, data in costs.items():
            costs_str += f"  - {cat}: ${data['value']:,.0f}\n"
            total_cost += data['value']

        return (
            f"Generate a professional project summary report for:\n\n"
            f"PROJECT DETAILS:\n"
            f"- Owner: {project_data.get('owner_name', 'N/A')}\n"
            f"- Location: {project_data.get('location', 'N/A')}\n"
            f"- Type: {project_data.get('house_type', 'N/A')}\n"
            f"- Floors: {project_data.get('floors', 'N/A')}\n"
            f"- Area: {project_data.get('area', 'N/A')} sq ft\n"
            f"- Budget: ${project_data.get('budget', 0):,}\n\n"
            f"ROOMS:\n{rooms_str}\n"
            f"MATERIALS:\n{materials_str}\n"
            f"COSTS:\n{costs_str}"
            f"Total Cost: ${total_cost:,.0f}\n\n"
            f"Provide a structured executive summary covering:\n"
            f"1. Project overview and feasibility\n"
            f"2. Key strengths of the plan\n"
            f"3. Areas of concern or risk\n"
            f"4. Budget assessment\n"
            f"5. Recommended next steps\n"
            f"6. Timeline estimation"
        )

    # ── AI Layout Generation Prompt ──────────────────────────────────
    
    def get_layout_generation_prompt(self, area: float, house_type: str, floors: int) -> str:
        """Generate a prompt that requests a JSON layout of rooms for a specific house."""
        return (
            f"Act as an expert architect. I am building a {house_type} with {floors} floors and a total area of {area} sq ft. "
            f"Design an optimal room layout. You must ONLY output a valid JSON dictionary containing the rooms and their length and width in feet. "
            f"Do not output any markdown formatting, no backticks, no explanations. Just raw JSON.\n\n"
            f"Format:\n"
            f"{{\n"
            f"  \"Living Room\": {{\"length\": 20.0, \"width\": 15.0}},\n"
            f"  \"Kitchen\": {{\"length\": 12.0, \"width\": 10.0}}\n"
            f"}}\n\n"
            f"Ensure the total area of the rooms is roughly 80% of the total house area ({area * 0.8} sq ft) to account for walls and hallways. "
            f"Include standard rooms appropriate for a {house_type}."
        )

    # ── Analytics Prompt ─────────────────────────────────────────────

    def get_analytics_prompt(
        self, project_data: dict, room_data: dict, materials: dict, costs: dict
    ) -> str:
        """Generate a prompt for AI-driven analytics insights."""
        total_cost = sum(c["value"] for c in costs.values())
        budget = project_data.get("budget", 0)

        rooms_str = ""
        for room, dims in room_data.items():
            rooms_str += f"  - {room}: {dims['length']}ft × {dims['width']}ft\n"

        costs_str = ""
        for cat, data in costs.items():
            costs_str += f"  - {cat}: ${data['value']:,.0f}\n"

        return (
            f"Analyze this construction project and provide predictive insights:\n\n"
            f"Project: {project_data.get('house_type', 'N/A')} | "
            f"Area: {project_data.get('area', 0)} sq ft | "
            f"Floors: {project_data.get('floors', 1)}\n"
            f"Budget: ${budget:,.0f} | Estimated Cost: ${total_cost:,.0f}\n\n"
            f"Rooms:\n{rooms_str}\n"
            f"Costs:\n{costs_str}\n"
            f"Provide:\n"
            f"1. Construction timeline prediction (weeks/months)\n"
            f"2. Potential delay factors and their likelihood\n"
            f"3. Cost overrun risk areas\n"
            f"4. Material price volatility warnings\n"
            f"5. Seasonal construction recommendations\n"
            f"6. Labor availability predictions\n"
            f"7. Energy efficiency score prediction\n"
        )

    # ── Risk Analysis Prompt ─────────────────────────────────────────

    def get_risk_analysis_prompt(self, project_data: dict, costs: dict) -> str:
        """Generate a prompt for risk analysis."""
        total_cost = sum(c["value"] for c in costs.values())
        budget = project_data.get("budget", 0)
        budget_status = "under" if budget >= total_cost else "over"

        return (
            f"Perform a comprehensive risk analysis for this construction project:\n\n"
            f"Project Type: {project_data.get('house_type', 'N/A')}\n"
            f"Location: {project_data.get('location', 'N/A')}\n"
            f"Area: {project_data.get('area', 0)} sq ft\n"
            f"Floors: {project_data.get('floors', 1)}\n"
            f"Budget: ${budget:,.0f}\n"
            f"Estimated Cost: ${total_cost:,.0f} ({budget_status} budget by ${abs(budget - total_cost):,.0f})\n\n"
            f"Analyze and rate (High/Medium/Low) these risk categories:\n"
            f"1. Budget Risk - likelihood of cost overruns\n"
            f"2. Schedule Risk - likelihood of delays\n"
            f"3. Quality Risk - areas where quality might suffer\n"
            f"4. Safety Risk - construction safety concerns\n"
            f"5. Regulatory Risk - permit and compliance issues\n"
            f"6. Environmental Risk - weather and site conditions\n"
            f"7. Supply Chain Risk - material availability\n\n"
            f"For each risk, provide: rating, description, and mitigation strategy."
        )

    # ── Site Safety Prompt ───────────────────────────────────────────

    def get_site_safety_prompt(self, project_data: dict, scenario: str) -> str:
        """Generate a prompt for site safety and OSHA compliance."""
        return (
            f"As a Construction Safety AI Officer, review the following scenario for a construction project:\n\n"
            f"Project: {project_data.get('house_type', 'N/A')} ({project_data.get('area', 0)} sq ft)\n"
            f"Scenario: {scenario}\n\n"
            f"Please provide:\n"
            f"1. Potential safety hazards in this scenario.\n"
            f"2. Required Personal Protective Equipment (PPE).\n"
            f"3. OSHA or general construction safety guidelines that apply.\n"
            f"4. A step-by-step mitigation plan to ensure worker safety.\n"
            f"5. Emergency response recommendations."
        )

    # ── Daily Report Prompt ──────────────────────────────────────────

    def get_daily_report_prompt(self, report_date: str, weather: str, manpower: str, tasks_completed: str, issues: str) -> str:
        """Generate a prompt for AI-generated daily construction reports."""
        return (
            f"You are a Construction Project Manager. Draft a professional Daily Construction Report based on the following notes:\n\n"
            f"Date: {report_date}\n"
            f"Weather: {weather}\n"
            f"Manpower on site: {manpower}\n"
            f"Tasks Completed: {tasks_completed}\n"
            f"Issues/Delays: {issues}\n\n"
            f"Please provide a structured report with:\n"
            f"1. Executive Summary of the day's progress.\n"
            f"2. Detailed Activity Log (expand on the tasks professionally).\n"
            f"3. Workforce & Weather Impact analysis.\n"
            f"4. Issues & Action Items for tomorrow."
        )

    # ── Project Q&A Prompt ───────────────────────────────────────────

    def get_project_qa_prompt(self, project_data: dict, question: str) -> str:
        """Generate a prompt for answering questions about the specific project."""
        return (
            f"You are the AI assistant for the following construction project:\n\n"
            f"- Type: {project_data.get('house_type', 'N/A')}\n"
            f"- Location: {project_data.get('location', 'N/A')}\n"
            f"- Area: {project_data.get('area', 0)} sq ft\n"
            f"- Floors: {project_data.get('floors', 1)}\n"
            f"- Budget: ${project_data.get('budget', 0):,}\n"
            f"- Start Date: {project_data.get('start_date', 'N/A')}\n\n"
            f"User Question: {question}\n\n"
            f"Provide a clear, accurate, and helpful answer based on the project details. If the project details do not contain the answer, use your general construction knowledge."
        )
