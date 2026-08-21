import numpy as np
import pandas as pd

def compute_expense_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes total expenses, financial burden, and income after expenses."""
    df_out = df.copy()
    df_out['total_monthly_expenses'] = (
        df_out['monthly_rent']
        + df_out['school_fees']
        + df_out['college_fees']
        + df_out['travel_expenses']
        + df_out['groceries_utilities']
        + df_out['other_monthly_expenses']
    )
    
    df_out['total_financial_burden'] = (
        df_out['total_monthly_expenses']
        + df_out['current_emi_amount']
    )
    
    df_out['income_after_expenses'] = (
        df_out['monthly_salary']
        - df_out['total_financial_burden']
    )
    return df_out

def compute_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes EMI, expense, and financial burden ratios."""
    df_out = df.copy()
    
    df_out['emi_to_income_ratio'] = np.where(
        df_out['monthly_salary'] != 0,
        df_out['current_emi_amount'] / df_out['monthly_salary'],
        np.nan
    )
    
    df_out['expense_to_income_ratio'] = np.where(
        df_out['monthly_salary'] != 0,
        df_out['total_monthly_expenses'] / df_out['monthly_salary'],
        np.nan
    )
    
    df_out['financial_burden_ratio'] = np.where(
        df_out['monthly_salary'] != 0,
        df_out['total_financial_burden'] / df_out['monthly_salary'],
        np.nan
    )
    return df_out

def compute_coverage_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes emergency fund and bank balance coverage over expenses."""
    df_out = df.copy()
    
    df_out['emergency_fund_coverage'] = np.where(
        df_out['total_monthly_expenses'] != 0,
        df_out['emergency_fund'] / df_out['total_monthly_expenses'],
        np.nan
    )
    
    df_out['bank_balance_coverage'] = np.where(
        df_out['total_monthly_expenses'] != 0,
        df_out['bank_balance'] / df_out['total_monthly_expenses'],
        np.nan
    )
    return df_out

def compute_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes interactions like salary times credit score."""
    df_out = df.copy()
    df_out['salary_credit_interaction'] = df_out['monthly_salary'] * df_out['credit_score']
    return df_out
