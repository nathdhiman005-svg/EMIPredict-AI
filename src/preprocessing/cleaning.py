import pandas as pd
import numpy as np

def clean_malformed_float_string(value):
    """
    Cleans strings with multiple decimal points (e.g., '58.0.0' to '58.0').
    Returns the cleaned string representation or np.nan if the value is already NaN.
    """
    if pd.isna(value):
        return np.nan

    s_value = str(value).strip()

    # Check for the specific malformed pattern 'X.Y.Z...'
    if s_value.count('.') > 1:
        parts = s_value.split('.')
        if len(parts) >= 2:
            s_value = parts[0] + '.' + parts[1]

    return s_value

def clean_malformed_floats(df, columns):
    """
    Applies malformed float cleaning to specified columns and converts them to float.
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_malformed_float_string)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def standardize_gender(df, column='gender'):
    """
    Normalizes case, strips whitespace, and enforces mapping to 'M' and 'F'.
    Ambiguous values are converted to NaN.
    """
    if column not in df.columns:
        return df
        
    df = df.copy()
    
    # Normalize capitalization and remove whitespace
    df['gender_normalized'] = df[column].astype(str).str.upper().str.strip()
    
    gender_mapping = {
        'M': 'M',
        'MALE': 'M',
        'F': 'F',
        'FEMALE': 'F'
    }
    
    # Identify ambiguous values (values not in our mapping)
    ambiguous_values = df[~df['gender_normalized'].isin(gender_mapping.keys())]['gender_normalized'].unique()
    
    if len(ambiguous_values) > 0:
        df.loc[df['gender_normalized'].isin(ambiguous_values), 'gender_normalized'] = np.nan
        
    # Apply mapping
    df[column] = df['gender_normalized'].map(gender_mapping)
    df = df.drop(columns=['gender_normalized'])
    
    return df

def replace_invalid_domain_values(df):
    """
    Converts domain rule violations to NaN. 
    Target variables (emi_eligibility, max_monthly_emi) are explicitly ignored.
    """
    df = df.copy()
    
    def count_and_replace_invalid(df, column, condition):
        if column in df.columns:
            invalid_mask = condition(df[column])
            df.loc[invalid_mask, column] = np.nan
        return df

    # --- Handle 'age' ---
    # Valid range: 25–60.
    df = count_and_replace_invalid(
        df, 'age',
        lambda x: (x < 25) | (x > 60)
    )

    # --- Handle 'years_of_employment' ---
    # Values below 0 are invalid.
    df = count_and_replace_invalid(
        df, 'years_of_employment',
        lambda x: x < 0
    )

    # --- Handle 'family_size' ---
    # Values less than or equal to 0 are invalid.
    df = count_and_replace_invalid(
        df, 'family_size',
        lambda x: x <= 0
    )

    # --- Handle 'dependents' ---
    # Values below 0 are invalid.
    df = count_and_replace_invalid(
        df, 'dependents',
        lambda x: x < 0
    )

    # Values greater than family_size are invalid.
    if 'dependents' in df.columns and 'family_size' in df.columns:
        invalid_dependents_mask = (df['dependents'] > df['family_size']) & df['dependents'].notna() & df['family_size'].notna()
        df.loc[invalid_dependents_mask, 'dependents'] = np.nan

    # --- Handle 'credit_score' ---
    # Values below 300 or above 850 are invalid.
    if 'credit_score' in df.columns:
        # Just in case it's string, coercing it.
        df['credit_score'] = pd.to_numeric(df['credit_score'], errors='coerce')
        df = count_and_replace_invalid(
            df, 'credit_score',
            lambda x: (x < 300) | (x > 850)
        )

    # --- Handle Financial amount columns (negative values) ---
    # EXCLUDE target max_monthly_emi
    financial_amount_cols = [
        'monthly_salary', 'monthly_rent', 'school_fees', 'college_fees',
        'travel_expenses', 'groceries_utilities', 'other_monthly_expenses',
        'current_emi_amount', 'bank_balance', 'emergency_fund',
        'requested_amount'
    ]
    
    for col in financial_amount_cols:
        df = count_and_replace_invalid(
            df, col,
            lambda x: x < 0
        )

    # --- Handle 'requested_tenure' ---
    # Values less than or equal to 0 are invalid.
    df = count_and_replace_invalid(
        df, 'requested_tenure',
        lambda x: x <= 0
    )

    return df
