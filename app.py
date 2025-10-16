import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import os
from backend import MuscleTrackerBackend

# Page configuration
st.set_page_config(
    page_title="Muscle Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .nutrition-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .quick-add-btn {
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

class MuscleTrackerApp:
    def __init__(self):
        self.backend = MuscleTrackerBackend()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'page' not in st.session_state:
            st.session_state.page = "login"
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = date.today().isoformat()
        if 'meal_items' not in st.session_state:
            st.session_state.meal_items = []
        if 'meal_builder_items' not in st.session_state:
            st.session_state.meal_builder_items = []
        if 'form_success' not in st.session_state:
            st.session_state.form_success = False
        if 'recently_imported_foods' not in st.session_state:
            st.session_state.recently_imported_foods = None
        if 'reset_quantity' not in st.session_state:
            st.session_state.reset_quantity = False
        if 'meal_item_quantity' not in st.session_state:
            st.session_state.meal_item_quantity = 1.0
    
    def run(self):
        """Main application runner"""
        # Header
        st.markdown('<h1 class="main-header"> Diet Tracker</h1>', unsafe_allow_html=True)
        
        # Navigation
        if st.session_state.user:
            self.show_main_app()
        else:
            self.show_auth_page()
    
    def show_auth_page(self):
        """Show login/signup page"""
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown('<h2 class="sub-header">Login</h2>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login")
                
                if login_btn:
                    if username and password:
                        success, result = self.backend.authenticate_user(username, password)
                        if success:
                            st.session_state.user = result
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result)
                    else:
                        st.error("Please fill all fields")
        
        with tab2:
            st.markdown('<h2 class="sub-header">Sign Up</h2>', unsafe_allow_html=True)
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                signup_btn = st.form_submit_button("Create Account")
                
                if signup_btn:
                    if new_username and new_password and confirm_password:
                        if new_password == confirm_password:
                            success, message = self.backend.create_user(new_username, new_password)
                            if success:
                                st.success(message)
                                st.info("You can now login with your credentials")
                            else:
                                st.error(message)
                        else:
                            st.error("Passwords don't match")
                    else:
                        st.error("Please fill all fields")
    
    def show_main_app(self):
        """Show main application after login"""
        # Sidebar
        with st.sidebar:
            st.write(f"Welcome, **{st.session_state.user.username}**!")
            st.divider()
            
            # Navigation
            page_options = [
                "📊 Dashboard",
                "🍽️ Log Meal", 
                "📥 Import Foods",
                "➕ Add Food",
                "📈 View Logs",
                "😴 Sleep Log",
                "📤 Export Data"
            ]
            
            selected_page = st.radio("Navigation", page_options)
            
            # Date selector
            st.divider()
            selected_date = st.date_input("Select Date", value=date.today())
            st.session_state.selected_date = selected_date.isoformat()
            
            # Logout button
            st.divider()
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.meal_items = []
                st.session_state.meal_builder_items = []
                st.session_state.recently_imported_foods = None
                st.rerun()
        
        # Main content based on selection
        if selected_page == "📊 Dashboard":
            self.show_dashboard()
        elif selected_page == "🍽️ Log Meal":
            self.show_log_meal()
        elif selected_page == "📥 Import Foods":
            self.show_import_foods()
        elif selected_page == "➕ Add Food":
            self.show_add_food()
        elif selected_page == "📈 View Logs":
            self.show_view_logs()
        elif selected_page == "😴 Sleep Log":
            self.show_sleep_log()
        elif selected_page == "📤 Export Data":
            self.show_export_data()
    
    def show_dashboard(self):
        """Show dashboard with daily summary"""
        st.markdown('<h2 class="sub-header">📊 Daily Summary</h2>', unsafe_allow_html=True)
        
        # Date info
        st.write(f"**Date:** {st.session_state.selected_date}")
        
        # Nutrition summary
        nutrition = self.backend.get_daily_nutrition(
            st.session_state.user.id, 
            st.session_state.selected_date
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Calories", f"{nutrition['calories']} kcal")
        with col2:
            st.metric("Protein", f"{nutrition['protein']}g")
        with col3:
            st.metric("Carbs", f"{nutrition['carbs']}g")
        with col4:
            st.metric("Fat", f"{nutrition['fat']}g")
        
        # Recent meals
        st.markdown('<h3 class="sub-header">Recent Meals</h3>', unsafe_allow_html=True)
        recent_meals = self.backend.get_meal_logs(
            st.session_state.user.id, 
            st.session_state.selected_date
        )
        
        if recent_meals:
            for meal in recent_meals:
                with st.expander(f"{meal.meal_type} - {len(meal.items)} items"):
                    total_protein = sum(item.food.protein * item.quantity for item in meal.items)
                    total_carbs = sum(item.food.carbs * item.quantity for item in meal.items)
                    total_fat = sum(item.food.fat * item.quantity for item in meal.items)
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write("**Food Items:**")
                        for item in meal.items:
                            st.write(f"- {item.quantity}x {item.food.name} ({item.food.unit})")
                    with col2:
                        st.write("**Nutrition:**")
                        st.write(f"Protein: {total_protein:.1f}g")
                        st.write(f"Carbs: {total_carbs:.1f}g")
                        st.write(f"Fat: {total_fat:.1f}g")
        else:
            st.info("No meals logged for today. Go to 'Log Meal' to add your first meal!")
    
    def show_log_meal(self):
        """A professional, interactive meal logging interface using a 'shopping cart' model."""
        st.markdown('<h2 class="sub-header">🍽️ Log Meal</h2>', unsafe_allow_html=True)

        # Check if we need to reset the quantity from the previous run
        if st.session_state.get('reset_quantity', False):
            st.session_state.meal_item_quantity = 1.0
            st.session_state.reset_quantity = False

        # --- Step 1: Meal Context (Type and Date) ---
        st.markdown("#### Step 1: Set Meal Details")
        col1, col2 = st.columns(2)
        with col1:
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack"],
                key="meal_type_select"
            )
        with col2:
            meal_date = st.date_input(
                "Meal Date",
                value=date.fromisoformat(st.session_state.selected_date),
                key="meal_date_select"
            )
        st.divider()

        # --- Step 2: Add Foods to the Meal ---
        st.markdown("#### Step 2: Add Foods")
        user_foods = self.backend.get_user_foods(st.session_state.user.id)

        # If foods were recently imported, filter the list to show only those.
        # Otherwise, show all user foods.
        if st.session_state.recently_imported_foods:
            filtered_foods = [f for f in user_foods if f.name in st.session_state.recently_imported_foods]
            st.info(f"Showing the {len(filtered_foods)} food(s) from your recent import. Your old food list has been replaced.")
        else:
            filtered_foods = user_foods

        food_options = {f"({f.category}) {f.name} - {f.unit}": f for f in sorted(filtered_foods, key=lambda x: x.name)}

        with st.form("add_food_to_meal_form"):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                selected_food_key = st.selectbox("Search and select a food item", options=list(food_options.keys()), label_visibility="collapsed")
            with c2:
                # The value is read from session_state after the form is submitted.
                st.number_input("Quantity", min_value=0.1, value=1.0, step=0.5, label_visibility="collapsed", key="meal_item_quantity")
                st.number_input("Quantity", min_value=0.1, step=0.5, label_visibility="collapsed", key="meal_item_quantity")
            with c3:
                add_food_btn = st.form_submit_button("➕ Add", use_container_width=True)

            if add_food_btn and selected_food_key:
                selected_food = food_options[selected_food_key]
                # Read the quantity from session_state here to get the submitted value
                st.session_state.meal_builder_items.append({'food': selected_food, 'quantity': st.session_state.meal_item_quantity})
                st.session_state.reset_quantity = True # Set a flag to reset on the next run
                st.rerun()

        st.divider()

        # --- Step 3: Review and Log Meal ---
        st.markdown("#### Step 3: Review and Log")
        if not st.session_state.meal_builder_items:
            st.info("Your meal is empty. Add some foods above to get started.")
        else:
            # Display items in a structured way
            total_protein, total_carbs, total_fat, total_calories = 0, 0, 0, 0
            
            for i, item in enumerate(st.session_state.meal_builder_items):
                food = item['food']
                qty = item['quantity']
                
                # Calculate totals
                total_protein += food.protein * qty
                total_carbs += food.carbs * qty
                total_fat += food.fat * qty
                total_calories += food.calories * qty
                
                # Display item with a remove button
                c1, c2, c3 = st.columns([4, 2, 1])
                with c1:
                    st.write(f"**{food.name}**")
                with c2:
                    st.write(f"{qty} x *({food.unit})*")
                with c3:
                    # Use a unique key for each remove button
                    if st.button(f"➖ Remove", key=f"remove_{i}", use_container_width=True):
                        st.session_state.meal_builder_items.pop(i)
                        st.rerun()
            
            # Display meal totals
            st.markdown("---")
            st.markdown("**Meal Totals:**")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Calories", f"{total_calories:.1f} kcal")
            m2.metric("Protein", f"{total_protein:.1f} g")
            m3.metric("Carbs", f"{total_carbs:.1f} g")
            m4.metric("Fat", f"{total_fat:.1f} g")

            # Final action buttons
            st.markdown("---")
            log_c1, log_c2 = st.columns(2)
            with log_c1:
                if st.button("✅ Log This Meal", use_container_width=True, type="primary"):
                    food_items_to_log = [(item['food'].id, item['quantity']) for item in st.session_state.meal_builder_items]
                    success, message = self.backend.log_meal(
                        st.session_state.user.id, meal_type, meal_date.isoformat(), food_items_to_log
                    )
                    if success:
                        st.success("🎉 Meal logged successfully!")
                        st.session_state.meal_builder_items = [] # Clear the builder
                        # st.balloons()
                    else:
                        st.error(f"Error: {message}")
            with log_c2:
                if st.button("🗑️ Clear Meal", use_container_width=True):
                    st.session_state.meal_builder_items = []
                    st.rerun()
    
    def show_import_foods(self):
        """Show food import interface"""
        st.markdown('<h2 class="sub-header">📥 Import Foods from CSV</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
            **CSV Format Required:**
            **Warning:** This will **replace** your entire existing food list with the contents of the CSV file.
            - **Columns:** `name`, `category`, `unit`, `protein`, `carbs`, `fat`
            - `protein`, `carbs`, and `fat` values should be in grams per the specified `unit`.
            - `calories` will be calculated automatically based on the macros.
            """)
            
            uploaded_file = st.file_uploader(
                "Choose CSV file", 
                type=['csv'],
                help="Upload a CSV file with the required columns"
            )
        
        with col2:
            # Download template
            template_df = pd.DataFrame({
                'name': ['Example Food'],
                'category': ['Grains & Carbs'],
                'unit': ['100g'],
                'protein': [10.0],
                'carbs': [75.0],
                'fat': [2.5]
            })
            st.download_button(
                label="Download Template CSV",
                data=template_df.to_csv(index=False),
                file_name="food_import_template.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        if uploaded_file is not None:
            # Preview data
            try:
                df = pd.read_csv(uploaded_file)
                st.write("**Preview of your data:**")
                st.dataframe(df.head())
                
                if st.button("Import Foods", use_container_width=True, key="import_foods_btn"):
                    # Reset buffer to the beginning before reading again in the backend
                    uploaded_file.seek(0)
                    success, result = self.backend.import_foods_from_csv(
                        st.session_state.user.id,
                        uploaded_file
                    )
                    if success:
                        message, imported_food_names = result # result is now a tuple (message, list)
                        st.success(message)
                        st.session_state.recently_imported_foods = imported_food_names
                        st.info("Go to the 'Log Meal' page to use your new food list!")
                    else:
                        st.error(result)
            
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
    
    def show_add_food(self):
        """Show manual food addition interface"""
        st.markdown('<h2 class="sub-header">➕ Add or Update Foods</h2>', unsafe_allow_html=True)
        
        with st.form("add_food_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Food Name*")
                category = st.selectbox(
                    "Category*",
                    ["Grains & Carbs", "Proteins", "Vegetables", "Fruits", 
                     "Dairy", "Beverages", "Fats & Oils", "Sweeteners", 
                     "Cooked Dishes", "Common Foods", "Other"]
                )
                unit = st.text_input("Unit* (e.g., 100g, 1 cup, 1 piece)")
            
            with col2:
                protein = st.number_input("Protein (g)*", min_value=0.0, step=0.1, value=0.0)
                carbs = st.number_input("Carbs (g)*", min_value=0.0, step=0.1, value=0.0)
                fat = st.number_input("Fat (g)*", min_value=0.0, step=0.1, value=0.0)
            
            # Calculate calories
            calories = (protein * 4) + (carbs * 4) + (fat * 9)
            st.write(f"**Calculated Calories:** {calories:.1f} kcal")
            
            submit_food = st.form_submit_button("Add Food", use_container_width=True)
            
            if submit_food:
                if name and category and unit:
                    success, message = self.backend.add_food(
                        st.session_state.user.id,
                        name,
                        category,
                        unit,
                        protein,
                        carbs,
                        fat
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all required fields (*)")
        
        st.divider()
        st.markdown("#### Or, Add/Update from CSV")
        st.info("""
        Upload a CSV to add new foods or update existing ones in your database.
        - If a food name in the CSV matches one of your existing foods, it will be **updated**.
        - If the food name is new, it will be **added**.
        - This is a non-destructive way to bulk-edit your food list.
        """)

        uploaded_file = st.file_uploader(
            "Choose a CSV file to add or update foods", 
            type=['csv'],
            key="add_update_csv"
        )

        if uploaded_file is not None:
            if st.button("Process CSV File", use_container_width=True, key="process_csv_btn"):
                # Reset buffer to the beginning before reading again in the backend
                uploaded_file.seek(0)
                success, result = self.backend.upsert_foods_from_csv(
                    st.session_state.user.id,
                    uploaded_file
                )
                if success:
                    message, processed_food_names = result
                    st.success(message)
                    # Clear the filter from any previous "Import" action to ensure all foods are now visible.
                    st.session_state.recently_imported_foods = None
                    st.info("Go to the 'Log Meal' page to see the changes!")
                else:
                    st.error(result)
    
    def show_view_logs(self):
        """Show meal logs and nutrition history"""
        st.markdown('<h2 class="sub-header">📈 Meal Logs & History</h2>', unsafe_allow_html=True)
        
        # Date filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today(), key="start_date_logs")
        with col2:
            end_date = st.date_input("End Date", value=date.today(), key="end_date_logs")
        
        # Get logs for date range
        all_logs = self.backend.get_meal_logs(st.session_state.user.id)
        filtered_logs = [
            log for log in all_logs 
            if start_date <= date.fromisoformat(log.date) <= end_date
        ]
        
        if filtered_logs:
            # Display logs
            for meal in filtered_logs:
                with st.expander(f"{meal.date} - {meal.meal_type}"):
                    total_protein = sum(item.food.protein * item.quantity for item in meal.items)
                    total_carbs = sum(item.food.carbs * item.quantity for item in meal.items)
                    total_fat = sum(item.food.fat * item.quantity for item in meal.items)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Food Items:**")
                        for item in meal.items:
                            st.write(f"- {item.quantity}x {item.food.name} ({item.food.unit})")
                    
                    with col2:
                        st.write("**Nutrition:**")
                        st.write(f"Protein: {total_protein:.1f}g")
                        st.write(f"Carbs: {total_carbs:.1f}g")
                        st.write(f"Fat: {total_fat:.1f}g")
        else:
            st.info("No meal logs found for the selected date range.")
    
    def show_sleep_log(self):
        """A professional and visual sleep logging interface."""
        st.markdown('<h2 class="sub-header">😴 Sleep Log</h2>', unsafe_allow_html=True)

        # --- 1. Visual Summary: Chart and Metrics ---
        st.markdown("#### Last 7 Days at a Glance")
        sleep_logs = self.backend.get_sleep_logs(st.session_state.user.id)
        recent_logs = sleep_logs[:7]

        if recent_logs:
            df_sleep = pd.DataFrame([{'date': log.date, 'hours': log.hours} for log in recent_logs])
            df_sleep['date'] = pd.to_datetime(df_sleep['date'])
            df_sleep = df_sleep.set_index('date').sort_index()

            avg_hours = df_sleep['hours'].mean()
            st.metric("7-Day Average Sleep", f"{avg_hours:.1f} hours")
            st.bar_chart(df_sleep['hours'])
        else:
            st.info("No sleep data yet. Log your sleep below to see your trends!")

        st.divider()

        # --- 2. Logging Form (in an expander for a cleaner look) ---
        with st.expander("✏️ Log or Update Sleep", expanded=True):
            with st.form("sleep_log_form"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    sleep_date = st.date_input("Date", value=date.fromisoformat(st.session_state.selected_date))
                    quality = st.selectbox("Sleep Quality", ["Excellent", "Good", "Fair", "Poor"])
                with c2:
                    hours = st.slider("Hours Slept", min_value=0.0, max_value=16.0, value=7.5, step=0.5)
                    notes = st.text_area("Notes (optional)")

                submit_sleep = st.form_submit_button("💾 Save Sleep Log", use_container_width=True, type="primary")

                if submit_sleep:
                    success, message = self.backend.log_sleep(st.session_state.user.id, sleep_date.isoformat(), hours, quality, notes)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        st.divider()

        # --- 3. Detailed History ---
        st.markdown("#### 📜 Sleep History")
        if sleep_logs:
            for log in sleep_logs:
                with st.container():
                    c1, c2, c3 = st.columns([2, 2, 4])
                    c1.write(f"**{log.date}**")
                    c2.write(f"{log.hours} hours ({log.quality})")
                    c3.write(f"*{log.notes or 'No notes'}*")
                    st.markdown("---", help="line") # A subtle separator
        else:
            st.info("Your sleep history will appear here once you start logging.")
    
    def show_export_data(self):
        """Show data export interface"""
        st.markdown('<h2 class="sub-header">📤 Export Your Data</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Export Options:**
            - A combined file of daily nutrition and sleep data
            - All your custom food items
            """)

            # Prepare health data for download
            df_food_log, df_daily_metrics = self.backend.export_combined_logs(st.session_state.user.id)
            if not df_food_log.empty or not df_daily_metrics.empty:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_food_log.to_excel(writer, index=False, sheet_name='Food Log')
                    df_daily_metrics.to_excel(writer, index=False, sheet_name='Daily Metrics')
                excel_data = output.getvalue()

                st.download_button(
                    label="Download Health Data (Excel)",
                    data=excel_data,
                    file_name=f"health_data_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_health_data_btn"
                )
            else:
                st.button("Download Health Data (Excel)", use_container_width=True, disabled=True)
        
        with col2:
            # Prepare food database for download
            foods = self.backend.get_user_foods(st.session_state.user.id)
            if foods:
                food_data = [{
                    'name': food.name, 'category': food.category, 'unit': food.unit,
                    'protein': food.protein, 'carbs': food.carbs, 'fat': food.fat,
                    'calories': food.calories
                } for food in foods]
                
                df_foods = pd.DataFrame(food_data)
                csv_foods = df_foods.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Download Food Database (CSV)",
                    data=csv_foods,
                    file_name=f"my_foods_{date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_food_db_btn"
                )
            else:
                st.button("Download Food Database (CSV)", use_container_width=True, disabled=True)

        st.divider()
        
        # Destructive actions area
        st.markdown("### ⚠️ Danger Zone")
        with st.expander("Reset Account Data"):
            st.warning("This action is irreversible. It will delete all your meal logs, sleep logs, and custom foods, resetting your account to its original state.")
            
            if st.button("I understand, reset my data", use_container_width=True, type="primary", key="reset_data_btn"):
                success, message = self.backend.reset_user_data(st.session_state.user.id)
                if success:
                    st.success(message)
                    st.info("Your page will now refresh.")
                    st.rerun()
                else:
                    st.error(message)

# Run the app
if __name__ == "__main__":
    app = MuscleTrackerApp()
    app.run()