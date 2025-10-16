import pandas as pd
from sqlalchemy import and_, func
from datetime import datetime, date
from sqlalchemy.orm import selectinload
import os
from database import get_session, User, Food, Meal, MealItem, SleepLog

class MuscleTrackerBackend:
    def __init__(self):
        pass  # Session will be created per-method
    
    # User Authentication
    def create_user(self, username, password):
        """Create a new user with hashed password"""
        session = get_session()
        try:
            if session.query(User).filter(User.username == username).first():
                return False, "Username already exists"
            
            user = User(username=username)
            user.set_password(password)
            session.add(user)
            session.flush() # Flush to get user.id for the next step
            
            # Add default foods for new user
            self._add_default_foods(user.id, session)
            
            session.commit() # Commit the entire transaction
            return True, "User created successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error creating user: {str(e)}"
        finally:
            session.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        session = get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user and user.check_password(password):
                return True, user
            return False, "Invalid username or password"
        finally:
            session.close()
    
    def _add_default_foods(self, user_id, session):
        """Add default food items for new users"""
        default_foods = [
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
            
            # 🍞 Breakfast Foods (but can be used in any meal)
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
            
            # ☕ Beverages
            {"name": "Coffee (with milk)", "category": "Beverages", "unit": "1 cup (~150ml)", "protein": 2, "carbs": 5, "fat": 2},
            {"name": "Tea (with milk)", "category": "Beverages", "unit": "1 cup (~150ml)", "protein": 1.5, "carbs": 4, "fat": 1.5},
            {"name": "Lemon juice (no salt)", "category": "Beverages", "unit": "1 glass (~200ml)", "protein": 0.2, "carbs": 2, "fat": 0},
            {"name": "Lemon honey water", "category": "Beverages", "unit": "1 glass (~200ml)", "protein": 0.2, "carbs": 12, "fat": 0},
            
            # 🥜 Fats & Misc
            {"name": "Coconut/Sunflower oil", "category": "Fats & Oils", "unit": "1 tbsp (~15ml)", "protein": 0, "carbs": 0, "fat": 13.5},
            {"name": "Honey/Jaggery", "category": "Sweeteners", "unit": "1 tbsp (~20g)", "protein": 0, "carbs": 16, "fat": 0},
            {"name": "Peanut butter", "category": "Fats & Oils", "unit": "1 tbsp (~15g)", "protein": 4, "carbs": 3, "fat": 8},
        ]
        
        for food_data in default_foods:
            food = Food(
                user_id=user_id,
                name=food_data["name"],
                category=food_data["category"],
                unit=food_data["unit"],
                protein=food_data["protein"],
                carbs=food_data["carbs"],
                fat=food_data["fat"],
                calories=self._calculate_calories(food_data["protein"], food_data["carbs"], food_data["fat"])
            )
            session.add(food)
        
    def _calculate_calories(self, protein, carbs, fat):
        """Calculate calories using standard formula: 4*protein + 4*carbs + 9*fat"""
        return (protein * 4) + (carbs * 4) + (fat * 9)
    
    # Food Management
    def add_food(self, user_id, name, category, unit, protein, carbs, fat):
        """Add a new food item to user's database"""
        session = get_session()
        try:
            calories = self._calculate_calories(protein, carbs, fat)
            food = Food(
                user_id=user_id,
                name=name,
                category=category,
                unit=unit,
                protein=protein,
                carbs=carbs,
                fat=fat,
                calories=calories
            )
            session.add(food)
            session.commit()
            return True, "Food added successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error adding food: {str(e)}"
        finally:
            session.close()
    
    def get_user_foods(self, user_id):
        """Get all food items for a user"""
        session = get_session()
        try:
            return session.query(Food).filter(Food.user_id == user_id).all()
        finally:
            session.close()
    
    def search_foods(self, user_id, search_term):
        """Search foods by name for a user"""
        session = get_session()
        try:
            return session.query(Food).filter(
                and_(
                    Food.user_id == user_id,
                    Food.name.ilike(f"%{search_term}%")
                )
            ).all()
        finally:
            session.close()
    
    def import_foods_from_csv(self, user_id, csv_file_object):
        """Import foods from CSV file"""
        session = get_session()
        try:
            # Use pandas to fill empty values with 0 for numeric columns
            # and empty strings for others to prevent errors.
            df = pd.read_csv(csv_file_object).fillna({'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'category': 'Other', 'unit': 'unit'})

            required_columns = ['name', 'category', 'unit', 'protein', 'carbs', 'fat']
            
            if not all(col in df.columns for col in required_columns):
                return False, "CSV missing required columns: name, category, unit, protein, carbs, fat"
            
            # --- DESTRUCTIVE ACTION: Delete all existing foods for this user ---
            session.query(Food).filter(Food.user_id == user_id).delete(synchronize_session=False)
            
            imported_count = 0
            imported_food_names = []
            for _, row in df.iterrows():
                # Clean the input name: remove leading/trailing whitespace
                food_name_from_csv = str(row['name']).strip()

                # Since we deleted all previous foods, we can add every row from the CSV as a new food.
                if food_name_from_csv: # Ensure the name is not empty
                    # Ensure macros default to 0.0 if they are missing/NaN in the CSV
                    protein = float(row.get('protein', 0.0) or 0.0)
                    carbs = float(row.get('carbs', 0.0) or 0.0)
                    fat = float(row.get('fat', 0.0) or 0.0)

                    calories = self._calculate_calories(protein, carbs, fat)

                    food = Food(
                        user_id=user_id,
                        name=food_name_from_csv, # Use the cleaned name
                        category=row['category'],
                        unit=row['unit'],
                        protein=protein,
                        carbs=carbs,
                        fat=fat,
                        calories=calories
                    )
                    session.add(food)
                    imported_count += 1
                    imported_food_names.append(food_name_from_csv)
            
            session.commit()
            message = f"Success! Your food list has been replaced with {imported_count} new food(s) from your file."
            return True, (message, imported_food_names)
        except Exception as e:
            session.rollback()
            return False, f"Error importing foods: {str(e)}"
        finally:
            session.close()
    
    def upsert_foods_from_csv(self, user_id, csv_file_object):
        """
        Adds or updates foods from a CSV file.
        If a food with the same name exists, it's updated. Otherwise, it's added.
        This is a non-destructive operation.
        """
        session = get_session()
        try:
            df = pd.read_csv(csv_file_object).fillna({'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'category': 'Other', 'unit': 'unit'})
            required_columns = ['name', 'category', 'unit', 'protein', 'carbs', 'fat']
            if not all(col in df.columns for col in required_columns):
                return False, "CSV missing required columns: name, category, unit, protein, carbs, fat"

            added_count = 0
            updated_count = 0
            processed_food_names = []

            for _, row in df.iterrows():
                food_name_from_csv = str(row['name']).strip()
                if not food_name_from_csv:
                    continue

                # Find existing food (case-insensitive)
                existing_food = session.query(Food).filter(
                    and_(
                        Food.user_id == user_id,
                        func.lower(Food.name) == food_name_from_csv.lower()
                    )
                ).first()

                protein = float(row.get('protein', 0.0) or 0.0)
                carbs = float(row.get('carbs', 0.0) or 0.0)
                fat = float(row.get('fat', 0.0) or 0.0)
                calories = self._calculate_calories(protein, carbs, fat)

                if existing_food:
                    # Update existing food
                    existing_food.category = row['category']
                    existing_food.unit = row['unit']
                    existing_food.protein = protein
                    existing_food.carbs = carbs
                    existing_food.fat = fat
                    existing_food.calories = calories
                    updated_count += 1
                else:
                    # Add new food
                    new_food = Food(user_id=user_id, name=food_name_from_csv, category=row['category'], unit=row['unit'], protein=protein, carbs=carbs, fat=fat, calories=calories)
                    session.add(new_food)
                    added_count += 1
                processed_food_names.append(food_name_from_csv)
            
            session.commit()
            message = f"Success! Added {added_count} new food(s) and updated {updated_count} existing one(s)."
            return True, (message, processed_food_names)
        except Exception as e:
            session.rollback()
            return False, f"Error processing CSV: {str(e)}"
        finally:
            session.close()

    # Meal Logging
    def log_meal(self, user_id, meal_type, meal_date, food_items):
        """Log a meal with multiple food items"""
        session = get_session()
        try:
            # Create meal
            meal = Meal(
                user_id=user_id,
                meal_type=meal_type,
                date=meal_date
            )
            session.add(meal)
            session.flush()  # Get meal ID
            
            # Add meal items
            for food_id, quantity in food_items:
                meal_item = MealItem(
                    meal_id=meal.id,
                    food_id=food_id,
                    quantity=quantity
                )
                session.add(meal_item)
            
            session.commit()
            return True, "Meal logged successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error logging meal: {str(e)}"
        finally:
            session.close()
    
    def get_daily_nutrition(self, user_id, target_date):
        """Get total nutrition for a specific date"""
        session = get_session()
        try:
            # Get all meals for the date
            meals = session.query(Meal).filter(
                and_(
                    Meal.user_id == user_id,
                    Meal.date == target_date
                )
            ).all()
            
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            total_calories = 0
            
            for meal in meals:
                for item in meal.items:
                    food = item.food
                    total_protein += food.protein * item.quantity
                    total_carbs += food.carbs * item.quantity
                    total_fat += food.fat * item.quantity
                    total_calories += food.calories * item.quantity
            
            return {
                'protein': round(total_protein, 2),
                'carbs': round(total_carbs, 2),
                'fat': round(total_fat, 2),
                'calories': round(total_calories, 2)
            }
        except Exception as e:
            # In a read-only operation, just return default values on error
            return {'protein': 0, 'carbs': 0, 'fat': 0, 'calories': 0}
        finally:
            session.close()
    
    def get_meal_logs(self, user_id, target_date=None):
        """Get meal logs for a user, optionally filtered by date"""
        session = get_session()
        try:
            query = session.query(Meal).options(
                selectinload(Meal.items).selectinload(MealItem.food)
            ).filter(Meal.user_id == user_id)
            
            if target_date:
                query = query.filter(Meal.date == target_date)
            
            return query.order_by(Meal.date.desc(), Meal.created_at.desc()).all()
        finally:
            session.close()
    
    def export_meal_logs(self, user_id):
        """Export all meal logs to pandas DataFrame"""
        # We need to manage the session within this function to ensure
        # all data is loaded before creating the DataFrame.
        session = get_session()
        try:
            meals = session.query(Meal).options(
                selectinload(Meal.items).selectinload(MealItem.food)
            ).filter(Meal.user_id == user_id).order_by(Meal.date.desc(), Meal.created_at.desc()).all()
        finally:
            session.close()
        
        data = []
        for meal in meals:
            for item in meal.items:
                data.append({
                    'date': meal.date,
                    'meal_type': meal.meal_type,
                    'food_name': item.food.name,
                    'quantity': item.quantity,
                    'protein': item.food.protein * item.quantity,
                    'carbs': item.food.carbs * item.quantity,
                    'fat': item.food.fat * item.quantity,
                    'calories': item.food.calories * item.quantity,
                    'logged_at': meal.created_at
                })
        
        return pd.DataFrame(data)
    
    # Sleep Logging
    def log_sleep(self, user_id, sleep_date, hours, quality, notes=None):
        """Log sleep data"""
        session = get_session()
        try:
            # Check if sleep log already exists for this date
            existing = session.query(SleepLog).filter(
                and_(
                    SleepLog.user_id == user_id,
                    SleepLog.date == sleep_date
                )
            ).first()
            
            if existing:
                existing.hours = hours
                existing.quality = quality
                existing.notes = notes
            else:
                sleep_log = SleepLog(
                    user_id=user_id,
                    date=sleep_date,
                    hours=hours,
                    quality=quality,
                    notes=notes
                )
                session.add(sleep_log)
            
            session.commit()
            return True, "Sleep logged successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error logging sleep: {str(e)}"
        finally:
            session.close()
    
    def get_sleep_logs(self, user_id):
        """Get sleep logs for a user"""
        session = get_session()
        try:
            return session.query(SleepLog).filter(
                SleepLog.user_id == user_id
            ).order_by(SleepLog.date.desc()).all()
        finally:
            session.close()
    
    def export_sleep_logs(self, user_id):
        """Export all sleep logs to pandas DataFrame"""
        sleep_logs = self.get_sleep_logs(user_id)
        
        data = []
        for log in sleep_logs:
            data.append({
                'date': log.date,
                'hours': log.hours,
                'quality': log.quality,
                'notes': log.notes,
                'logged_at': log.created_at
            })
        
        return pd.DataFrame(data)

    def export_combined_logs(self, user_id):
        """Export combined meal and sleep logs into two separate DataFrames for Excel sheets."""
        
        # --- DataFrame 1: Detailed Food Log ---
        df_meals_tidy = self.export_meal_logs(user_id)
        if not df_meals_tidy.empty:
            df_meals_tidy['date'] = pd.to_datetime(df_meals_tidy['date']).dt.date

        # --- DataFrame 2: Daily Summary Metrics ---
        # a) Aggregate daily nutrition from the food log
        if not df_meals_tidy.empty:
            df_daily_nutrition = df_meals_tidy.groupby('date').agg(
                total_protein=('protein', 'sum'),
                total_carbs=('carbs', 'sum'),
                total_fat=('fat', 'sum'),
                total_calories=('calories', 'sum')
            ).reset_index()
        else:
            df_daily_nutrition = pd.DataFrame(columns=['date', 'total_protein', 'total_carbs', 'total_fat', 'total_calories'])

        # b) Get sleep logs
        df_sleep = self.export_sleep_logs(user_id)
        if not df_sleep.empty:
            df_sleep['date'] = pd.to_datetime(df_sleep['date']).dt.date
            df_sleep.rename(columns={'quality': 'sleep_quality'}, inplace=True)
            # Only drop 'logged_at' if the DataFrame is not empty
            df_sleep_to_merge = df_sleep.drop(columns=['logged_at'])
        else:
            df_sleep_to_merge = pd.DataFrame(columns=['date', 'hours', 'sleep_quality', 'notes'])

        # c) Merge daily nutrition with sleep logs
        df_daily_metrics = pd.merge(
            df_daily_nutrition,
            df_sleep_to_merge,
            on='date', how='outer'
        ).sort_values(by='date', ascending=False)
        
        return df_meals_tidy, df_daily_metrics

    def reset_user_data(self, user_id):
        """Deletes all logs and custom foods for a user, then restores default foods."""
        session = get_session()
        try:
            # Delete associated MealItems first due to foreign key constraints
            meal_ids_query = session.query(Meal.id).filter(Meal.user_id == user_id)
            session.query(MealItem).filter(MealItem.meal_id.in_(meal_ids_query)).delete(synchronize_session=False)
            
            # Delete Meals
            session.query(Meal).filter(Meal.user_id == user_id).delete(synchronize_session=False)
            
            # Delete SleepLogs
            session.query(SleepLog).filter(SleepLog.user_id == user_id).delete(synchronize_session=False)
            
            # Delete all existing foods for the user
            session.query(Food).filter(Food.user_id == user_id).delete(synchronize_session=False)
            
            # Re-add the default foods
            self._add_default_foods(user_id, session)
            
            session.commit()
            return True, "All your data has been reset successfully."
        except Exception as e:
            session.rollback()
            return False, f"An error occurred while resetting data: {str(e)}"
        finally:
            session.close()