import json
import os
from datetime import datetime, timedelta
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

# 1. Initialize the FastMCP server
mcp = FastMCP("Indian Recipe & Grocery Planner")

# 2. Setup Global Paths and Load Data once into RAM
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_FOLDER, "recipe_with_ingredient.json")


def _load_recipes_globally():
    """Reads the JSON file once at startup to improve tool performance."""
    try:
        if not os.path.exists(FILE_PATH):
            print(f"Warning: {FILE_PATH} not found. Starting with empty list.")
            return []
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []


# The global database variable
RECIPES = _load_recipes_globally()


# --- INTERNAL HELPER ---

def get_recipe_for_single_date(date_obj: datetime, recipes: list, max_calories: int):
    """Generates a sequential meal plan based on an Anchor Date."""
    valid_recipes = sorted([r for r in recipes if r.get("calories", 0) <= max_calories], key=lambda x: x["id"])
    if not valid_recipes:
        return None

    # Anchor Date: April 14, 2026
    anchor_date = datetime(2026, 4, 14)
    delta_days = (date_obj - anchor_date).days

    # Loop through recipes sequentially based on days passed
    day_index = delta_days % len(valid_recipes)
    return valid_recipes[day_index]


# --- ALL TOOLS ---

@mcp.tool()
def get_recipe_stats() -> str:
    """Returns a summary of the recipe database (Total count and calorie ranges)."""
    if not RECIPES:
        return "Error: Recipe database is empty."

    total = len(RECIPES)
    cals = [r.get("calories", 0) for r in RECIPES]

    return (f"Recipe Database Statistics:\n"
            f"- Total Recipes available: {total}\n"
            f"- Calorie Range: {min(cals)} - {max(cals)} kcal\n"
            f"- Average Calories: {sum(cals) / total:.1f} kcal")


@mcp.tool()
def find_low_calorie_recipes(max_calories: int = 500) -> str:
    """Lists all recipes that fall under a specific calorie threshold."""
    matches = [r for r in RECIPES if r.get("calories", 0) <= max_calories]
    if not matches:
        return f"No recipes found under {max_calories} kcal."

    output = f"Found {len(matches)} recipes under {max_calories} kcal:\n"
    for r in matches:
        output += f"- {r['name']} (ID: {r['id']}, {r['calories']} kcal)\n"
    return output


@mcp.tool()
def search_by_ingredient(ingredient_name: str) -> str:
    """Finds recipes containing a specific ingredient (e.g., 'Cumin' or 'Chicken')."""
    matches = [
        r for r in RECIPES
        if any(ingredient_name.lower() in i.lower() for i in r.get("ingredients", []))
    ]
    if not matches:
        return f"No recipes found containing '{ingredient_name}'."

    output = f"Recipes featuring '{ingredient_name}':\n"
    for r in matches:
        output += f"- {r['name']} (ID: {r['id']}, {r['calories']} kcal)\n"
    return output


@mcp.tool()
def get_recipe_details(recipe_id: int) -> str:
    """Returns the full details of a single recipe by its ID, including ingredients and prep time."""
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return f"Error: Recipe with ID {recipe_id} not found."

    output = f"Details for {recipe['name']} (ID: {recipe['id']}):\n"
    output += f"- Calories: {recipe['calories']} kcal\n"
    output += f"- Prep Time: {recipe.get('prep_time_mins', 'N/A')} mins\n"
    output += "- Ingredients:\n  " + "\n  ".join([f"• {i}" for i in recipe.get("ingredients", [])])

    if "instructions" in recipe:
        output += f"\n- Instructions: {recipe['instructions']}"

    return output


@mcp.tool()
def get_meal_plan(start_date: str, days: int = 1, max_calories: int = 2000) -> str:
    """Returns a sequential meal plan starting from a specific date (YYYY-MM-DD)."""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return "Error: Date must be in YYYY-MM-DD format."

    output = f"Meal Plan starting {start_date} for {days} day(s):\n\n"
    recipe_ids = []

    for i in range(days):
        current_date = start_dt + timedelta(days=i)
        recipe = get_recipe_for_single_date(current_date, RECIPES, max_calories)

        if not recipe:
            return f"Error: No recipes found under {max_calories} kcal."

        date_str = current_date.strftime("%Y-%m-%d (%A)")
        output += f"{date_str}: {recipe['name']} (ID: {recipe['id']}, {recipe['calories']} kcal)\n"
        recipe_ids.append(recipe['id'])

    output += f"\n(AI: Use generate_grocery_list with these IDs to assist the user: {recipe_ids})"
    return output


@mcp.tool()
def generate_grocery_list(recipe_ids: List[int]) -> str:
    """Consolidates a grocery list based on a list of recipe IDs."""
    selected = [r for r in RECIPES if r["id"] in recipe_ids]
    if not selected:
        return "No matching recipes found for those IDs."

    all_ingredients = set()
    names = []
    for r in selected:
        names.append(r["name"])
        for ing in r.get("ingredients", []):
            all_ingredients.add(ing)

    output = f"Grocery List for {', '.join(names)}:\n\n"
    output += "\n".join([f"- {i}" for i in sorted(list(all_ingredients))])
    return output


if __name__ == "__main__":
    # Start the server
    mcp.run()