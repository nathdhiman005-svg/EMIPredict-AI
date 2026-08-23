from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class FinancialAssessment(Base):
    __tablename__ = "financial_assessments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Categorical Inputs (8 fields)
    gender = Column(String(10), nullable=False)
    marital_status = Column(String(20), nullable=False)
    education = Column(String(50), nullable=False)
    employment_type = Column(String(50), nullable=False)
    company_type = Column(String(50), nullable=False)
    house_type = Column(String(50), nullable=False)
    existing_loans = Column(String(10), nullable=False)
    emi_scenario = Column(String(100), nullable=False)

    # Numerical Inputs (17 fields)
    age = Column(Float, nullable=False)
    monthly_salary = Column(Float, nullable=False)
    years_of_employment = Column(Float, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    family_size = Column(Float, nullable=False)
    dependents = Column(Float, nullable=False)
    school_fees = Column(Float, nullable=False)
    college_fees = Column(Float, nullable=False)
    travel_expenses = Column(Float, nullable=False)
    groceries_utilities = Column(Float, nullable=False)
    other_monthly_expenses = Column(Float, nullable=False)
    current_emi_amount = Column(Float, nullable=False)
    credit_score = Column(Float, nullable=False)
    bank_balance = Column(Float, nullable=False)
    emergency_fund = Column(Float, nullable=False)
    requested_amount = Column(Float, nullable=False)
    requested_tenure = Column(Float, nullable=False)

    # ML Predictions (3 fields)
    predicted_eligibility = Column(String(50), nullable=True)
    prediction_probabilities = Column(String(255), nullable=True)
    predicted_max_monthly_emi = Column(Float, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelPerformance(Base):
    __tablename__ = "model_performance_records"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    problem_type = Column(String(50), nullable=False) # Classification or Regression
    purpose = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="Active")
    
    # Classification Metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    
    # Regression Metrics
    r2_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
