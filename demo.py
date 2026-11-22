"""
Standalone demo script for the Meal Log Review Agent.
Runs Case 1 (complete) and Case 2 (missing quantity) with clear section headers.
Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python demo.py
"""

import json
import sys
from main import analyze_meal_log

SEPARATOR = "=" * 60

def main():
    print("\n" + SEPARATOR)
    print("MEAL LOG REVIEW AGENT — DEMO")
    print(SEPARATOR)
    print("This demo runs two cases:")
    print("  Case 1 — All quantities provided  → Full nutrient report")
    print("  Case 2 — Two quantities missing   → Agent asks for clarification")
    print(SEPARATOR + "\n")

    # Case 1: complete meal
    print("▶ CASE 1: Complete Meal Log (PT-001)")
    print(SEPARATOR)
    with open("sample_data/complete_meal.json") as f:
        complete = json.load(f)
    analyze_meal_log(complete)

    # Case 2: missing quantities
    print("\n▶ CASE 2: Missing Quantities — Problem Case (PT-002)")
    print(SEPARATOR)
    with open("sample_data/missing_qty_meal.json") as f:
        missing = json.load(f)
    analyze_meal_log(missing)

    print("\n" + SEPARATOR)
    print("Demo complete.")
    print(SEPARATOR + "\n")


if __name__ == "__main__":
    main()
