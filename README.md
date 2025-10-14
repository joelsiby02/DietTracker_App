# Diet Tracker - Nutrition and Fitness Tracking Application

A comprehensive web application built with Streamlit, SQlLite for tracking nutrition intake, meal logging, and sleep patterns. Features personalized food databases and detailed analytics.

## Features

### User Management
- Secure user registration and login system
- Individual user sessions with password protection
- Personalized data isolation

### Meal Tracking
- Advanced meal builder interface for adding multiple foods
- Support for various quantity types:
  - Discrete items (eggs, dosa, chapathi)
  - Weight-based quantities (grams for rice, curry)
  - Volume measurements (cups, spoons)
  - Custom units (scoops for protein powder)
- Real-time nutrition calculation
- Meal categorization (Breakfast, Lunch, Dinner, Snack)

### Nutrition Analytics
- Daily macronutrient summary (calories, protein, carbohydrates, fat)
- Historical meal tracking with date filtering
- Comprehensive nutrition breakdowns

### Food Database Management
- Personal food databases per user
- Pre-configured with 40+ common Indian food items
- Bulk import/export functionality via CSV
- Manual food entry with complete nutritional information

### Sleep Monitoring
- Sleep duration and quality tracking
- Visual trend analysis with charts
- Historical sleep data with notes

### Data Management
- Export capabilities to Excel and CSV formats
- Combined health reports integrating nutrition and sleep data
- Account reset functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Development Setup

1. Clone the repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the application:
```bash
streamlit run app.py
```

4. Access the application at `http://localhost:8501` #in case if it didnt open automatically



## Project Structure

```
muscle_tracker_app/
├── app.py                 # Main application interface
├── backend.py             # Business logic and data operations
├── database.py            # Database models and configuration
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Database Schema

The application utilizes SQLite with the following core tables:

- **users**: User account information and authentication
- **foods**: Individual food items (user-specific)
- **meals**: Meal recording entries
- **meal_items**: Constituent foods within meals
- **sleep_logs**: Sleep tracking records


## User Guide

### Initial Setup
1. Create a new user account
2. Access pre-loaded food database containing common Indian foods
3. Begin logging meals using the meal builder interface
4. Optionally track sleep patterns

### Meal Logging Process
1. Navigate to "Log Meal" section
2. Specify meal type and date
3. Search and select food items with appropriate quantities
4. Review nutritional summary
5. Save complete meal record

### Data Management
- **Export**: Download comprehensive reports in Excel format
- **Import**: Add multiple foods using CSV templates
- **Reset**: Clear all user data and restore default food database

## Technical Specifications

### Architecture
- **Frontend**: Streamlit framework
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite
- **Authentication**: bcrypt hashing
- **Data Processing**: pandas library

### Security Implementation
- Secure password hashing
- Parameterized queries to prevent SQL injection
- User data segregation
- Robust session management

## Included Food Database

The application includes nutritional data for common Indian foods across categories:

- Grains and Carbohydrates: Matta rice, Whole wheat roti, Oats
- Prepared Dishes: Various biriyani, curry, and dal preparations
- Protein Sources: Eggs, Chicken, Soya products, Legumes
- Vegetables: Onion, Tomato, Cucumber, Carrot, Leafy greens
- Fruits: Banana, Papaya, Citrus fruits, Apple
- Beverages: Coffee, Tea, Fruit juices
- Fats and Condiments: Cooking oils, Sweeteners, Nut butters

## Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/description`)
3. Implement changes with appropriate testing
4. Commit changes (`git commit -m 'Feature description'`)
5. Push to branch (`git push origin feature/description`)
6. Submit Pull Request

## License

This project is distributed under the MIT License. Refer to LICENSE file for complete details.

## Support

For technical issues or questions:
1. Review existing issues in the issue tracker
2. Create new issue with detailed description and reproduction steps

## Acknowledgments

- Built using Streamlit framework
- Nutritional data based on standard food composition tables
- Designed for practical daily nutrition tracking

---

Begin tracking your nutritional intake and health metrics with this comprehensive dietary monitoring application.