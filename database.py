import sqlalchemy as db
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import bcrypt
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    foods = relationship("Food", back_populates="user")
    meals = relationship("Meal", back_populates="user")
    sleep_logs = relationship("SleepLog", back_populates="user")
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Food(Base):
    __tablename__ = 'foods'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    unit = Column(String(50))
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    calories = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="foods")
    meal_items = relationship("MealItem", back_populates="food")

class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    meal_type = Column(String(20), nullable=False)  # Breakfast, Lunch, Dinner, Snack
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meals")
    items = relationship("MealItem", back_populates="meal")

class MealItem(Base):
    __tablename__ = 'meal_items'
    
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'), nullable=False)
    food_id = Column(Integer, ForeignKey('foods.id'), nullable=False)
    quantity = Column(Float, default=1.0)
    
    # Relationships
    meal = relationship("Meal", back_populates="items")
    food = relationship("Food", back_populates="meal_items")

class SleepLog(Base):
    __tablename__ = 'sleep_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    hours = Column(Float, nullable=False)
    quality = Column(String(20))  # Excellent, Good, Fair, Poor
    notes = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sleep_logs")

# Database setup
def init_db():
    engine = create_engine('sqlite:///muscle_tracker.db', echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()