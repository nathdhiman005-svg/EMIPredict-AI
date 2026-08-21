import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler

class MLPreparator(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible pipeline for ML Data Preparation.
    Encodes categorical features and scales continuous numerical features.
    It expects all 34 features and returns a dataframe with 49 features.
    """
    
    def __init__(self):
        self.binary_mappings = {
            'gender': {'F': 0, 'M': 1},
            'marital_status': {'Single': 0, 'Married': 1},
            'existing_loans': {'No': 0, 'Yes': 1}
        }
        self.ohe_features = [
            'education', 'employment_type', 'company_type', 
            'house_type', 'emi_scenario'
        ]
        self.continuous_features = [
            'age', 'monthly_salary', 'years_of_employment', 'monthly_rent', 'family_size',
            'dependents', 'school_fees', 'college_fees', 'travel_expenses', 'groceries_utilities',
            'other_monthly_expenses', 'current_emi_amount', 'credit_score', 'bank_balance',
            'emergency_fund', 'requested_amount', 'requested_tenure', 'total_monthly_expenses',
            'total_financial_burden', 'income_after_expenses', 'emi_to_income_ratio',
            'expense_to_income_ratio', 'financial_burden_ratio', 'emergency_fund_coverage',
            'bank_balance_coverage', 'salary_credit_interaction'
        ]
        
        self.ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.scaler = StandardScaler()
        self.feature_names_out_ = None

    def fit(self, X: pd.DataFrame, y=None):
        X_copy = X.copy()
        
        # Apply binary mappings for fitting (not strictly necessary for OHE/Scaler, 
        # but good for consistency if we wanted to introspect)
        for col, mapping in self.binary_mappings.items():
            if col in X_copy.columns:
                X_copy[col] = X_copy[col].replace(mapping)
                
        # Fit OneHotEncoder
        self.ohe.fit(X_copy[self.ohe_features])
        
        # Fit StandardScaler
        self.scaler.fit(X_copy[self.continuous_features])
        
        # Store expected features order for transform
        ohe_feature_names = list(self.ohe.get_feature_names_out(self.ohe_features))
        # Final columns order: continuous -> binary -> one-hot
        self.feature_names_out_ = self.continuous_features + list(self.binary_mappings.keys()) + ohe_feature_names
        
        return self
        
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_copy = X.copy()
        
        # Binary map
        for col, mapping in self.binary_mappings.items():
            if col in X_copy.columns:
                X_copy[col] = X_copy[col].replace(mapping)
                
        # Transform OHE
        ohe_array = self.ohe.transform(X_copy[self.ohe_features])
        ohe_df = pd.DataFrame(
            ohe_array, 
            columns=self.ohe.get_feature_names_out(self.ohe_features), 
            index=X.index
        )
        
        # Transform Scaler
        X_copy[self.continuous_features] = self.scaler.transform(X_copy[self.continuous_features])
        
        # Drop original OHE features
        X_copy = X_copy.drop(columns=self.ohe_features)
        
        # Concat original (now with binary mapped and continuous scaled) + OHE
        X_out = pd.concat([X_copy, ohe_df], axis=1)
        
        # Ensure we only return the final expected 49 features in consistent order.
        # Drop any unexpected columns (like targets if they accidentally leaked in)
        return X_out[self.feature_names_out_]
