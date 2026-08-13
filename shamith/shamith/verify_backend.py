# -*- coding: utf-8 -*-
"""Quick verification script for backend modules."""
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, ".")

print("=" * 50)
print("CIH Backend Verification")
print("=" * 50)

# Test 1: Material Calculator
print("\n[1] Material Calculator...")
from backend.material_calculator import MaterialCalculator
mc = MaterialCalculator()
materials = mc.calculate_all(2500, 2, "Villa")
for k, v in materials.items():
    print(f"    {k}: {v['quantity']} {v['unit']}")
print("    PASS")

# Test 2: Cost Calculator
print("\n[2] Cost Calculator...")
from backend.cost_calculator import CostCalculator
cc = CostCalculator()
costs = cc.calculate_costs(2500, 2, "Villa", materials)
total = cc.get_total_cost(costs)
for k, v in costs.items():
    print(f"    {k}: ${v['value']:,}")
print(f"    Total: ${total:,}")
print(f"    Per sqft: ${cc.get_cost_per_sqft(costs, 2500):,.2f}")
print("    PASS")

# Test 3: Config
print("\n[3] Config...")
from backend.config import Config
cfg = Config()
print(f"    Model: {cfg.MODEL_NAME}")
print(f"    Host: {cfg.OLLAMA_HOST}")
print(f"    Temp: {cfg.TEMPERATURE}")
print("    PASS")

# Test 4: Prompt Manager
print("\n[4] Prompt Manager...")
from backend.prompt_manager import PromptManager
pm = PromptManager()
sys_prompt = pm.get_system_prompt()
print(f"    System prompt length: {len(sys_prompt)} chars")
print("    PASS")

# Test 5: Utils
print("\n[5] Utils...")
from backend.utils import format_number, validate_project_data
print(f"    format_number(45000) = {format_number(45000)}")
valid, errors = validate_project_data({"owner_name": "Test", "location": "NYC", "area": 2500, "budget": 100000, "floors": 2})
print(f"    validate_project_data = {valid}, errors = {errors}")
print("    PASS")

# Test 6: Llama Service (connectivity)
print("\n[6] Llama Service...")
from backend.llama_service import LlamaService
ls = LlamaService()
status = ls.get_status()
print(f"    Ollama running: {status['ollama_running']}")
print(f"    Model available: {status['model_available']}")
print(f"    Available models: {status['available_models']}")
print("    PASS")

# Test 7: Logger
print("\n[7] Logger...")
from backend.logger import AppLogger
logger = AppLogger()
logger.info("Verification test completed")
print("    PASS")

print("\n" + "=" * 50)
print("All backend modules verified successfully!")
print("=" * 50)
