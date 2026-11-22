# Meal Log Review Agent

An agentic AI system that analyzes patient meal logs, computes daily nutrient intake,
and produces a draft summary for clinician review — built with the Anthropic Claude API
and Python tool use.

> ⚠️ All output is labeled **DRAFT — FOR CLINICIAN REVIEW ONLY. NOT MEDICAL ADVICE.**

---

## What It Does

1. Reads a patient meal log (JSON) containing food items and quantities
2. For each food item with a known quantity, calls `lookup_nutrients` to retrieve
   calories, protein, carbs, and fat from a local reference table
3. If any food item is **missing a quantity**, the agent stops and asks for clarification
   instead of guessing
4. After all lookups, calls `calculate_daily_summary` to total up the day's nutrients
   and compare them against standard Daily Reference Intake (DRI) values
5. Produces a formatted clinical draft report

The language model decides which tool to call and when — it is not a fixed pipeline.

---

## Project Structure

```
meal-log-agent/
├── main.py                        # Agent entry point (Anthropic tool-use loop)
├── tools.py                       # lookup_nutrients and calculate_daily_summary
├── food_table.json                # Local nutrient reference table (20 foods, per 100 g)
├── requirements.txt
└── sample_data/
    ├── complete_meal.json         # Demo case 1: all quantities provided
    └── missing_qty_meal.json      # Demo case 2: two quantities missing (problem case)
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd meal-log-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Run the Demo

```bash
python main.py
```

This runs two cases back-to-back:

| Case | Input | Expected behavior |
|------|-------|-------------------|
| Case 1 | `complete_meal.json` — PT-001, all quantities provided | Full nutrient report with DRI comparison |
| Case 2 | `missing_qty_meal.json` — PT-002, 2 quantities missing | Agent stops and asks for the missing quantities |

---

## Tools

| Tool | Description |
|------|-------------|
| `lookup_nutrients(food_name, quantity_g)` | Looks up a food in `food_table.json` and returns scaled nutrient values |
| `calculate_daily_summary(nutrient_list)` | Sums all nutrient entries and compares totals against DRI |

---

## Sample Output (Case 1 — excerpt)

```
[Tool Call] lookup_nutrients({"food_name": "chicken breast", "quantity_g": 180})
[Tool Result] {"status": "ok", "calories": 297.0, "protein_g": 55.8, ...}
...
[Tool Call] calculate_daily_summary({...})

⚠️ DRAFT — FOR CLINICIAN REVIEW ONLY. NOT MEDICAL ADVICE.

Daily Totals: 1738.8 kcal | Protein 131.9 g (264% DRI) | Carbs 165.1 g | Fat 63.4 g
```

## Sample Output (Case 2 — problem case)

```
⚠️ Missing Quantities Detected — Action Required

Before proceeding, the following quantities are missing:
  - Breakfast → Orange  ❌
  - Lunch     → Tuna    ❌

Please provide quantities in grams to continue.
```

---

## Dependencies

- `anthropic >= 0.40.0`
- Python 3.10+

---

## Author

Wan Lin Yang — CSYE 7374 Agentic AI, Northeastern University, Fall 2026
