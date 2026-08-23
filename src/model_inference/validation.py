from typing import Dict, Any, List

# The exact 25 raw input features expected from the user
EXPECTED_RAW_FEATURES = [
    'age', 'gender', 'marital_status', 'education', 'monthly_salary',
    'employment_type', 'years_of_employment', 'company_type', 'house_type',
    'monthly_rent', 'family_size', 'dependents', 'school_fees', 'college_fees',
    'travel_expenses', 'groceries_utilities', 'other_monthly_expenses',
    'existing_loans', 'current_emi_amount', 'credit_score', 'bank_balance',
    'emergency_fund', 'emi_scenario', 'requested_amount', 'requested_tenure'
]

TARGET_FEATURES = ['emi_eligibility', 'max_monthly_emi']

def validate_raw_input(raw_data: Dict[str, Any]) -> None:
    """
    Validates that the raw input dictionary contains exactly the required features
    and does not contain the target columns.
    Raises ValueError if validation fails.
    """
    input_keys = set(raw_data.keys())
    expected_keys = set(EXPECTED_RAW_FEATURES)
    target_keys = set(TARGET_FEATURES)

    # Check for target leakage
    leaked_targets = input_keys.intersection(target_keys)
    if leaked_targets:
        raise ValueError(f"Target columns are not allowed in inference input: {leaked_targets}")

    # Check for missing required features
    missing_keys = expected_keys - input_keys
    if missing_keys:
        raise ValueError(f"Missing required input features: {missing_keys}")

    # Check for unexpected extra features (optional strictness, but good for safety)
    extra_keys = input_keys - expected_keys
    if extra_keys:
        raise ValueError(f"Unexpected extra input features found: {extra_keys}")

def validate_final_features(columns: List[str], expected_ordered_features: List[str]) -> None:
    """
    Validates that the final feature dataframe has exactly 49 features in the correct order.
    """
    if len(columns) != 49:
        raise ValueError(f"Expected exactly 49 final features, but got {len(columns)}.")
    
    if list(columns) != list(expected_ordered_features):
        raise ValueError("The ordering or names of the final features do not match the expected metadata.")

