"""
Material Calculator – Construction Material Estimation
======================================================
Uses standard construction engineering formulas to estimate
material quantities based on project area, floors, and house type.
"""

from backend.config import Config


class MaterialCalculator:
    """Calculates construction material quantities using engineering formulas."""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def calculate_all(self, area: float, floors: int, house_type: str) -> dict:
        """
        Calculate all material quantities for a construction project.

        Args:
            area: Total construction area in sq ft.
            floors: Number of floors.
            house_type: Type of house (Villa, Apartment, etc.).

        Returns:
            dict: Material name → {quantity, unit, formula, icon}
        """
        multiplier = self.config.HOUSE_TYPE_MULTIPLIERS.get(house_type, 1.0)

        materials = {
            "Cement": {
                "quantity": round(area * 0.4 * floors * multiplier, 1),
                "unit": "Bags",
                "icon": "fa-box-open",
                "formula": f"{area} × 0.4 × {floors} × {multiplier}",
                "description": "50kg bags of OPC/PPC cement",
            },
            "Sand": {
                "quantity": round(area * 0.816 / 35.3147 * floors * multiplier, 1),
                "unit": "Tons",
                "icon": "fa-mountain",
                "formula": f"{area} × 0.816 cft/sqft ÷ 35.31 × {floors} × {multiplier}",
                "description": "River sand / M-sand for masonry & plastering",
            },
            "Bricks": {
                "quantity": round(area * 8 * floors * multiplier),
                "unit": "Pcs",
                "icon": "fa-cubes",
                "formula": f"{area} × 8 bricks/sqft × {floors} × {multiplier}",
                "description": "Standard size clay or fly-ash bricks",
            },
            "Steel": {
                "quantity": round(area * 4 / 2204.62 * floors * multiplier, 2),
                "unit": "Tons",
                "icon": "fa-layer-group",
                "formula": f"{area} × 4 kg/sqft ÷ 2204.62 × {floors} × {multiplier}",
                "description": "TMT steel bars for RCC work",
            },
            "Aggregate": {
                "quantity": round(area * 0.608 / 35.3147 * floors * multiplier, 1),
                "unit": "Tons",
                "icon": "fa-cube",
                "formula": f"{area} × 0.608 cft/sqft ÷ 35.31 × {floors} × {multiplier}",
                "description": "Coarse aggregate (20mm) for concrete",
            },
            "Tiles": {
                "quantity": round(area * 1.1 * multiplier, 0),
                "unit": "Sq Ft",
                "icon": "fa-th",
                "formula": f"{area} × 1.1 (10% wastage) × {multiplier}",
                "description": "Floor tiles including 10% wastage",
            },
            "Paint": {
                "quantity": round(area * 2.5 / 350 * floors * multiplier, 1),
                "unit": "Liters",
                "icon": "fa-fill-drip",
                "formula": f"{area} × 2.5 wall factor ÷ 350 coverage × {floors} × {multiplier}",
                "description": "Interior + exterior paint (2 coats)",
            },
        }

        return materials

    def get_material_summary(self, materials: dict) -> str:
        """Generate a text summary of materials for display/export."""
        lines = []
        for mat, data in materials.items():
            qty = data["quantity"]
            # Format large numbers with commas
            if qty >= 1000:
                qty_str = f"{qty:,.0f}"
            else:
                qty_str = f"{qty:,.1f}"
            lines.append(f"{mat}: {qty_str} {data['unit']}")
        return "\n".join(lines)
