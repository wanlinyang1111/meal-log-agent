import json
import anthropic
from tools import lookup_nutrients, calculate_daily_summary

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "lookup_nutrients",
        "description": (
            "Look up the nutrient content (calories, protein, carbs, fat) of a single "
            "food item for a given quantity in grams. Use this for each food item that "
            "has a known quantity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "The name of the food item, e.g. 'chicken breast'.",
                },
                "quantity_g": {
                    "type": "number",
                    "description": "The quantity of the food item in grams.",
                },
            },
            "required": ["food_name", "quantity_g"],
        },
    },
    {
        "name": "calculate_daily_summary",
        "description": (
            "Calculate the total daily nutrient intake and compare it against the "
            "Daily Reference Intake (DRI). Call this after all individual food lookups "
            "are complete."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nutrient_list": {
                    "type": "array",
                    "description": "List of nutrient result objects returned by lookup_nutrients.",
                    "items": {"type": "object"},
                }
            },
            "required": ["nutrient_list"],
        },
    },
]

SYSTEM_PROMPT = """You are a clinical nutrition assistant that analyzes patient meal logs.

Your task:
1. For each food item in the meal log, check whether a quantity (in grams) is provided.
2. If a quantity is MISSING (null or not provided), DO NOT guess or proceed with that item.
   Instead, stop and ask the user to provide the missing quantity. List ALL missing items at once.
3. If a food item is not found in the reference table, note it as unknown and continue with the rest.
4. For all items with valid quantities, call lookup_nutrients for each one.
5. After all lookups are done, call calculate_daily_summary with the full results.
6. Produce a final report clearly labeled:

   ⚠️  DRAFT — FOR CLINICIAN REVIEW ONLY. NOT MEDICAL ADVICE.

The report should include the daily nutrient totals, DRI comparison, and any flagged items."""


def run_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "lookup_nutrients":
        result = lookup_nutrients(**tool_input)
    elif tool_name == "calculate_daily_summary":
        result = calculate_daily_summary(**tool_input)
    else:
        result = {"status": "error", "message": f"Unknown tool: {tool_name}"}
    return json.dumps(result)


def analyze_meal_log(meal_record: dict) -> None:
    print("=" * 60)
    print(f"Analyzing meal log for patient: {meal_record.get('patient_id', 'Unknown')}")
    print(f"Date: {meal_record.get('date', 'Unknown')}")
    print("=" * 60)

    messages = [
        {
            "role": "user",
            "content": (
                "Please analyze the following meal log and produce a nutrient summary report.\n\n"
                f"Meal log:\n{json.dumps(meal_record, indent=2)}"
            ),
        }
    ]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Print any text content the model outputs
        for block in response.content:
            if hasattr(block, "text"):
                print("\n[Model]:", block.text)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            # Process all tool calls in this response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[Tool Call] {block.name}({json.dumps(block.input)})")
                    result_str = run_tool(block.name, block.input)
                    result_data = json.loads(result_str)
                    print(f"[Tool Result] {json.dumps(result_data, indent=2)}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str,
                        }
                    )

            # Append assistant response and tool results to message history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason
            break

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys

    # Case 1: Complete meal log
    print("\n" + "█" * 60)
    print("CASE 1: Complete meal log (all quantities provided)")
    print("█" * 60)
    with open("sample_data/complete_meal.json") as f:
        complete = json.load(f)
    analyze_meal_log(complete)

    # Case 2: Meal log with missing quantities
    print("\n" + "█" * 60)
    print("CASE 2: Meal log with MISSING quantities (problem case)")
    print("█" * 60)
    with open("sample_data/missing_qty_meal.json") as f:
        missing = json.load(f)
    analyze_meal_log(missing)
