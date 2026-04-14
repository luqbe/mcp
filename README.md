# Recipe & Grocery Planner MCP Server

A Model Context Protocol (MCP) server that provides tools for planning meals and generating grocery lists.

## Features

- **Meal Planning**: Generate a continuous, sequential meal plan starting from a specific date.
- **Grocery List Generation**: Create a consolidated list of ingredients based on selected recipe IDs.
- **Calorie Filtering**: Filter meal plans by maximum calorie constraints.

## Tools

### `get_meal_plan`
Returns a persistent, sequential meal plan starting from a specific date.
- `start_date` (string): MUST be in `YYYY-MM-DD` format (e.g., '2026-04-14').
- `days` (int, optional): Number of consecutive days to generate. Default is 1.
- `max_calories` (int, optional): Maximum calories per meal. Default is 2000.

### `generate_grocery_list`
Generates a consolidated grocery list based on a list of recipe IDs.
- `recipe_ids` (List[int]): A list of recipe IDs to include in the grocery list.

## Setup

1. Install dependencies:
   ```bash
   pip install mcp
   ```
2. Run the server:
   ```bash
   python mcp_recipe/server.py
   ```

## Data Source
The server uses a local JSON database `recipe_with_ingredient.json` containing recipe details, including ingredients, calories, and preparation time.
