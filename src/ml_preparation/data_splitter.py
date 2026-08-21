import pandas as pd
from sklearn.model_selection import train_test_split

def prepare_data_splits(
    df: pd.DataFrame, 
    classification_target: str = 'emi_eligibility', 
    regression_target: str = 'max_monthly_emi',
    test_size_temp: float = 0.30,
    val_test_ratio: float = 0.50,
    random_state: int = 42
):
    """
    Imputes target variables if necessary (offline only), separates features from targets,
    and performs a 70/15/15 train/val/test split.
    
    Returns:
        dict containing the splits for both classification and regression tasks:
        {
            'classification': (X_train, X_val, X_test, y_train, y_val, y_test),
            'regression': (X_train, X_val, X_test, y_train, y_val, y_test)
        }
    """
    df_clean = df.copy()
    
    # 1. Target Imputation for offline splitting
    if df_clean[classification_target].isna().sum() > 0:
        mode_val = df_clean[classification_target].mode()[0]
        df_clean[classification_target] = df_clean[classification_target].fillna(mode_val)
        
    # 2. Separate X and y
    excluded_features = [classification_target, regression_target]
    X_full = df_clean.drop(columns=excluded_features)
    
    y_class = df_clean[classification_target]
    y_reg = df_clean[regression_target]
    
    # 3. Classification splits (stratified)
    X_c_train, X_c_temp, y_c_train, y_c_temp = train_test_split(
        X_full, y_class,
        test_size=test_size_temp,
        random_state=random_state,
        stratify=y_class
    )
    X_c_val, X_c_test, y_c_val, y_c_test = train_test_split(
        X_c_temp, y_c_temp,
        test_size=val_test_ratio,
        random_state=random_state,
        stratify=y_c_temp
    )
    
    # 4. Regression splits (no stratification)
    X_r_train, X_r_temp, y_r_train, y_r_temp = train_test_split(
        X_full, y_reg,
        test_size=test_size_temp,
        random_state=random_state
    )
    X_r_val, X_r_test, y_r_val, y_r_test = train_test_split(
        X_r_temp, y_r_temp,
        test_size=val_test_ratio,
        random_state=random_state
    )
    
    return {
        'classification': (X_c_train, X_c_val, X_c_test, y_c_train, y_c_val, y_c_test),
        'regression': (X_r_train, X_r_val, X_r_test, y_r_train, y_r_val, y_r_test)
    }
