import pandas as pd
import numpy as np

class DataImputer:
    """
    Learns imputation parameters (medians, modes) from the training data during fit()
    and applies them consistently during transform().
    """
    def __init__(self):
        self.numerical_medians_ = {}
        self.categorical_modes_ = {}
        self.is_fitted_ = False

    def fit(self, X, y=None):
        """
        Learns medians for numerical columns and modes for categorical columns.
        Ignores target variables ('emi_eligibility', 'max_monthly_emi') if they are in X.
        """
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input X must be a pandas DataFrame.")
            
        df = X.copy()
        
        # Targets that should not be imputed by this imputer
        target_cols = ['emi_eligibility', 'max_monthly_emi']
        
        # Separate features to impute
        imputable_cols = [col for col in df.columns if col not in target_cols]
        
        # Identify types
        numerical_cols = df[imputable_cols].select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df[imputable_cols].select_dtypes(exclude=np.number).columns.tolist()
        
        # Learn medians for numericals
        for col in numerical_cols:
            self.numerical_medians_[col] = df[col].median()
            
        # Learn modes for categoricals
        for col in categorical_cols:
            if not df[col].dropna().empty:
                # Mode returns a Series, take the first one
                self.categorical_modes_[col] = df[col].mode()[0]
            else:
                self.categorical_modes_[col] = 'Unknown' # Fallback for completely empty columns
                
        self.is_fitted_ = True
        return self

    def transform(self, X):
        """
        Applies the learned medians and modes to fill missing values.
        """
        if not self.is_fitted_:
            raise RuntimeError("You must fit the imputer before calling transform.")
            
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input X must be a pandas DataFrame.")
            
        df = X.copy()
        
        # Apply numerical medians
        for col, median_val in self.numerical_medians_.items():
            if col in df.columns:
                df[col] = df[col].fillna(median_val)
                
        # Apply categorical modes
        for col, mode_val in self.categorical_modes_.items():
            if col in df.columns:
                df[col] = df[col].fillna(mode_val)
                
        return df

    def fit_transform(self, X, y=None):
        """
        Fits to the data and then transforms it.
        """
        return self.fit(X, y).transform(X)
