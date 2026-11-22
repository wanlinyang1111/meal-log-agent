import json
import os

FOOD_TABLE_PATH = os.path.join(os.path.dirname(__file__), "food_table.json")

with open(FOOD_TABLE_PATH) as f:
    FOOD_TABLE = json.load(f)

# Daily Reference Intake (simplified adult values)
DRI = {
    "calories": 2000,
    "protein": 50,
    "carbs": 275,
    "fat": 78,
}


def lookup_nutrients(food_name: str, quantity_g: float) -> dict:
    """
    Look up the nutrient content of a food item for a given quantity in grams.
    Returns calories, protein, carbs, and fat scaled to the given quantity.
    """
    food_name = food_name.lower().strip()
    if food_name not in FOOD_TABLE:
        return {
            "status": "error",
            "message": f"Food '{food_name}' not found in the reference table.",
        }

    per_100g = FOOD_TABLE[food_name]
    scale = quantity_g / 100.0
    return {
        "status": "ok",
        "food": food_name,
        "quantity_g": quantity_g,
        "calories": round(per_100g["calories"] * scale, 1),
        "protein_g": round(per_100g["protein"] * scale, 1),
        "carbs_g": round(per_100g["carbs"] * scale, 1),
        "fat_g": round(per_100g["fat"] * scale, 1),
    }


def calculate_daily_summary(nutrient_list: list[dict]) -> dict:
    """
    Sum up all successfully looked-up nutrient entries for the day.
    Compare totals against simplified Daily Reference Intake (DRI) values.
    """
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}

    for item in nutrient_list:
        if item.get("status") != "ok":
            continue
        totals["calories"] += item.get("calories", 0)
        totals["protein_g"] += item.get("protein_g", 0)
        totals["carbs_g"] += item.get("carbs_g", 0)
        totals["fat_g"] += item.get("fat_g", 0)

    for key in totals:
        totals[key] = round(totals[key], 1)

    dri_key_map = {
        "calories": "calories",
        "protein_g": "protein",
        "carbs_g": "carbs",
        "fat_g": "fat",
    }

    comparison = {}
    for total_key, dri_key in dri_key_map.items():
        actual = totals[total_key]
        recommended = DRI[dri_key]
        pct = round((actual / recommended) * 100, 1)
        comparison[total_key] = {
            "actual": actual,
            "recommended": recommended,
            "percent_of_dri": pct,
        }

    return {
        "status": "ok",
        "daily_totals": totals,
        "dri_comparison": comparison,
    }
