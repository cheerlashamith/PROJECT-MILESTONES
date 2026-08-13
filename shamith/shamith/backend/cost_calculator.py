"""
Cost Calculator – Construction Cost Estimation
===============================================
Calculates construction costs based on material quantities,
per-unit pricing, labor rates, and house-type multipliers.
"""

from backend.config import Config
from backend.material_calculator import MaterialCalculator


class CostCalculator:
    """Calculates construction costs from material quantities and standard rates."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.material_calculator = MaterialCalculator(config)

    def calculate_costs(
        self, area: float, floors: int, house_type: str, materials: dict = None
    ) -> dict:
        """
        Calculate detailed construction costs.

        Args:
            area: Total construction area in sq ft.
            floors: Number of floors.
            house_type: Type of house.
            materials: Pre-computed materials dict (optional, will compute if not provided).

        Returns:
            dict: Cost category → {value, icon, breakdown}
        """
        if not materials:
            materials = self.material_calculator.calculate_all(area, floors, house_type)

        multiplier = self.config.HOUSE_TYPE_MULTIPLIERS.get(house_type, 1.0)
        prices = self.config.MATERIAL_PRICES

        # ── Material Cost ────────────────────────────────────────────
        material_cost = 0.0
        material_breakdown = {}
        for mat_name, mat_data in materials.items():
            if mat_name in prices:
                unit_price = prices[mat_name]["price"]
                cost = mat_data["quantity"] * unit_price
                material_cost += cost
                material_breakdown[mat_name] = {
                    "quantity": mat_data["quantity"],
                    "unit": mat_data["unit"],
                    "unit_price": unit_price,
                    "total": cost,
                }

        # ── Labor Cost (typically 25-35% of material cost) ──────────
        labor_cost = area * 18 * floors * multiplier

        # ── Finishing Cost ───────────────────────────────────────────
        finishing_cost = area * 12 * multiplier

        # ── Plumbing & Electrical ────────────────────────────────────
        plumbing_electrical = area * 8 * multiplier

        # ── Miscellaneous (permits, transport, contingency) ─────────
        miscellaneous = area * 5 * multiplier

        costs = {
            "Material Cost": {
                "value": round(material_cost),
                "icon": "fa-layer-group",
                "color": "#1E3A8A",
                "breakdown": material_breakdown,
            },
            "Labor Cost": {
                "value": round(labor_cost),
                "icon": "fa-users",
                "color": "#F97316",
            },
            "Finishing Cost": {
                "value": round(finishing_cost),
                "icon": "fa-brush",
                "color": "#10b981",
            },
            "Plumbing & Electrical": {
                "value": round(plumbing_electrical),
                "icon": "fa-plug",
                "color": "#8b5cf6",
            },
            "Miscellaneous": {
                "value": round(miscellaneous),
                "icon": "fa-ellipsis-h",
                "color": "#64748b",
            },
        }

        return costs

    def get_total_cost(self, costs: dict) -> float:
        """Calculate total cost from all categories."""
        return sum(c["value"] for c in costs.values())

    def get_cost_per_sqft(self, costs: dict, area: float) -> float:
        """Calculate cost per square foot."""
        total = self.get_total_cost(costs)
        return round(total / area, 2) if area > 0 else 0

    def get_cost_summary(self, costs: dict, area: float) -> str:
        """Generate a text summary of costs for display/export."""
        total = self.get_total_cost(costs)
        per_sqft = self.get_cost_per_sqft(costs, area)
        lines = []
        for cat, data in costs.items():
            lines.append(f"{cat}: ${data['value']:,}")
        lines.append(f"\nTotal: ${total:,}")
        lines.append(f"Cost per sq ft: ${per_sqft:,.2f}")
        return "\n".join(lines)
