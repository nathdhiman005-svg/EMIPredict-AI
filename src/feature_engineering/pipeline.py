import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from .features import (
    compute_expense_features,
    compute_ratio_features,
    compute_coverage_features,
    compute_interaction_features
)

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible pipeline for generating financial and affordability features.
    It applies stateless, row-wise feature engineering.
    """
    
    def __init__(self):
        self.engineered_features_ = [
            'total_monthly_expenses',
            'total_financial_burden',
            'income_after_expenses',
            'emi_to_income_ratio',
            'expense_to_income_ratio',
            'financial_burden_ratio',
            'emergency_fund_coverage',
            'bank_balance_coverage',
            'salary_credit_interaction'
        ]

    def fit(self, X: pd.DataFrame, y=None):
        """
        No-op since feature engineering logic is stateless.
        """
        return self
        
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Applies feature engineering functions to the dataset.
        """
        X_out = X.copy()
        
        # Apply sequential transformations
        X_out = compute_expense_features(X_out)
        X_out = compute_ratio_features(X_out)
        X_out = compute_coverage_features(X_out)
        X_out = compute_interaction_features(X_out)
        
        return X_out
