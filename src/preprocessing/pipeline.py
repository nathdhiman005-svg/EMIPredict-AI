import pandas as pd
from .cleaning import clean_malformed_floats, standardize_gender, replace_invalid_domain_values
from .imputation import DataImputer

class DataPreprocessor:
    """
    Orchestrates the complete Phase 2 preprocessing workflow.
    Designed with a fit/transform interface to ensure preprocessing 
    parameters learned on the training set are correctly applied to 
    the test set and real-time user input.
    """
    def __init__(self):
        self.imputer = DataImputer()
        self.is_fitted_ = False
        self.malformed_cols_ = ['age', 'monthly_salary', 'bank_balance']
        
    def _apply_cleaning(self, df):
        """
        Applies pure data cleaning and domain rule handling.
        This step requires no learned parameters.
        """
        # 1. Clean malformed floats
        df = clean_malformed_floats(df, self.malformed_cols_)
        
        # 2. Standardize gender
        df = standardize_gender(df, 'gender')
        
        # 3. Replace invalid domain values with NaN
        df = replace_invalid_domain_values(df)
        
        return df

    def fit(self, X, y=None):
        """
        Learns the preprocessing parameters (imputation medians and modes) 
        from the training data.
        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input X must be a pandas DataFrame.")
            
        # Create a working copy
        df = X.copy()
        
        # Apply cleaning to ensure we don't learn parameters from invalid data
        df = self._apply_cleaning(df)
        
        # Fit the imputer on the cleaned data
        self.imputer.fit(df)
        
        self.is_fitted_ = True
        return self

    def transform(self, X):
        """
        Transforms the data using the already learned parameters.
        """
        if not self.is_fitted_:
            raise RuntimeError("You must fit the preprocessor before calling transform.")
            
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input X must be a pandas DataFrame.")
            
        # Create a working copy
        df = X.copy()
        
        # 1. Apply stateless cleaning
        df = self._apply_cleaning(df)
        
        # 2. Apply learned imputations
        df = self.imputer.transform(df)
        
        return df

    def fit_transform(self, X, y=None):
        """
        Fits to the data and then transforms it.
        """
        return self.fit(X, y).transform(X)
