import pandas as pd
import os

def generate_my_food_csv():
    """
    This script generates a personalized CSV file of common foods,
    ready to be imported into the Diet Tracker application.
    
    You can easily add, remove, or modify the food items in the `my_foods` list
    to create your own custom diet plan.
    """

    # --- Customize Your Food List Here ---
    my_foods = [
        # 🌾 Grains & Carbs
        {"name": "Matta rice", "category": "Grains & Carbs", "unit": "100g cooked", "protein": 7, "carbs": 78, "fat": 0.8},
        {"name": "Whole wheat roti", "category": "Grains & Carbs", "unit": "1 roti (~50g)", "protein": 6, "carbs": 35, "fat": 0.6},
        {"name": "Oats (plain)", "category": "Grains & Carbs", "unit": "40g dry", "protein": 5.2, "carbs": 25, "fat": 2},
        
        # 🍲 Cooked Dishes
        {"name": "Soya biriyani", "category": "Cooked Dishes", "unit": "1 cup (~200g)", "protein": 18, "carbs": 45, "fat": 8},
        {"name": "Paneer biriyani", "category": "Cooked Dishes", "unit": "1 cup (~200g)", "protein": 20, "carbs": 42, "fat": 12},
        {"name": "Egg curry", "category": "Cooked Dishes", "unit": "1 serving (~150g)", "protein": 12, "carbs": 5, "fat": 10},
        {"name": "Potato curry", "category": "Cooked Dishes", "unit": "1 serving (~150g)", "protein": 3, "carbs": 28, "fat": 7},
        {"name": "Cabbage curry", "category": "Cooked Dishes", "unit": "1 serving (~150g)", "protein": 4, "carbs": 15, "fat": 4},
        {"name": "Green gram curry", "category": "Cooked Dishes", "unit": "1 cup (~200g)", "protein": 14, "carbs": 30, "fat": 2},
        
        # 🍞 Common Foods
        {"name": "Dosa", "category": "Common Foods", "unit": "1 dosa (~80g)", "protein": 3, "carbs": 22, "fat": 3},
        {"name": "Appam (Kerala)", "category": "Common Foods", "unit": "1 appam (~70g)", "protein": 2, "carbs": 20, "fat": 1},
        {"name": "Chutney (coconut)", "category": "Common Foods", "unit": "2 tbsp (~40g)", "protein": 1, "carbs": 3, "fat": 4},
        {"name": "Chapathi", "category": "Common Foods", "unit": "1 piece (~50g)", "protein": 6, "carbs": 35, "fat": 0.6},
        {"name": "Poori", "category": "Common Foods", "unit": "1 piece (~30g)", "protein": 2, "carbs": 15, "fat": 5},
        
        # 🍗 Proteins
        {"name": "Egg", "category": "Proteins", "unit": "1 piece", "protein": 6, "carbs": 0.3, "fat": 5},
        {"name": "Soya chunks", "category": "Proteins", "unit": "50g", "protein": 35, "carbs": 10, "fat": 1},
        {"name": "Toor/Moong dal", "category": "Proteins", "unit": "100g cooked", "protein": 9, "carbs": 20, "fat": 0.8},
        {"name": "Chicken (skinless)", "category": "Proteins", "unit": "100g cooked", "protein": 27, "carbs": 0, "fat": 2},
        {"name": "Peanuts", "category": "Proteins", "unit": "30g handful", "protein": 7, "carbs": 3, "fat": 20},
        {"name": "Curd (low-fat)", "category": "Dairy", "unit": "100g", "protein": 3, "carbs": 4, "fat": 1},
        
        # 🥦 Vegetables
        {"name": "Onion", "category": "Vegetables", "unit": "100g", "protein": 1, "carbs": 9, "fat": 0},
        {"name": "Tomato", "category": "Vegetables", "unit": "100g", "protein": 0.5, "carbs": 3.5, "fat": 0},
        {"name": "Cucumber", "category": "Vegetables", "unit": "100g", "protein": 0.4, "carbs": 1.6, "fat": 0},
        {"name": "Carrot", "category": "Vegetables", "unit": "100g", "protein": 0.8, "carbs": 6, "fat": 0},
        {"name": "Beans/Cabbage/Spinach", "category": "Vegetables", "unit": "100g", "protein": 2.5, "carbs": 6, "fat": 0},
        
        # 🍎 Fruits
        {"name": "Banana", "category": "Fruits", "unit": "1 medium (~100g)", "protein": 1, "carbs": 23, "fat": 0.3},
        {"name": "Papaya", "category": "Fruits", "unit": "1 cup (~150g)", "protein": 0.8, "carbs": 16, "fat": 0},
        {"name": "Orange/Mosambi", "category": "Fruits", "unit": "1 piece (~150g)", "protein": 0.9, "carbs": 12, "fat": 0.1},
        {"name": "Guava", "category": "Fruits", "unit": "1 medium (~100g)", "protein": 2.5, "carbs": 14, "fat": 0.2},
        {"name": "Apple", "category": "Fruits", "unit": "1 medium (~100g)", "protein": 0.3, "carbs": 14, "fat": 0.2},
        {"name": "Grapes", "category": "Fruits", "unit": "100g", "protein": 0.6, "carbs": 17, "fat": 0.2},
    ]
    # --- End of Customization ---

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(my_foods)

    # Define the output filename
    output_filename = "my_personal_food_list.csv"
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)

    # Save the DataFrame to a CSV file
    df.to_csv(output_path, index=False)

    print(f"✅ Successfully generated your food list at: {output_path}")

if __name__ == "__main__":
    generate_my_food_csv()